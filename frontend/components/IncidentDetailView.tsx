"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { PriorityBadge, StatusBadge } from "@/components/IncidentBadges";
import {
  canWriteIncidents,
  deleteIncident,
  getIncident,
  getStoredUser,
  INCIDENT_STATUSES,
  updateIncident,
  type IncidentDetail,
  type IncidentStatus,
  type User,
} from "@/lib/api";

function formatDate(value: string | null): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
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
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Incident not found");
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
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Update failed");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete() {
    if (!incident || !writable) return;
    if (!window.confirm(`Delete ${incident.ticket_number}? This cannot be undone.`)) return;
    setSaving(true);
    setActionError(null);
    try {
      await deleteIncident(incident.id);
      router.push("/incidents");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Delete failed");
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-muted">Loading incident…</p>;
  }

  if (error || !incident) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-danger">{error ?? "Incident not found"}</p>
        <Link href="/incidents" className="text-sm text-accent hover:underline">
          Back to incidents
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/incidents" className="text-xs text-muted hover:text-accent">
            ← Incidents
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
            <span className="font-mono text-xs text-muted">{incident.category}</span>
          </div>
        </div>
      </div>

      <section className="space-y-3">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Description</h3>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
          {incident.description?.trim() || "No description provided."}
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Service</p>
          <p className="mt-1 text-sm">{incident.affected_service || "—"}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">System</p>
          <p className="mt-1 text-sm">{incident.affected_system || "—"}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Severity</p>
          <p className="mt-1 text-sm">{incident.severity}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Created</p>
          <p className="mt-1 text-sm">{formatDate(incident.created_at)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Updated</p>
          <p className="mt-1 text-sm">{formatDate(incident.updated_at)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface/40 px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Resolved</p>
          <p className="mt-1 text-sm">{formatDate(incident.resolved_at)}</p>
        </div>
      </section>

      {writable ? (
        <section className="space-y-3 rounded-lg border border-white/10 bg-surface/30 p-4">
          <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Update status</h3>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={statusDraft}
              onChange={(e) => setStatusDraft(e.target.value as IncidentStatus)}
              className="rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
            >
              {INCIDENT_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={saving || statusDraft === incident.status}
              onClick={() => void onStatusSave()}
              className="rounded-md bg-accent px-3 py-2 text-sm font-semibold text-background disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={() => void onDelete()}
              className="rounded-md border border-danger/40 px-3 py-2 text-sm text-danger transition hover:bg-danger/10"
            >
              Delete
            </button>
          </div>
          {actionError ? <p className="text-sm text-danger">{actionError}</p> : null}
        </section>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">Timeline</h3>
        <p className="text-xs text-muted">
          Minimal create/update events for Phase 3. Full AI timeline arrives later.
        </p>
        <ol className="space-y-3 border-l border-white/10 pl-4">
          {incident.timeline.map((event) => (
            <li key={event.id} className="relative">
              <span className="absolute -left-[1.35rem] top-1.5 h-2 w-2 rounded-full bg-accent" />
              <p className="text-sm text-foreground">{event.message}</p>
              <p className="mt-0.5 font-mono text-[11px] text-muted">
                {event.type} · {formatDate(event.at)}
              </p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
