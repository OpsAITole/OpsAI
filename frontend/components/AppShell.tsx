"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import {
  clearSession,
  fetchMe,
  getStoredToken,
  getStoredUser,
  logoutUser,
  type User,
} from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Dashboard", soon: false },
  { href: "/incidents", label: "Incidents", soon: false },
  { href: "/settings", label: "Settings", soon: false },
  { href: "#", label: "Observability", soon: true },
  { href: "#", label: "AI Assistant", soon: true },
  { href: "#", label: "Agent", soon: true },
] as const;

type AppShellProps = {
  children: ReactNode;
  title?: string;
};

export function AppShell({ children, title }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const token = getStoredToken();
      if (!token) {
        if (!cancelled) {
          setUser(null);
          setLoading(false);
          router.replace("/login");
        }
        return;
      }
      const cached = getStoredUser();
      if (cached && !cancelled) setUser(cached);
      try {
        const me = await fetchMe(token);
        if (!cancelled) {
          setUser(me);
          setLoading(false);
        }
      } catch {
        clearSession();
        if (!cancelled) {
          setUser(null);
          setLoading(false);
          router.replace("/login");
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [router]);

  async function onLogout() {
    await logoutUser();
    router.replace("/login");
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted">
        Loading workspace…
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex min-h-screen">
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-white/10 bg-surface/95 backdrop-blur transition-transform lg:static lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="border-b border-white/10 px-5 py-5">
          <Link href="/dashboard" className="block">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-accent">OpsAI</p>
            <p className="mt-1 text-sm text-muted">IT operations assistant</p>
          </Link>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {NAV.map((item) => {
            const active =
              !item.soon &&
              (pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href)));
            if (item.soon) {
              return (
                <span
                  key={item.label}
                  className="flex items-center justify-between rounded-md px-3 py-2 text-sm text-muted/60"
                >
                  {item.label}
                  <span className="font-mono text-[10px] uppercase tracking-wider text-muted/50">
                    soon
                  </span>
                </span>
              );
            }
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`block rounded-md px-3 py-2 text-sm transition ${
                  active
                    ? "bg-accent/15 font-medium text-accent"
                    : "text-foreground/85 hover:bg-white/5 hover:text-foreground"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 px-4 py-4">
          <p className="truncate text-sm font-medium text-foreground">{user.name}</p>
          <p className="truncate text-xs text-muted">
            {user.email} · {user.role}
          </p>
          <button
            type="button"
            onClick={() => void onLogout()}
            className="mt-3 text-xs text-muted transition hover:text-danger"
          >
            Log out
          </button>
        </div>
      </aside>

      {mobileOpen ? (
        <button
          type="button"
          aria-label="Close menu"
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-white/10 bg-background/80 px-4 py-3 backdrop-blur sm:px-6">
          <button
            type="button"
            className="rounded-md border border-white/15 px-2.5 py-1.5 text-xs lg:hidden"
            onClick={() => setMobileOpen(true)}
          >
            Menu
          </button>
          <h1 className="text-base font-semibold tracking-tight text-foreground sm:text-lg">
            {title ?? "OpsAI"}
          </h1>
        </header>
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
