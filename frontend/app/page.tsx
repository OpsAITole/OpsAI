import { ApiStatus } from "@/components/ApiStatus";
import { AuthPanel } from "@/components/AuthPanel";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col justify-center px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">Phase 2 · Authentication</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">OpsAI</h1>
      <p className="mt-4 max-w-xl text-base leading-relaxed text-muted">
        Intelligent IT operations assistant. Assistance-only — suggestions never auto-execute
        production changes.
      </p>
      <div className="mt-10 space-y-4">
        <ApiStatus />
        <AuthPanel />
      </div>
    </main>
  );
}
