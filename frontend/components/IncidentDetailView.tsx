"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { PriorityBadge, StatusBadge } from "@/components/IncidentBadges";
import {
  analyzeIncident,
  canWriteIncidents,
  deleteIncident,
  getIncident,
  getStoredUser,
  INCIDENT_STATUSES,
  updateIncident,
  type IncidentAnalysis,
  type IncidentAnalysisResult,
  type IncidentDetail,
  type IncidentStatus,
  type User,
} from "@/lib/api";
import {
  categoryLabel,
  formatDateEs,
  priorityLabel,
  severityLabel,
  STATUS_LABELS,
} from "@/lib/labels";

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function DiagnosisPanel({
  analysis,
  provider,
  createdAt,
}: {
  analysis: IncidentAnalysisResult;
  provider: string;
  createdAt: string;
}) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Diagnóstico</h3>
        <p className="font-mono text-[11px] text-muted">
          {provider} · {formatDateEs(createdAt)} · confianza {formatConfidence(analysis.confidence)}
        </p>
      </div>

      <p className="text-sm leading-relaxed text-foreground/90">{analysis.summary}</p>

      <div className="flex flex-wrap gap-3 font-mono text-[11px] uppercase tracking-[0.12em] text-muted">
        <span>Categoría {categoryLabel(analysis.classification.category)}</span>
        <span>Severidad {severityLabel(analysis.classification.severity)}</span>
        <span>Prioridad {priorityLabel(analysis.classification.priority)}</span>
      </div>

      <div className="rounded-lg border border-accent/30 bg-accent/5 px-4 py-3">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent">
          Próxima mejor acción
        </p>
        <p className="mt-1 text-sm text-foreground">{analysis.next_best_action}</p>
      </div>

      {analysis.warnings.length > 0 ? (
        <div className="rounded-lg border border-danger/30 bg-danger/5 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-danger">Avisos</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-foreground/90">
            {analysis.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <DiagnosisList title="Síntomas" items={analysis.symptoms} />
      <DiagnosisList title="Posibles causas" items={analysis.possible_causes} />
      <DiagnosisList title="Evidencia" items={analysis.evidence} />
      <DiagnosisList title="Pasos recomendados" items={analysis.recommended_steps} />
      {analysis.similar_incidents.length > 0 ? (
        <DiagnosisList title="Incidentes similares" items={analysis.similar_incidents} />
      ) : null}
    </div>
  );
}

function DiagnosisList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">{title}</p>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-foreground/90">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function IncidentDetailView({ incidentId }: { incidentId: string }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusDraft, setStatusDraft] = useState<IncidentStatus>("NEW");
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<IncidentAnalysis | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getIncident(incidentId);
        if (!cancelled) {
          setIncident(data);
          setStatusDraft(data.status);
          setAnalysis(data.latest_analysis ?? null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Incidente no encontrado");
          setIncident(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [incidentId]);

  const writable = canWriteIncidents(user);

  async function onStatusSave() {
    if (!incident || !writable) return;
    setSaving(true);
    setActionError(null);
    try {
      const updated = await updateIncident(incident.id, { status: statusDraft });
      const refreshed = await getIncident(incident.id);
      setIncident(refreshed);
      setStatusDraft(updated.status);
      setAnalysis(refreshed.latest_analysis ?? null);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Error al actualizar");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete() {
    if (!incident || !writable) return;
    if (!window.confirm(`¿Eliminar ${incident.ticket_number}? Esta acción no se puede deshacer.`))
      return;
    setSaving(true);
    setActionError(null);
    try {
      await deleteIncident(incident.id);
      router.push("/incidents");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Error al eliminar");
      setSaving(false);
    }
  }

  async function onAnalyze() {
    if (!incident || !writable) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const result = await analyzeIncident(incident.id);
      setAnalysis(result);
      const refreshed = await getIncident(incident.id);
      setIncident(refreshed);
    } catch (err) {
      setAnalyzeError(
        err instanceof Error
          ? err.message
          : "El análisis con IA ha fallado. Revisa la configuración del proveedor e inténtalo de nuevo.",
      );
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-muted">Cargando incidente…</p>;
  }

  if (error || !incident) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-danger">{error ?? "Incidente no encontrado"}</p>
        <Link href="/incidents" className="text-sm text-accent hover:underline">
          Volver a incidentes
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/incidents" className="text-xs text-muted hover:text-accent">
            ← Incidentes
          </Link>
          <p className="mt-3 font-mono text-xs uppercase tracking-[0.18em] text-accent">
            {incident.ticket_number}
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-foreground">
            {incident.title}
          </h2>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <StatusBadge status={incident.status} />
            <PriorityBadge priority={incident.priority} />
            <span className="font-mono text-xs text-muted">{categoryLabel(incident.category)}</span>
          </div>
        </div>
      </div>

      <section className="space-y-3">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Descripción</h3>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
          {incident.description?.trim() || "Sin descripción."}
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Servicio</p>
          <p className="mt-1 text-sm">{incident.affected_service || "—"}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Sistema</p>
          <p className="mt-1 text-sm">{incident.affected_system || "—"}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Severidad</p>
          <p className="mt-1 text-sm">{severityLabel(incident.severity)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Creado</p>
          <p className="mt-1 text-sm">{formatDateEs(incident.created_at)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Actualizado</p>
          <p className="mt-1 text-sm">{formatDateEs(incident.updated_at)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Resuelto</p>
          <p className="mt-1 text-sm">{formatDateEs(incident.resolved_at)}</p>
        </div>
      </section>

      <section className="space-y-4 rounded-lg border border-white/10 bg-surface/30 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
              Asistencia IA
            </h3>
            <p className="mt-1 text-xs text-muted">
              Solo sugerencias — OpsAI nunca ejecuta cambios en producción.
            </p>
          </div>
          {writable ? (
            <button
              type="button"
              disabled={analyzing}
              onClick={() => void onAnalyze()}
              className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-background disabled:opacity-60"
            >
              {analyzing ? "Analizando…" : "Analizar con IA"}
            </button>
          ) : (
            <p className="text-xs text-muted">
              Se requiere rol TECHNICIAN o ADMIN para lanzar el análisis.
            </p>
          )}
        </div>
        {analyzing ? (
          <p className="text-sm text-muted" data-testid="analyze-loading">
            Ejecutando diagnóstico con el proveedor de IA configurado…
          </p>
        ) : null}
        {analyzeError ? <p className="text-sm text-danger">{analyzeError}</p> : null}
        {analysis ? (
          <DiagnosisPanel
            analysis={analysis.analysis}
            provider={analysis.provider}
            createdAt={analysis.created_at}
          />
        ) : !analyzing ? (
          <p className="text-sm text-muted">Aún no hay un diagnóstico guardado para este incidente.</p>
        ) : null}
      </section>

      {writable ? (
        <section className="space-y-3 rounded-lg border border-white/10 bg-surface/30 p-4">
          <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
            Actualizar estado
          </h3>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={statusDraft}
              onChange={(e) => setStatusDraft(e.target.value as IncidentStatus)}
              className="rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
            >
              {INCIDENT_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {STATUS_LABELS[s]}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={saving || statusDraft === incident.status}
              onClick={() => void onStatusSave()}
              className="rounded-md bg-accent px-3 py-2 text-sm font-semibold text-background disabled:opacity-50"
            >
              {saving ? "Guardando…" : "Guardar"}
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={() => void onDelete()}
              className="rounded-md border border-danger/40 px-3 py-2 text-sm text-danger transition hover:bg-danger/10"
            >
              Eliminar
            </button>
          </div>
          {actionError ? <p className="text-sm text-danger">{actionError}</p> : null}
        </section>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Cronología</h3>
        <ol className="space-y-3 border-l border-white/10 pl-4">
          {incident.timeline.map((event) => (
            <li key={event.id} className="relative">
              <span className="absolute -left-[1.35rem] top-1.5 h-2 w-2 rounded-full bg-accent" />
              <p className="text-sm text-foreground">{event.message}</p>
              <p className="mt-0.5 font-mono text-[11px] text-muted">
                {event.type} · {formatDateEs(event.at)}
              </p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
