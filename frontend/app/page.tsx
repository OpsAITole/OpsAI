"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiStatus } from "@/components/ApiStatus";
import { getStoredToken, getStoredUser } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (getStoredToken() && getStoredUser()) {
      router.replace("/dashboard");
      return;
    }
    setChecking(false);
  }, [router]);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center text-sm text-muted">
        Loading…
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col justify-center px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">Phase 3 · Incidents</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">OpsAI</h1>
      <p className="mt-4 max-w-xl text-base leading-relaxed text-muted">
        Intelligent IT operations assistant. Track and triage incidents — assistance-only, never
        auto-executes production changes.
      </p>
      <div className="mt-10 space-y-4">
        <ApiStatus />
        <div className="flex flex-wrap gap-3">
          <Link
            href="/login"
            className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-background transition hover:brightness-110"
          >
            Sign in
          </Link>
          <Link
            href="/register"
            className="rounded-md border border-white/15 px-4 py-2 text-sm font-medium text-foreground transition hover:border-accent/50"
          >
            Register
          </Link>
        </div>
      </div>
    </main>
  );
}
