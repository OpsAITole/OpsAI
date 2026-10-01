"""Pytest suite for OpsAI incidents CRUD and RBAC."""

from fastapi.testclient import TestClient


def _register_and_login(
    client: TestClient,
    *,
    email: str,
    name: str,
    role: str | None = None,
    password: str = "password123",
) -> str:
    payload: dict = {"email": email, "password": password, "name": name}
    if role is not None:
        payload["role"] = role
    reg = client.post("/api/v1/auth/register", json=payload)
    assert reg.status_code == 201, reg.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_incident_crud_flow(client: TestClient) -> None:
    token = _register_and_login(
        client, email="admin@example.com", name="Admin", role="ADMIN"
    )

    create = client.post(
        "/api/v1/incidents",
        headers=_auth(token),
        json={
            "title": "VPN gateway down",
            "description": "Users cannot connect to corporate VPN",
            "category": "VPN",
            "priority": "HIGH",
            "affected_service": "vpn-gw-01",
            "affected_system": "edge",
        },
    )
    assert create.status_code == 201, create.text
    incident = create.json()
    assert incident["ticket_number"] == "INC-0001"
    assert incident["status"] == "NEW"
    assert incident["priority"] == "HIGH"
    assert incident["severity"] == "HIGH"
    assert incident["category"] == "VPN"
    assert incident["affected_service"] == "vpn-gw-01"
    assert incident["created_by"]
    incident_id = incident["id"]

    listed = client.get("/api/v1/incidents", headers=_auth(token))
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["ticket_number"] == "INC-0001"

    detail = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(token))
    assert detail.status_code == 200
    body = detail.json()
    assert body["title"] == "VPN gateway down"
    assert len(body["timeline"]) >= 1
    assert body["timeline"][0]["type"] == "created"

    updated = client.put(
        f"/api/v1/incidents/{incident_id}",
        headers=_auth(token),
        json={"status": "INVESTIGATING", "priority": "CRITICAL"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "INVESTIGATING"
    assert updated.json()["priority"] == "CRITICAL"
    assert updated.json()["resolved_at"] is None

    resolved = client.put(
        f"/api/v1/incidents/{incident_id}",
        headers=_auth(token),
        json={"status": "RESOLVED"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "RESOLVED"
    assert resolved.json()["resolved_at"] is not None

    second = client.post(
        "/api/v1/incidents",
        headers=_auth(token),
        json={"title": "DNS latency", "category": "DNS", "priority": "MEDIUM"},
    )
    assert second.status_code == 201
    assert second.json()["ticket_number"] == "INC-0002"

    filtered = client.get(
        "/api/v1/incidents",
        headers=_auth(token),
        params={"category": "DNS", "search": "latency"},
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["ticket_number"] == "INC-0002"

    deleted = client.delete(f"/api/v1/incidents/{incident_id}", headers=_auth(token))
    assert deleted.status_code == 200
    missing = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(token))
    assert missing.status_code == 404


def test_viewer_read_only(client: TestClient) -> None:
    admin_token = _register_and_login(
        client, email="boss@example.com", name="Boss", role="ADMIN"
    )
    created = client.post(
        "/api/v1/incidents",
        headers=_auth(admin_token),
        json={"title": "Disk full", "category": "LINUX", "priority": "MEDIUM"},
    )
    assert created.status_code == 201
    incident_id = created.json()["id"]

    viewer_token = _register_and_login(
        client, email="viewer@example.com", name="Viewer"
    )

    listed = client.get("/api/v1/incidents", headers=_auth(viewer_token))
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    detail = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(viewer_token))
    assert detail.status_code == 200

    forbidden_create = client.post(
        "/api/v1/incidents",
        headers=_auth(viewer_token),
        json={"title": "Should fail", "category": "OTHER", "priority": "LOW"},
    )
    assert forbidden_create.status_code == 403

    forbidden_update = client.put(
        f"/api/v1/incidents/{incident_id}",
        headers=_auth(viewer_token),
        json={"status": "CLOSED"},
    )
    assert forbidden_update.status_code == 403

    forbidden_delete = client.delete(
        f"/api/v1/incidents/{incident_id}", headers=_auth(viewer_token)
    )
    assert forbidden_delete.status_code == 403


def test_technician_bootstrap_crud(client: TestClient) -> None:
    token = _register_and_login(
        client, email="tech@example.com", name="Tech", role="TECHNICIAN"
    )
    me = client.get("/api/v1/auth/me", headers=_auth(token))
    assert me.json()["role"] == "TECHNICIAN"

    created = client.post(
        "/api/v1/incidents",
        headers=_auth(token),
        json={
            "title": "Windows update stuck",
            "description": "WSUS clients hanging",
            "category": "WINDOWS",
            "priority": "LOW",
            "affected_service": "wsus",
            "affected_system": "corp-pc",
        },
    )
    assert created.status_code == 201, created.text
    incident_id = created.json()["id"]

    updated = client.put(
        f"/api/v1/incidents/{incident_id}",
        headers=_auth(token),
        json={"status": "WAITING"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "WAITING"


def test_analyze_endpoint_is_live(client: TestClient) -> None:
    from app.ai import get_ai_provider

    get_ai_provider.cache_clear()
    token = _register_and_login(
        client, email="admin2@example.com", name="Admin2", role="ADMIN"
    )
    created = client.post(
        "/api/v1/incidents",
        headers=_auth(token),
        json={"title": "Analyze me", "category": "APPLICATION", "priority": "MEDIUM"},
    )
    incident_id = created.json()["id"]
    analyze = client.post(
        f"/api/v1/incidents/{incident_id}/analyze", headers=_auth(token)
    )
    assert analyze.status_code == 201, analyze.text
    assert analyze.json()["analysis"]["summary"]


def test_sort_and_priority_filter(client: TestClient) -> None:
    token = _register_and_login(
        client, email="sorter@example.com", name="Sorter", role="ADMIN"
    )
    for title, priority in [("Low issue", "LOW"), ("Crit issue", "CRITICAL")]:
        res = client.post(
            "/api/v1/incidents",
            headers=_auth(token),
            json={"title": title, "category": "OTHER", "priority": priority},
        )
        assert res.status_code == 201

    crit = client.get(
        "/api/v1/incidents",
        headers=_auth(token),
        params={"priority": "CRITICAL"},
    )
    assert crit.status_code == 200
    assert crit.json()["total"] == 1
    assert crit.json()["items"][0]["title"] == "Crit issue"

    asc = client.get(
        "/api/v1/incidents",
        headers=_auth(token),
        params={"sort_by": "title", "sort_dir": "asc"},
    )
    titles = [i["title"] for i in asc.json()["items"]]
    assert titles == sorted(titles)
