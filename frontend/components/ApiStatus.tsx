"use client";

import { useEffect, useState } from "react";

import { fetchApiStatus } from "@/lib/api";

type LoadState = "loading" | "online" | "offline";

export function ApiStatus() {
  const [state, setState] = useState<LoadState>("loading");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchApiStatus();
        if (cancelled) return;
        if (data.status === "online") {
          setState("online");
          setDetail(`${data.service} · v${data.version} · ${data.environment}`);
        } else {
          setState("offline");
          setDetail(`Estado inesperado: ${data.status}`);
        }
      } catch (error) {
        if (cancelled) return;
        setState("offline");
        setDetail(error instanceof Error ? error.message : "No se pudo contactar con la API");
      }
    }

    void load();
    const id = window.setInterval(() => void load(), 15_000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const label =
    state === "loading"
      ? "API OpsAI: comprobando…"
      : state === "online"
        ? "API OpsAI: en línea"
        : "API OpsAI: fuera de línea";

  const tone =
    state === "online" ? "text-ok" : state === "offline" ? "text-danger" : "text-muted";

  return (
    <div className="rounded-lg border border-white/10 bg-surface/80 px-5 py-4 backdrop-blur">
      <p className={`font-mono text-sm font-medium tracking-wide ${tone}`}>{label}</p>
      {detail ? <p className="mt-2 text-xs text-muted">{detail}</p> : null}
    </div>
  );
}
