"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { loginUser, registerUser, storeSession } from "@/lib/api";

export function RegisterForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      await registerUser({ name, email, password });
      const result = await loginUser({ email, password });
      storeSession(result.access_token, result.user);
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 space-y-5">
      <label className="block">
        <span className="text-xs uppercase tracking-[0.16em] text-muted">Name</span>
        <input
          type="text"
          required
          autoComplete="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-2 w-full rounded-md border border-white/10 bg-background/60 px-3 py-2.5 text-sm text-foreground outline-none ring-accent/40 focus:ring-2"
        />
      </label>
      <label className="block">
        <span className="text-xs uppercase tracking-[0.16em] text-muted">Email</span>
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-2 w-full rounded-md border border-white/10 bg-background/60 px-3 py-2.5 text-sm text-foreground outline-none ring-accent/40 focus:ring-2"
        />
      </label>
      <label className="block">
        <span className="text-xs uppercase tracking-[0.16em] text-muted">Password</span>
        <input
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-2 w-full rounded-md border border-white/10 bg-background/60 px-3 py-2.5 text-sm text-foreground outline-none ring-accent/40 focus:ring-2"
        />
      </label>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-background transition hover:brightness-110 disabled:opacity-60"
      >
        {pending ? "Creating account…" : "Create account"}
      </button>
      <p className="text-sm text-muted">
        Already registered?{" "}
        <Link href="/login" className="text-accent underline-offset-4 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
