"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("clinician@medigraph.example.com");
  const [password, setPassword] = useState("clinic123");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    const res = await login(email, password);
    if (res.ok) {
      // Route by role
      const user = (await import("@/lib/auth")).getUser();
      if (user?.role === "admin") {
        router.push("/admin/users");
      } else if (user?.role === "clinician") {
        router.push("/clinician");
      } else {
        router.push("/intake");
      }
    } else {
      setErr("Login failed: " + (res.error ?? "unknown error"));
      setBusy(false);
    }
  }

  const demoAccounts = [
    { role: "Clinician", email: "clinician@medigraph.example.com", password: "clinic123" },
    { role: "Admin",     email: "admin@medigraph.example.com",     password: "admin123" },
    { role: "Patient",   email: "patient@medigraph.example.com",   password: "patient123" },
  ];

  function pick(acct: { email: string; password: string }) {
    setEmail(acct.email);
    setPassword(acct.password);
  }

  return (
    <main className="max-w-md mx-auto p-8">
      <Link href="/" className="text-sm text-blue-600 hover:underline">Home</Link>
      <h1 className="mt-2 text-2xl font-semibold">Sign in to MediGraph</h1>
      <p className="text-sm text-slate-600 mt-1">
        Staff accounts for the clinician and admin views.
      </p>

      <form onSubmit={submit} className="mt-6 space-y-4">
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="mt-1 w-full border border-slate-300 rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="mt-1 w-full border border-slate-300 rounded px-3 py-2"
          />
        </div>

        {err && <p className="text-sm text-red-600">{err}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
        >
          {busy ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <div className="mt-8 border-t border-slate-200 pt-4">
        <p className="text-xs text-slate-500 mb-2">Demo accounts (click to fill):</p>
        <ul className="space-y-1">
          {demoAccounts.map(a => (
            <li key={a.email}>
              <button
                type="button"
                onClick={() => pick(a)}
                className="text-xs text-left w-full px-2 py-1 rounded hover:bg-slate-100"
              >
                <span className="font-medium">{a.role}:</span>{" "}
                <span className="text-slate-600">{a.email} / {a.password}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}