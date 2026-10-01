"""Deterministic MockAIProvider for local Docker without API keys."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.ai.provider import AIProvider
from app.ai.schemas import AnalysisClassification, IncidentAnalysisResult

_CATEGORY_HINTS = {
    "VPN": ("vpn", "tunnel", "anyconnect", "ipsec"),
    "DNS": ("dns", "resolver", "nxdomain"),
    "DATABASE": ("database", "postgres", "mysql", "sql", "db "),
    "NETWORK": ("network", "latency", "packet", "firewall", "switch"),
    "WINDOWS": ("windows", "wsus", "active directory", "ad ", "gpo"),
    "LINUX": ("linux", "systemd", "kernel", "ssh"),
    "SECURITY": ("security", "malware", "breach", "phishing", "auth fail"),
    "CLOUD": ("cloud", "aws", "azure", "gcp", "kubernetes", "k8s"),
    "HARDWARE": ("hardware", "disk", "raid", "nic", "memory"),
    "APPLICATION": ("application", "app ", "http 5", "timeout", "deploy"),
}


def _extract_block(prompt: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, prompt, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else prompt


def _guess_category(text: str, fallback: str) -> str:
    lowered = text.lower()
    for category, hints in _CATEGORY_HINTS.items():
        if any(h in lowered for h in hints):
            return category
    return fallback.upper() if fallback else "OTHER"


def _guess_severity(text: str, fallback: str) -> str:
    lowered = text.lower()
    if any(w in lowered for w in ("critical", "outage", "down", "unavailable", "p1")):
        return "CRITICAL"
    if any(w in lowered for w in ("high", "degraded", "major", "p2")):
        return "HIGH"
    if any(w in lowered for w in ("low", "minor", "cosmetic")):
        return "LOW"
    allowed = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    candidate = fallback.upper()
    return candidate if candidate in allowed else "MEDIUM"


class MockAIProvider(AIProvider):
    """
    Returns deterministic structured analysis derived only from the prompt context.
    Suitable for CI and local Compose without external keys.
    """

    name = "mock"

    def analyze_incident(self, prompt: str, **kwargs: Any) -> IncidentAnalysisResult:
        del kwargs  # unused — interface compatibility
        incident_block = _extract_block(prompt, "Incident context")
        similar_block = _extract_block(prompt, "Similar incidents (for reference only)")

        title = ""
        description = ""
        category = "OTHER"
        priority = "MEDIUM"
        severity = "MEDIUM"
        service = ""
        ticket = ""

        for line in incident_block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "ticket":
                ticket = value
            elif key == "title":
                title = value
            elif key == "description":
                description = value
            elif key == "category":
                category = value
            elif key == "priority":
                priority = value
            elif key == "severity":
                severity = value
            elif key == "affected service":
                service = value

        blob = f"{title} {description} {category} {service}".strip()
        resolved_category = _guess_category(blob, category)
        resolved_severity = _guess_severity(blob, severity or priority)
        resolved_priority = _guess_severity(blob, priority)

        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        # Stable confidence in 0.55–0.82 from content hash (not random inventing of facts)
        confidence = 0.55 + (int(digest[:2], 16) / 255.0) * 0.27

        symptoms: list[str] = []
        if title:
            symptoms.append(f"Reported issue: {title}")
        if description:
            # Keep factual — quote provided description, truncated
            snippet = description if len(description) <= 240 else description[:237] + "..."
            symptoms.append(f"Operator description: {snippet}")
        if service:
            symptoms.append(f"Affected service named in ticket: {service}")
        if not symptoms:
            symptoms.append("Insufficient detail in the ticket description.")

        similar_refs: list[str] = []
        if similar_block and "none provided" not in similar_block.lower():
            for line in similar_block.splitlines():
                line = line.strip().lstrip("-•").strip()
                if line and not line.lower().startswith("none"):
                    similar_refs.append(line)
                    if len(similar_refs) >= 5:
                        break

        evidence: list[str] = [
            f"Ticket fields provided for {ticket or 'this incident'} (category={category}, "
            f"priority={priority}, severity={severity})."
        ]
        if similar_refs:
            evidence.append(
                f"{len(similar_refs)} similar historical ticket(s) matched by category/service/keywords."
            )
        else:
            evidence.append("No strongly matching historical tickets were supplied in context.")

        possible_causes = [
            f"Hypothesis: fault related to {resolved_category.lower()} based on category/keywords in the ticket "
            "(not confirmed by telemetry — OpsAI has no live execution data).",
            "Hypothesis: recent change or capacity issue affecting the named service/system "
            "(verify change calendar and monitoring before acting).",
        ]

        recommended_steps = [
            "Confirm the symptom with the reporter and note exact error messages / timestamps (read-only).",
            "Check existing monitoring/dashboards and recent alerts for the affected service — do not restart anything yet.",
            "Review recent changes (deployments, firewall, DNS, certs) in the change window overlapping the start time.",
            "If impact is confirmed, escalate per runbook and document findings in the ticket.",
        ]

        warnings = [
            "OpsAI assistance only: this analysis does not execute commands or change production systems.",
            "Do not perform destructive remediation (reboot, wipe, drop, force failover) without change approval.",
        ]
        if confidence < 0.65:
            warnings.append("Low-to-moderate confidence — treat causes as hypotheses until verified.")

        summary = (
            f"Assistance-only diagnosis for {ticket or 'incident'}: "
            f"'{title or 'untitled'}' classified as {resolved_category} "
            f"({resolved_severity} severity). "
            "Findings are based solely on ticket text and similar incidents supplied in context."
        )

        next_best = (
            "Gather confirming evidence from monitoring and the reporter before any remediation; "
            "start with read-only checks listed in recommended_steps."
        )

        return IncidentAnalysisResult(
            summary=summary,
            classification=AnalysisClassification(
                category=resolved_category,
                severity=resolved_severity,
                priority=resolved_priority,
            ),
            symptoms=symptoms,
            possible_causes=possible_causes,
            evidence=evidence,
            recommended_steps=recommended_steps,
            similar_incidents=similar_refs,
            confidence=round(confidence, 3),
            next_best_action=next_best,
            warnings=warnings,
        )
