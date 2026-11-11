"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ReviewRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/clinician/ai-review");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-slate-500 text-sm">
      <div className="flex items-center gap-3">
        <span className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-purple-500 animate-spin" />
        Redirecting to AI Summary Review...
      </div>
    </div>
  );
}