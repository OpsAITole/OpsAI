export function StatusBadge({ status }: { status: string }) {
  const tones: Record<string, string> = {
    NEW: "bg-sky-500/15 text-sky-300",
    INVESTIGATING: "bg-amber-500/15 text-amber-300",
    WAITING: "bg-violet-500/15 text-violet-300",
    RESOLVED: "bg-ok/15 text-ok",
    CLOSED: "bg-white/10 text-muted",
  };
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 font-mono text-[11px] uppercase tracking-wide ${
        tones[status] ?? "bg-white/10 text-muted"
      }`}
    >
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  const tones: Record<string, string> = {
    LOW: "text-muted",
    MEDIUM: "text-sky-300",
    HIGH: "text-amber-300",
    CRITICAL: "text-danger",
  };
  return (
    <span className={`font-mono text-xs uppercase tracking-wide ${tones[priority] ?? "text-muted"}`}>
      {priority}
    </span>
  );
}
