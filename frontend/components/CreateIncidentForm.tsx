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
import { CATEGORY_LABELS, PRIORITY_LABELS } from "@/lib/labels";

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
      setError(
        "Tu rol es de solo lectura. Pide a un ADMIN o TECHNICIAN que cree los incidentes.",
      );
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
      setError(err instanceof Error ? err.message : "No se pudo crear el incidente");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto max-w-2xl space-y-5">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Nuevo incidente</p>
        <p className="mt-1 text-sm text-muted">
          Captura el título, el impacto y la clasificación. El análisis con IA está disponible en el
          detalle del ticket.
        </p>
      </div>

      <label className="block">
        <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Título</span>
        <input
          required
          maxLength={500}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          placeholder="p. ej. Pasarela VPN inalcanzable"
        />
      </label>

      <label className="block">
        <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Descripción</span>
        <textarea
          rows={5}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          placeholder="Qué ha pasado, a quién afecta y qué síntomas se observan…"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Categoría</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as IncidentCategory)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            {INCIDENT_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {CATEGORY_LABELS[c]}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Prioridad</span>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as IncidentPriority)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            {INCIDENT_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {PRIORITY_LABELS[p]}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Servicio afectado</span>
          <input
            value={service}
            onChange={(e) => setService(e.target.value)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2.5 text-sm outline-none ring-accent/40 focus:ring-2"
            placeholder="vpn-gw-01"
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Sistema afectado</span>
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
          {pending ? "Creando…" : "Crear incidente"}
        </button>
        <Link
          href="/incidents"
          className="rounded-md border border-white/15 px-4 py-2.5 text-sm transition hover:border-accent/40"
        >
          Cancelar
        </Link>
      </div>
    </form>
  );
}
