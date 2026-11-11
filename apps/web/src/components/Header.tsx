"use client";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { AuthUser, getUser, logout } from "@/lib/auth";

export default function Header() {
  const pathname = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const isLanding = pathname === "/";

  useEffect(() => { setUser(getUser()); }, [pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Hide header on patient-facing pages and login.
  // Intake flow has its own step indicator + back link.
  if (pathname === "/login") return null;
  if (pathname === "/intake") return null;
  if (pathname.startsWith("/intake/")) return null;

  return (
    <header
      className={
        "fixed top-0 left-0 right-0 z-40 transition-all duration-300 " +
        (scrolled
          ? "bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/70 dark:border-slate-800/70 shadow-[0_1px_0_rgba(15,23,42,0.04),0_8px_24px_-12px_rgba(15,23,42,0.15)]"
          : isLanding
          ? "bg-gradient-to-b from-slate-950/70 to-transparent border-b border-transparent"
          : "bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800")
      }
    >
      <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-6">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-2.5 shrink-0">
          <span className="relative">
            <span className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-lg shadow-blue-500/30 group-hover:scale-105 transition-transform">
              M
            </span>
            {/* pulsing live dot */}
            <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-white dark:border-slate-900" />
            </span>
          </span>
          <div className="leading-tight">
            <div
              className={
                "font-semibold text-base transition-colors " +
                (scrolled || !isLanding
                  ? "text-slate-900 dark:text-white"
                  : "text-white")
              }
            >
              MediGraph
            </div>
            <div
              className={
                "text-[10px] uppercase tracking-widest transition-colors " +
                (scrolled || !isLanding
                  ? "text-slate-500 dark:text-slate-400"
                  : "text-blue-200/80")
              }
            >
              Local clinical AI
            </div>
          </div>
        </Link>

        {/* Center nav (desktop) */}
        <nav className="hidden md:flex items-center gap-1 text-sm">
          <HeaderLink href="/intake"     pathname={pathname} scrolled={scrolled} isLanding={isLanding}>
            Intake
          </HeaderLink>
          <HeaderLink href="/clinician"  pathname={pathname} scrolled={scrolled} isLanding={isLanding}>
            Clinician
          </HeaderLink>
          {isLanding && (
            <>
              <a
                href="#demo"
                className={
                  "px-3 py-1.5 rounded-lg transition-colors " +
                  (scrolled
                    ? "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
                    : "text-blue-100/80 hover:text-white hover:bg-white/10")
                }
              >
                Try it
              </a>
              <a
                href="#pipeline"
                className={
                  "px-3 py-1.5 rounded-lg transition-colors " +
                  (scrolled
                    ? "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
                    : "text-blue-100/80 hover:text-white hover:bg-white/10")
                }
              >
                Pipeline
              </a>
            </>
          )}
          {user?.role === "admin" && (
            <HeaderLink href="/admin/users" pathname={pathname} scrolled={scrolled} isLanding={isLanding}>
              Admin
            </HeaderLink>
          )}
        </nav>

        {/* Right: user / sign in */}
        <div className="flex items-center gap-2 shrink-0">
          <StatusPill scrolled={scrolled || !isLanding} />
          {user ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:block text-right leading-tight">
                <div
                  className={
                    "text-xs font-medium " +
                    (scrolled || !isLanding
                      ? "text-slate-800 dark:text-slate-200"
                      : "text-white")
                  }
                >
                  {user.full_name || user.email.split("@")[0]}
                </div>
                <div
                  className={
                    "text-[10px] font-mono uppercase " +
                    (scrolled || !isLanding
                      ? "text-slate-500 dark:text-slate-400"
                      : "text-blue-200/80")
                  }
                >
                  {user.role}
                </div>
              </div>
              <button
                onClick={logout}
                className={
                  "text-xs px-3 py-1.5 rounded-lg border transition-colors " +
                  (scrolled || !isLanding
                    ? "border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
                    : "border-white/20 text-white hover:bg-white/10")
                }
              >
                Sign out
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className={
                "text-xs px-3.5 py-1.5 rounded-lg font-medium transition-all hover:-translate-y-0.5 " +
                (scrolled || !isLanding
                  ? "bg-blue-600 text-white hover:bg-blue-700 shadow-sm shadow-blue-500/20"
                  : "bg-white text-slate-900 hover:bg-blue-50 shadow-lg shadow-blue-500/20")
              }
            >
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

function HeaderLink({
  href, pathname, scrolled, isLanding, children,
}: {
  href: string;
  pathname: string;
  scrolled: boolean;
  isLanding: boolean;
  children: React.ReactNode;
}) {
  const active = pathname.startsWith(href);
  return (
    <Link
      href={href}
      className={
        "px-3 py-1.5 rounded-lg transition-colors " +
        (active
          ? scrolled || !isLanding
            ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white font-medium"
            : "bg-white/10 text-white font-medium"
          : scrolled || !isLanding
          ? "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
          : "text-blue-100/80 hover:text-white hover:bg-white/10")
      }
    >
      {children}
    </Link>
  );
}

function StatusPill({ scrolled }: { scrolled: boolean }) {
  return (
    <div
      className={
        "hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium uppercase tracking-wider transition-colors " +
        (scrolled
          ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
          : "bg-emerald-500/15 text-emerald-100 border border-emerald-400/30")
      }
      title="All AI runs on this machine"
    >
      <span className="relative flex h-1.5 w-1.5">
        <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
      </span>
      On-premises
    </div>
  );
}