"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { PriorityBadge, StatusBadge } from "@/components/IncidentBadges";
import {
  canWriteIncidents,
  getStoredUser,
  INCIDENT_CATEGORIES,
  INCIDENT_PRIORITIES,
  INCIDENT_STATUSES,
  listIncidents,
  type Incident,
  type IncidentCategory,
  type IncidentPriority,
  type IncidentStatus,
  type User,
} from "@/lib/api";

function formatDate(value: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function IncidentsBoard() {
  const [user, setUser] = useState<User | null>(null);
  const [items, setItems] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<IncidentStatus | "">("");
  const [priority, setPriority] = useState<IncidentPriority | "">("");
  const [category, setCategory] = useState<IncidentCategory | "">("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [sortBy, setSortBy] = useState<"created_at" | "priority" | "status" | "title" | "ticket_number">(
    "created_at",
  );
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listIncidents({
        search: search.trim() || undefined,
        status,
        priority,
        category,
        created_from: createdFrom ? new Date(createdFrom).toISOString() : undefined,
        created_to: createdTo ? new Date(`${createdTo}T23:59:59`).toISOString() : undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
        limit: 100,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load incidents");
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, status, priority, category, createdFrom, createdTo, sortBy, sortDir]);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function onFilterSubmit(event: FormEvent) {
    event.preventDefault();
    void load();
  }

  const writable = canWriteIncidents(user);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Incidents</p>
          <p className="mt-1 text-sm text-muted">{total} ticket{total === 1 ? "" : "s"}</p>
        </div>
        {writable ? (
          <Link
            href="/incidents/new"
            className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-background transition hover:brightness-110"
          >
            Create incident
          </Link>
        ) : null}
      </div>

      <form
        onSubmit={onFilterSubmit}
        className="grid gap-3 rounded-lg border border-white/10 bg-surface/50 p-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <label className="block sm:col-span-2 lg:col-span-2">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Search</span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Title, ticket, service…"
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Status</span>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as IncidentStatus | "")}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            <option value="">All</option>
            {INCIDENT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Priority</span>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as IncidentPriority | "")}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            <option value="">All</option>
            {INCIDENT_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Category</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as IncidentCategory | "")}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            <option value="">All</option>
            {INCIDENT_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">From date</span>
          <input
            type="date"
            value={createdFrom}
            onChange={(e) => setCreatedFrom(e.target.value)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">To date</span>
          <input
            type="date"
            value={createdTo}
            onChange={(e) => setCreatedTo(e.target.value)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Sort by</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            <option value="created_at">Created</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="title">Title</option>
            <option value="ticket_number">Ticket</option>
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-[0.14em] text-muted">Direction</span>
          <select
            value={sortDir}
            onChange={(e) => setSortDir(e.target.value as "asc" | "desc")}
            className="mt-1.5 w-full rounded-md border border-white/10 bg-background/50 px-3 py-2 text-sm outline-none ring-accent/40 focus:ring-2"
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </label>
        <div className="flex items-end sm:col-span-2 lg:col-span-4">
          <button
            type="submit"
            className="rounded-md border border-white/15 px-4 py-2 text-sm transition hover:border-accent/50"
          >
            Apply filters
          </button>
        </div>
      </form>

      {error ? <p className="text-sm text-danger">{error}</p> : null}

      {loading ? (
        <p className="text-sm text-muted">Loading incidents…</p>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-white/15 px-6 py-12 text-center">
          <p className="text-sm text-muted">No incidents match these filters.</p>
          {writable ? (
            <Link href="/incidents/new" className="mt-3 inline-block text-sm text-accent hover:underline">
              Create the first incident
            </Link>
          ) : null}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-white/10">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-white/10 bg-surface/80 text-[11px] uppercase tracking-[0.12em] text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Ticket</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {items.map((incident) => (
                <tr key={incident.id} className="border-b border-white/5 transition hover:bg-white/[0.03]">
                  <td className="px-4 py-3 font-mono text-xs text-accent">
                    <Link href={`/incidents/${incident.id}`} className="hover:underline">
                      {incident.ticket_number}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/incidents/${incident.id}`} className="font-medium hover:text-accent">
                      {incident.title}
                    </Link>
                    {incident.affected_service ? (
                      <p className="mt-0.5 text-xs text-muted">{incident.affected_service}</p>
                    ) : null}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={incident.status} />
                  </td>
                  <td className="px-4 py-3">
                    <PriorityBadge priority={incident.priority} />
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted">{incident.category}</td>
                  <td className="px-4 py-3 text-xs text-muted">{formatDate(incident.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
