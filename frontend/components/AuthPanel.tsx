"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  clearSession,
  fetchMe,
  getStoredToken,
  getStoredUser,
  logoutUser,
  type User,
} from "@/lib/api";

export function AuthPanel() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const token = getStoredToken();
      const cached = getStoredUser();
      if (!token) {
        if (!cancelled) {
          setUser(null);
          setLoading(false);
        }
        return;
      }
      if (cached && !cancelled) setUser(cached);
      try {
        const me = await fetchMe(token);
        if (!cancelled) setUser(me);
      } catch {
        clearSession();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function onLogout() {
    await logoutUser();
    setUser(null);
  }

  if (loading) {
    return <p className="text-sm text-muted">Checking session…</p>;
  }

  if (!user) {
    return (
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
    );
  }

  return (
    <div className="rounded-lg border border-white/10 bg-surface/80 px-5 py-4 backdrop-blur">
      <p className="font-mono text-xs uppercase tracking-[0.16em] text-accent">Signed in</p>
      <p className="mt-2 text-base font-medium text-foreground">{user.name}</p>
      <p className="mt-1 text-sm text-muted">
        {user.email} · {user.role}
      </p>
      <button
        type="button"
        onClick={() => void onLogout()}
        className="mt-4 rounded-md border border-white/15 px-3 py-1.5 text-sm text-foreground transition hover:border-danger/60 hover:text-danger"
      >
        Log out
      </button>
    </div>
  );
}
