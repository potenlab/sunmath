"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { Sun } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"admin" | "student">("student");
  const [gradeLevel, setGradeLevel] = useState<number>(7);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const body: Record<string, unknown> = { name, email, password, role };
      if (role === "student") body.grade_level = gradeLevel;

      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Registration failed");
      }
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="rounded-2xl border bg-white dark:bg-neutral-900 shadow-xl p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 shadow-md mb-4">
            <Sun className="size-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold">SunMath</h1>
          <p className="text-sm text-muted-foreground mt-1">Create your account</p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 p-3 text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              placeholder="Your name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              placeholder="At least 6 characters"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-3">Role</label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setRole("student")}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-all ${
                  role === "student"
                    ? "border-amber-500 bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400"
                    : "hover:bg-muted"
                }`}
              >
                Student
              </button>
              <button
                type="button"
                onClick={() => setRole("admin")}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-all ${
                  role === "admin"
                    ? "border-amber-500 bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400"
                    : "hover:bg-muted"
                }`}
              >
                Admin
              </button>
            </div>
          </div>
          {role === "student" && (
            <div>
              <label className="block text-sm font-medium mb-1.5">Grade Level</label>
              <select
                value={gradeLevel}
                onChange={(e) => setGradeLevel(Number(e.target.value))}
                className="w-full rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                  <option key={g} value={g}>
                    Grade {g}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2.5 text-sm font-medium text-white hover:from-amber-600 hover:to-orange-600 disabled:opacity-50 transition-all"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href={`/${locale}/login`} className="text-amber-600 hover:text-amber-500 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
