"""Deterministic MockAIProvider for local Docker without API keys."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.ai.provider import AIProvider
from app.ai.schemas import AnalysisClassification, IncidentAnalysisResult

_CATEGORY_HINTS = {
    "VPN": ("vpn", "tunnel", "túnel", "anyconnect", "ipsec"),
    "DNS": ("dns", "resolver", "nxdomain"),
    "DATABASE": ("database", "base de datos", "postgres", "mysql", "sql", "db "),
    "NETWORK": ("network", "red", "latency", "latencia", "packet", "firewall", "switch"),
    "WINDOWS": ("windows", "wsus", "active directory", "ad ", "gpo"),
    "LINUX": ("linux", "systemd", "kernel", "ssh"),
    "SECURITY": ("security", "seguridad", "malware", "breach", "phishing", "auth fail"),
    "CLOUD": ("cloud", "nube", "aws", "azure", "gcp", "kubernetes", "k8s"),
    "HARDWARE": ("hardware", "disk", "disco", "raid", "nic", "memory", "memoria"),
    "APPLICATION": ("application", "aplicación", "app ", "http 5", "timeout", "deploy"),
}


def _extract_block(prompt: str, *headings: str) -> str:
    for heading in headings:
        pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, prompt, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return prompt


def _guess_category(text: str, fallback: str) -> str:
    lowered = text.lower()
    for category, hints in _CATEGORY_HINTS.items():
        if any(h in lowered for h in hints):
            return category
    return fallback.upper() if fallback else "OTHER"


def _guess_severity(text: str, fallback: str) -> str:
    lowered = text.lower()
    if any(
        w in lowered
        for w in ("critical", "crítica", "critica", "outage", "caída", "caida", "down", "unavailable", "indisponible", "p1")
    ):
        return "CRITICAL"
    if any(w in lowered for w in ("high", "alta", "degraded", "degradado", "major", "grave", "p2")):
        return "HIGH"
    if any(w in lowered for w in ("low", "baja", "minor", "menor", "cosmetic", "cosmético")):
        return "LOW"
    allowed = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    candidate = fallback.upper()
    return candidate if candidate in allowed else "MEDIUM"


_FIELD_ALIASES = {
    "ticket": "ticket",
    "title": "title",
    "título": "title",
    "titulo": "title",
    "description": "description",
    "descripción": "description",
    "descripcion": "description",
    "category": "category",
    "categoría": "category",
    "categoria": "category",
    "priority": "priority",
    "prioridad": "priority",
    "severity": "severity",
    "severidad": "severity",
    "affected service": "service",
    "servicio afectado": "service",
    "affected system": "system",
    "sistema afectado": "system",
    "status": "status",
    "estado": "status",
}


class MockAIProvider(AIProvider):
    """
    Returns deterministic structured analysis derived only from the prompt context.
    Suitable for CI and local Compose without external keys.
    """

    name = "mock"

    def analyze_incident(self, prompt: str, **kwargs: Any) -> IncidentAnalysisResult:
        del kwargs  # unused — interface compatibility
        incident_block = _extract_block(
            prompt, "Contexto del incidente", "Incident context"
        )
        similar_block = _extract_block(
            prompt,
            "Incidentes similares (solo referencia)",
            "Similar incidents (for reference only)",
        )

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
            mapped = _FIELD_ALIASES.get(key)
            if mapped == "ticket":
                ticket = value
            elif mapped == "title":
                title = value
            elif mapped == "description":
                description = value
            elif mapped == "category":
                category = value
            elif mapped == "priority":
                priority = value
            elif mapped == "severity":
                severity = value
            elif mapped == "service":
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
            symptoms.append(f"Incidencia reportada: {title}")
        if description:
            # Keep factual — quote provided description, truncated
            snippet = description if len(description) <= 240 else description[:237] + "..."
            symptoms.append(f"Descripción del operador: {snippet}")
        if service:
            symptoms.append(f"Servicio afectado indicado en el ticket: {service}")
        if not symptoms:
            symptoms.append("Detalle insuficiente en la descripción del ticket.")

        similar_refs: list[str] = []
        none_markers = ("none provided", "ninguno", "ninguna")
        if similar_block and not any(m in similar_block.lower() for m in none_markers):
            for line in similar_block.splitlines():
                line = line.strip().lstrip("-•").strip()
                if line and not line.lower().startswith(("none", "ninguno", "ninguna")):
                    similar_refs.append(line)
                    if len(similar_refs) >= 5:
                        break

        evidence: list[str] = [
            f"Campos del ticket facilitados para {ticket or 'este incidente'} "
            f"(categoría={category}, prioridad={priority}, severidad={severity})."
        ]
        if similar_refs:
            evidence.append(
                f"{len(similar_refs)} ticket(s) histórico(s) similares coinciden por categoría/servicio/palabras clave."
            )
        else:
            evidence.append(
                "No se han facilitado tickets históricos con coincidencia fuerte en el contexto."
            )

        possible_causes = [
            f"Hipótesis: fallo relacionado con {resolved_category.lower()} según la categoría/palabras clave del ticket "
            "(no confirmado por telemetría — OpsAI no dispone de datos de ejecución en vivo).",
            "Hipótesis: cambio reciente o problema de capacidad que afecta al servicio/sistema indicado "
            "(verifica el calendario de cambios y la monitorización antes de actuar).",
        ]

        recommended_steps = [
            "Confirma el síntoma con quien lo reportó y anota mensajes de error / marcas de tiempo exactas (solo lectura).",
            "Revisa la monitorización/dashboards y alertas recientes del servicio afectado — no reinicies nada todavía.",
            "Revisa cambios recientes (despliegues, firewall, DNS, certificados) en la ventana que solape con el inicio.",
            "Si el impacto está confirmado, escala según el runbook y documenta los hallazgos en el ticket.",
        ]

        warnings = [
            "OpsAI solo asiste: este análisis no ejecuta comandos ni modifica sistemas de producción.",
            "No realices remediación destructiva (reinicio, wipe, drop, failover forzado) sin aprobación de cambio.",
        ]
        if confidence < 0.65:
            warnings.append(
                "Confianza baja o moderada — trata las causas como hipótesis hasta verificarlas."
            )

        summary = (
            f"Diagnóstico solo de asistencia para {ticket or 'el incidente'}: "
            f"«{title or 'sin título'}» clasificado como {resolved_category} "
            f"(severidad {resolved_severity}). "
            "Los hallazgos se basan únicamente en el texto del ticket y en los incidentes similares del contexto."
        )

        next_best = (
            "Reúne evidencia de confirmación en monitorización y con quien reportó el incidente antes de cualquier remediación; "
            "empieza por las comprobaciones de solo lectura de los pasos recomendados."
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
