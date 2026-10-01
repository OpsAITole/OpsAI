"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { ApiStatus } from "@/components/ApiStatus";
import { PriorityBadge, StatusBadge } from "@/components/IncidentBadges";
import { listIncidents, type Incident } from "@/lib/api";

export default function DashboardPage() {
  const [recent, setRecent] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await listIncidents({ sort_by: "created_at", sort_dir: "desc", limit: 5 });
        if (!cancelled) {
          setRecent(data.items);
          setTotal(data.total);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "No se pudo cargar el panel");
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppShell title="Panel">
      <div className="space-y-8">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Resumen</p>
          <p className="mt-2 max-w-xl text-sm text-muted">
            Inicio ligero para el operador. Abre incidentes para hacer triaje; el análisis con IA está
            en el detalle de cada ticket.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-white/10 bg-surface/40 px-5 py-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">
              Tickets abiertos
            </p>
            <p className="mt-2 text-3xl font-semibold text-foreground">{total}</p>
            <Link href="/incidents" className="mt-3 inline-block text-sm text-accent hover:underline">
              Ver todos los incidentes
            </Link>
          </div>
          <div className="rounded-lg border border-white/10 bg-surface/40 px-5 py-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">API</p>
            <div className="mt-3">
              <ApiStatus />
            </div>
          </div>
        </div>

        <section className="space-y-3">
          <h2 className="text-sm font-medium text-foreground">Incidentes recientes</h2>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
          {recent.length === 0 && !error ? (
            <p className="text-sm text-muted">Todavía no hay incidentes.</p>
          ) : (
            <ul className="divide-y divide-white/5 rounded-lg border border-white/10">
              {recent.map((incident) => (
                <li key={incident.id}>
                  <Link
                    href={`/incidents/${incident.id}`}
                    className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 transition hover:bg-white/[0.03]"
                  >
                    <div>
                      <p className="font-mono text-[11px] text-accent">{incident.ticket_number}</p>
                      <p className="text-sm font-medium">{incident.title}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={incident.status} />
                      <PriorityBadge priority={incident.priority} />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </AppShell>
  );
}
