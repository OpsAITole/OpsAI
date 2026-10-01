"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { getStoredUser, type User } from "@/lib/api";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  return (
    <AppShell title="Settings">
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Account</p>
          <p className="mt-2 text-sm text-muted">
            Basic profile from Phase 2 auth. Team management and OAuth arrive later.
          </p>
        </div>
        {user ? (
          <dl className="space-y-4 rounded-lg border border-white/10 bg-surface/40 px-5 py-4">
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Name</dt>
              <dd className="mt-1 text-sm">{user.name}</dd>
            </div>
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Email</dt>
              <dd className="mt-1 text-sm">{user.email}</dd>
            </div>
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Role</dt>
              <dd className="mt-1 text-sm">{user.role}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-muted">Loading profile…</p>
        )}
      </div>
    </AppShell>
  );
}
