"""Pytest suite for OpsAI AI diagnosis (Phase 4)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.ai import MockAIProvider, get_ai_provider
from app.ai.schemas import IncidentAnalysisResult
from app.services.diagnosis import build_analysis_prompt


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


def _create_incident(client: TestClient, token: str, **overrides: object) -> dict:
    body = {
        "title": "VPN gateway unreachable",
        "description": "Users cannot connect to corporate VPN tunnel",
        "category": "VPN",
        "priority": "HIGH",
        "affected_service": "vpn-gw-01",
        "affected_system": "edge",
    }
    body.update(overrides)
    res = client.post("/api/v1/incidents", headers=_auth(token), json=body)
    assert res.status_code == 201, res.text
    return res.json()


def test_mock_provider_returns_valid_schema() -> None:
    provider = MockAIProvider()
    prompt = """## Safety rules (mandatory)
...
## Incident context
Ticket: INC-0001
Title: VPN gateway unreachable
Description: Users cannot connect
Status: NEW
Category: VPN
Priority: HIGH
Severity: HIGH
Affected service: vpn-gw-01
Affected system: edge

## Similar incidents (for reference only)
- INC-0000: Prior VPN flap [category=VPN, status=RESOLVED, service=vpn-gw-01]
"""
    result = provider.analyze_incident(prompt)
    assert isinstance(result, IncidentAnalysisResult)
    assert result.summary
    assert result.classification.category == "VPN"
    assert 0.0 <= result.confidence <= 1.0
    assert result.next_best_action
    assert result.symptoms
    assert result.recommended_steps
    assert any("asistencia" in w.lower() or "opsai" in w.lower() for w in result.warnings)
    # Deterministic for same prompt
    again = provider.analyze_incident(prompt)
    assert again.confidence == result.confidence
    assert again.summary == result.summary


def test_analysis_schema_rejects_invalid() -> None:
    with pytest.raises(ValidationError):
        IncidentAnalysisResult.model_validate(
            {
                "summary": "x",
                "classification": {"category": "VPN", "severity": "HIGH", "priority": "HIGH"},
                "symptoms": [],
                "possible_causes": [],
                "evidence": [],
                "recommended_steps": [],
                "similar_incidents": [],
                "confidence": 2.5,
                "next_best_action": "check",
                "warnings": [],
            }
        )


def test_get_ai_provider_mock_default() -> None:
    get_ai_provider.cache_clear()
    with patch("app.ai.settings") as mock_settings:
        mock_settings.ai_provider = "mock"
        provider = get_ai_provider()
        assert provider.name == "mock"
    get_ai_provider.cache_clear()


def test_analyze_endpoint_technician(client: TestClient) -> None:
    get_ai_provider.cache_clear()
    token = _register_and_login(
        client, email="tech-ai@example.com", name="Tech", role="TECHNICIAN"
    )
    incident = _create_incident(client, token)
    incident_id = incident["id"]

    analyze = client.post(
        f"/api/v1/incidents/{incident_id}/analyze", headers=_auth(token)
    )
    assert analyze.status_code == 201, analyze.text
    body = analyze.json()
    assert body["provider"] == "mock"
    assert body["incident_id"] == incident_id
    analysis = body["analysis"]
    assert analysis["summary"]
    assert "classification" in analysis
    assert isinstance(analysis["symptoms"], list)
    assert isinstance(analysis["possible_causes"], list)
    assert isinstance(analysis["recommended_steps"], list)
    assert analysis["next_best_action"]
    assert 0 <= analysis["confidence"] <= 1
    assert isinstance(analysis["warnings"], list)

    latest = client.get(
        f"/api/v1/incidents/{incident_id}/analysis", headers=_auth(token)
    )
    assert latest.status_code == 200
    assert latest.json()["id"] == body["id"]

    detail = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(token))
    assert detail.status_code == 200
    assert detail.json()["latest_analysis"]["id"] == body["id"]
    types = [e["type"] for e in detail.json()["timeline"]]
    assert "analyzed" in types


def test_analyze_endpoint_admin(client: TestClient) -> None:
    get_ai_provider.cache_clear()
    token = _register_and_login(
        client, email="admin-ai@example.com", name="Admin", role="ADMIN"
    )
    incident = _create_incident(client, token, title="DNS timeouts", category="DNS")
    analyze = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze", headers=_auth(token)
    )
    assert analyze.status_code == 201, analyze.text


def test_analyze_forbidden_for_viewer(client: TestClient) -> None:
    get_ai_provider.cache_clear()
    admin = _register_and_login(
        client, email="boss-ai@example.com", name="Boss", role="ADMIN"
    )
    incident = _create_incident(client, admin)
    viewer = _register_and_login(client, email="viewer-ai@example.com", name="Viewer")

    forbidden = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze", headers=_auth(viewer)
    )
    assert forbidden.status_code == 403

    # Viewer can still read analysis if one exists
    created = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze", headers=_auth(admin)
    )
    assert created.status_code == 201
    readable = client.get(
        f"/api/v1/incidents/{incident['id']}/analysis", headers=_auth(viewer)
    )
    assert readable.status_code == 200


def test_analysis_missing_returns_404(client: TestClient) -> None:
    token = _register_and_login(
        client, email="empty-ai@example.com", name="Empty", role="ADMIN"
    )
    incident = _create_incident(client, token, title="No analysis yet")
    missing = client.get(
        f"/api/v1/incidents/{incident['id']}/analysis", headers=_auth(token)
    )
    assert missing.status_code == 404


def test_invalid_ai_output_mapped_to_client_error(client: TestClient) -> None:
    get_ai_provider.cache_clear()
    token = _register_and_login(
        client, email="bad-ai@example.com", name="Bad", role="ADMIN"
    )
    incident = _create_incident(client, token)

    class BrokenProvider:
        name = "broken"

        def analyze_incident(self, prompt: str, **kwargs):  # noqa: ANN001, ANN003
            del prompt, kwargs
            return IncidentAnalysisResult.model_validate(
                {
                    "summary": "ok",
                    "classification": {
                        "category": "OTHER",
                        "severity": "LOW",
                        "priority": "LOW",
                    },
                    "symptoms": [],
                    "possible_causes": [],
                    "evidence": [],
                    "recommended_steps": [],
                    "similar_incidents": [],
                    "confidence": 0.1,
                    "next_best_action": "wait",
                    "warnings": [],
                }
            )

    # Force ValidationError path via provider raising AIProviderError-like validation
    from app.ai.openai_provider import AIProviderError

    class InvalidProvider:
        name = "invalid"

        def analyze_incident(self, prompt: str, **kwargs):  # noqa: ANN001, ANN003
            del prompt, kwargs
            raise AIProviderError(
                "La salida de la IA no superó la validación del esquema", status_code=422
            )

    with patch("app.services.diagnosis.get_ai_provider", return_value=InvalidProvider()):
        res = client.post(
            f"/api/v1/incidents/{incident['id']}/analyze", headers=_auth(token)
        )
    assert res.status_code == 422
    assert "validación" in res.json()["detail"].lower() or "validacion" in res.json()["detail"].lower()
    # No stack dump fields
    assert "traceback" not in res.text.lower()


def test_build_prompt_includes_safety_and_context() -> None:
    class FakeIncident:
        ticket_number = "INC-0009"
        title = "Disk full"
        description = "Root partition at 98%"
        status = type("S", (), {"value": "NEW"})()
        category = type("C", (), {"value": "LINUX"})()
        priority = type("P", (), {"value": "HIGH"})()
        severity = type("V", (), {"value": "HIGH"})()
        affected_service = "app-node"
        affected_system = "vm-12"

    prompt = build_analysis_prompt(FakeIncident(), [])  # type: ignore[arg-type]
    assert "no inventes" in prompt.lower() or "únicamente" in prompt.lower() or "unicamente" in prompt.lower()
    assert "INC-0009" in prompt
    assert "Disk full" in prompt
    assert "Ninguno" in prompt
