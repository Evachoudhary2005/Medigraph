"use client";
import { useRef, useState } from "react";

type Props = {
  language: "en" | "hi";
  onResult: (text: string, confidence: number) => void;
  disabled?: boolean;
};

export default function MicButton({ language, onResult, disabled }: Props) {
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  async function start() {
    setErr(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mr;
      chunksRef.current = [];
      mr.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = async () => {
        setRecording(false);
        streamRef.current?.getTracks().forEach(t => t.stop());
        streamRef.current = null;
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        await upload(blob);
      };
      mr.start();
      setRecording(true);
    } catch (e: any) {
      setErr("Mic error: " + (e?.message ?? String(e)));
    }
  }

  function stop() {
    mediaRecorderRef.current?.stop();
  }

  async function upload(blob: Blob) {
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", blob, "clip.webm");
      fd.append("language", language);
      const r = await fetch("/api/v1/speech/transcribe", { method: "POST", body: fd });
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      onResult(j.text ?? "", j.confidence ?? 0);
    } catch (e: any) {
      setErr("Transcribe error: " + (e?.message ?? String(e)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="inline-flex items-center gap-2">
      {!recording ? (
        <button
          type="button"
          onClick={start}
          disabled={disabled || busy}
          className="px-3 py-1 text-sm rounded border border-slate-300 hover:bg-slate-50 disabled:opacity-50"
          title="Speak your answer"
        >
          {busy ? "…" : "🎤 Speak"}
        </button>
      ) : (
        <button
          type="button"
          onClick={stop}
          className="px-3 py-1 text-sm rounded bg-red-600 text-white animate-pulse"
        >
          ■ Stop
        </button>
      )}
      {err && <span className="text-xs text-red-600">{err}</span>}
    </div>
  );
}