"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type User = {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "clinician" | "patient";
  is_active: boolean;
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const [newEmail, setNewEmail] = useState("");
  const [newPass, setNewPass] = useState("");
  const [newName, setNewName] = useState("");
  const [newRole, setNewRole] = useState<"clinician" | "patient" | "admin">("clinician");
  const [creating, setCreating] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      const r = await fetch("/api/v1/auth/users");
      if (r.status === 403 || r.status === 401) {
        window.location.href = "/clinician";
        return;
      }
      if (!r.ok) throw new Error(await r.text());
      setUsers(await r.json());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  async function toggle(u: User) {
    setErr(null);
    setBusyId(u.id);
    try {
      const r = await fetch("/api/v1/auth/users/" + u.id + "/toggle-active", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !u.is_active }),
      });
      if (!r.ok) throw new Error(await r.text());
      const updated = await r.json();
      setUsers(prev => prev.map(x => x.id === u.id ? updated : x));
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setBusyId(null);
    }
  }

  async function remove(u: User) {
    const ok = window.confirm(
      "Permanently delete this user?\n\n" +
      u.email + " (" + u.role + ")\n\n" +
      "This cannot be undone."
    );
    if (!ok) return;
    setErr(null);
    setBusyId(u.id);
    try {
      const r = await fetch("/api/v1/auth/users/" + u.id, { method: "DELETE" });
      if (!r.ok) throw new Error(await r.text());
      setUsers(prev => prev.filter(x => x.id !== u.id));
      setMsg("Deleted user: " + u.email);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setBusyId(null);
    }
  }

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setMsg(null);
    setErr(null);
    try {
      const r = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: newEmail,
          password: newPass,
          full_name: newName,
          role: newRole,
        }),
      });
      if (!r.ok) throw new Error(await r.text());
      setMsg("User created: " + newEmail);
      setNewEmail(""); setNewPass(""); setNewName("");
      await load();
    } catch (e: any) {
      setErr("Create failed: " + (e?.message ?? String(e)));
    } finally {
      setCreating(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="max-w-4xl mx-auto p-8">
      <Link href="/clinician" className="text-sm text-blue-600 hover:underline">
        Clinician dashboard
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">User management</h1>
      <p className="mt-1 text-sm text-slate-600">
        Admin-only. Create, activate, deactivate, or delete staff accounts.
      </p>

      {err && <p className="mt-4 text-sm text-red-600">{err}</p>}
      {msg && <p className="mt-4 text-sm text-emerald-700">{msg}</p>}

      <section className="mt-6 rounded border border-slate-200 bg-white p-4">
        <h2 className="font-medium">Create user</h2>
        <form onSubmit={create} className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input required type="email" placeholder="email"
                 value={newEmail} onChange={e => setNewEmail(e.target.value)}
                 className="border border-slate-300 rounded px-3 py-2 text-sm" />
          <input required type="password" placeholder="password (min 6 chars)"
                 minLength={6}
                 value={newPass} onChange={e => setNewPass(e.target.value)}
                 className="border border-slate-300 rounded px-3 py-2 text-sm" />
          <input placeholder="full name"
                 value={newName} onChange={e => setNewName(e.target.value)}
                 className="border border-slate-300 rounded px-3 py-2 text-sm" />
          <select value={newRole} onChange={e => setNewRole(e.target.value as any)}
                  className="border border-slate-300 rounded px-3 py-2 text-sm">
            <option value="clinician">clinician</option>
            <option value="patient">patient</option>
            <option value="admin">admin</option>
          </select>
          <button type="submit" disabled={creating}
                  className="sm:col-span-2 justify-self-start px-4 py-2 rounded bg-blue-600 text-white text-sm disabled:opacity-50">
            {creating ? "Creating..." : "Create user"}
          </button>
        </form>
      </section>

      <section className="mt-6">
        <h2 className="font-medium">Users ({users.length})</h2>
        {loading && <p className="mt-2 text-sm text-slate-500">Loading...</p>}
        {!loading && users.length === 0 && <p className="mt-2 text-sm text-slate-500">None.</p>}
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-slate-200">
              <th className="py-2">Email</th>
              <th>Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-b border-slate-100">
                <td className="py-2">{u.email}</td>
                <td>{u.full_name || "-"}</td>
                <td>
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-xs font-mono">
                    {u.role}
                  </span>
                </td>
                <td>
                  <span className={u.is_active ? "text-emerald-700" : "text-slate-400"}>
                    {u.is_active ? "active" : "inactive"}
                  </span>
                </td>
                <td>
                  <div className="flex gap-2">
                    <button onClick={() => toggle(u)} disabled={busyId === u.id}
                            className="text-xs px-2 py-1 rounded border border-slate-300 hover:bg-slate-50 disabled:opacity-50">
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                    <button onClick={() => remove(u)} disabled={busyId === u.id}
                            className="text-xs px-2 py-1 rounded border border-red-300 text-red-700 hover:bg-red-50 disabled:opacity-50">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-xs text-slate-500">
          You cannot delete your own account or the last remaining admin.
        </p>
      </section>
    </main>
  );
}