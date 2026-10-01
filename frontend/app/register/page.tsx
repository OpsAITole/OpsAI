import Link from "next/link";

import { RegisterForm } from "@/components/RegisterForm";

export default function RegisterPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6 py-16">
      <Link href="/" className="font-mono text-xs uppercase tracking-[0.2em] text-accent">
        OpsAI
      </Link>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">Create account</h1>
      <p className="mt-2 text-sm text-muted">
        Register as a VIEWER by default. Roles ADMIN / TECHNICIAN / VIEWER are enforced by the API.
      </p>
      <RegisterForm />
    </main>
  );
}
