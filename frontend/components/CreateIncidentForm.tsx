"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import {
  canWriteIncidents,
  createIncident,
  getStoredUser,
  INCIDENT_CATEGORIES,
  INCIDENT_PRIORITIES,
  type IncidentCategory,
  type IncidentPriority,
} from "@/lib/api";

export function CreateIncidentForm() {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<IncidentCategory>("OTHER");
  const [priority, setPriority] = useState<IncidentPriority>("MEDIUM");
  const [service, setService] = useState("");
  const [system, setSystem] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    if (!canWriteIncidents(user)) {
      setError("Your role is read-only. Ask an ADMIN or TECHNICIAN to create incidents.");
      setAllowed(false);
      return;
    }
    setAllowed(true);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!allowed) return;
    setPending(true);
    setError(null);
    try {
      const incident = await createIncident({
        title: title.trim(),
        description,
        category,
        priority,
        affected_service: service.trim() || null,
        affected_system: system.trim() || null,
      });
      router.push(`/incidents/${incident.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create incident");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto max-w-2xl space-y-5">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">New incident</p>
        <p className="mt-1 text-sm text-muted">
          Capture title, impact, and classification. AI analysis comes in a later phase.
        </p>
      </div>

      <label className="block">
        <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Title</span>
        <input
          required
          maxLength={500}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          placeholder="e.g. VPN gateway unreachable"
        />
      </label>

      <label className="block">
        <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Description</span>
        <textarea
          rows={5}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          placeholder="What happened, who is affected, and any symptoms observed…"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Category</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as IncidentCategory)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            {INCIDENT_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Priority</span>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as IncidentPriority)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            {INCIDENT_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Affected service</span>
          <input
            value={service}
            onChange={(e) => setService(e.target.value)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
            placeholder="vpn-gw-01"
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Affected system</span>
          <input
            value={system}
            onChange={(e) => setSystem(e.target.value)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
            placeholder="edge / prod / eu-west"
          />
        </label>
      </div>

      {error ? <p className="text-sm text-danger">{error}</p> : null}

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={pending || !allowed}
          className="rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-background transition hover:brightness-110 disabled:opacity-60"
        >
          {pending ? "Creating…" : "Create incident"}
        </button>
        <Link
          href="/incidents"
          className="rounded-md border border-white/15 px-4 py-2.5 text-sm transition hover:border-accent/40"
        >
          Cancel
        </Link>
      </div>
    </form>
  );
}
