import { NextResponse } from "next/server";
import { z } from "zod";

const askSchema = z
  .object({
    question: z.string().trim().min(3).max(500),
  })
  .strict();

const AI_SERVICE_URL =
  process.env.AI_SERVICE_URL ?? "http://127.0.0.1:8000";

// Proxy to the Python RAG service so the browser never talks to it directly.
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const parsed = askSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Question must be 3-500 characters." },
      { status: 400 }
    );
  }

  try {
    const res = await fetch(`${AI_SERVICE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(parsed.data),
      signal: AbortSignal.timeout(90_000),
    });
    if (!res.ok) {
      return NextResponse.json(
        { error: `AI service returned ${res.status}.` },
        { status: 502 }
      );
    }
    return NextResponse.json(await res.json());
  } catch (error) {
    console.error("POST /api/ask failed:", error);
    return NextResponse.json(
      { error: "AI service is unavailable." },
      { status: 503 }
    );
  }
}
