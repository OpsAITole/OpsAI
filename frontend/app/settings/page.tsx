"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { getStoredUser, type User } from "@/lib/api";
import { roleLabel } from "@/lib/labels";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  return (
    <AppShell title="Ajustes">
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Cuenta</p>
          <p className="mt-2 text-sm text-muted">
            Perfil básico de autenticación. La gestión de equipos y OAuth llegarán más adelante.
          </p>
        </div>
        {user ? (
          <dl className="space-y-4 rounded-lg border border-white/10 bg-surface/40 px-5 py-4">
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Nombre</dt>
              <dd className="mt-1 text-sm">{user.name}</dd>
            </div>
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Correo</dt>
              <dd className="mt-1 text-sm">{user.email}</dd>
            </div>
            <div>
              <dt className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">Rol</dt>
              <dd className="mt-1 text-sm">{roleLabel(user.role)}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-muted">Cargando perfil…</p>
        )}
      </div>
    </AppShell>
  );
}
