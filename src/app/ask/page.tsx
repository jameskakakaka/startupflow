"use client";

import Link from "next/link";
import { useState } from "react";

type Source = {
  n: number;
  chunk_id: string;
  title: string;
  section: string;
  score: number;
  text: string;
};

type AskResponse = {
  found: boolean;
  answer: string;
  citations: number[];
  sources: Source[];
  grounded: boolean;
  unsupported_numbers: string[];
  timings_ms: Record<string, number>;
};

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error ?? "Request failed.");
      }
      setResult(data as AskResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          Deal Memo Copilot
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          Ask about the (synthetic) deal memos in English or Vietnamese.
          Answers cite their sources; unsupported questions return
          &ldquo;not found&rdquo;.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="VíXanh đang gọi vốn bao nhiêu?"
            className="w-full rounded-lg border px-4 py-2"
          />
          <button
            type="submit"
            disabled={isLoading || question.trim().length < 3}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {isLoading ? "Thinking..." : "Ask"}
          </button>
        </form>

        {error && (
          <p role="alert" className="mt-4 text-red-600">
            {error}
          </p>
        )}

        {result && (
          <section className="mt-6 space-y-4">
            <div className="rounded-xl border p-4">
              <p>{result.answer}</p>
              <p className="mt-2 text-xs text-gray-500">
                {result.found
                  ? `Cited: ${result.citations.map((c) => `[${c}]`).join(" ")}`
                  : "Not found in the documents."}
                {!result.grounded &&
                  ` · Warning: unsupported numbers ${result.unsupported_numbers.join(", ")}`}
                {" · "}
                {Object.entries(result.timings_ms)
                  .map(([k, v]) => `${k} ${Math.round(v)} ms`)
                  .join(", ")}
              </p>
            </div>
            <ol className="space-y-2">
              {result.sources.map((s) => (
                <li
                  key={s.chunk_id}
                  className={`rounded-lg border p-3 text-sm ${
                    result.citations.includes(s.n) ? "border-black" : ""
                  }`}
                >
                  <span className="font-medium">
                    [{s.n}] {s.title}
                  </span>{" "}
                  <span className="text-gray-500">({s.chunk_id})</span>
                  <p className="mt-1 text-gray-700">{s.text}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        <Link href="/" className="mt-8 inline-block font-medium hover:underline">
          ← Back to Dashboard
        </Link>
      </div>
    </main>
  );
}
