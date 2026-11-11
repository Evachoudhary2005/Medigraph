"use client";
import { useEffect } from "react";
import { getToken } from "@/lib/auth";

/**
 * Patches window.fetch so every /api/... call automatically sends
 * the current bearer token. Runs once, on mount, client-side only.
 */
export default function AuthBootstrap() {
  useEffect(() => {
    const original = window.fetch.bind(window);

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      let url = "";
      if (typeof input === "string") url = input;
      else if (input instanceof URL) url = input.toString();
      else url = input.url;

      // Only inject for our own API calls
      if (url.startsWith("/api/")) {
        const token = getToken();
        if (token) {
          const headers = new Headers(init?.headers);
          if (!headers.has("Authorization")) {
            headers.set("Authorization", "Bearer " + token);
          }
          return original(input, { ...init, headers });
        }
      }
      return original(input, init);
    };

    return () => {
      window.fetch = original;
    };
  }, []);

  return null;
}