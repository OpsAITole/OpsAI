import Link from "next/link";

import { LoginForm } from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6 py-16">
      <Link href="/" className="font-mono text-xs uppercase tracking-[0.2em] text-accent">
        OpsAI
      </Link>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">Sign in</h1>
      <p className="mt-2 text-sm text-muted">Access your OpsAI operator workspace.</p>
      <LoginForm />
    </main>
  );
}
