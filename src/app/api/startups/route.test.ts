import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/startups", () => ({
  getStartups: vi.fn(),
  createStartup: vi.fn(),
}));

import { createStartup, getStartups } from "@/lib/startups";
import { GET, POST } from "./route";

const post = (body: string) =>
  POST(new Request("http://test/api/startups", { method: "POST", body }));

describe("/api/startups", () => {
  beforeEach(() => vi.resetAllMocks());

  it("GET returns 500 with an opaque error when the DB fails", async () => {
    vi.mocked(getStartups).mockRejectedValue(new Error("db down: secret detail"));
    vi.spyOn(console, "error").mockImplementation(() => {});
    const res = await GET();
    expect(res.status).toBe(500);
    expect(JSON.stringify(await res.json())).not.toContain("secret");
  });

  it("POST returns 400 on invalid JSON", async () => {
    expect((await post("{not json")).status).toBe(400);
  });

  it("POST returns 400 with field errors on bad input", async () => {
    const res = await post(JSON.stringify({ name: "" }));
    expect(res.status).toBe(400);
    expect((await res.json()).fieldErrors).toHaveProperty("name");
    expect(createStartup).not.toHaveBeenCalled();
  });

  it("POST returns 201 on valid input", async () => {
    const created = { id: "1", name: "A", industry: "B", stage: "Seed", status: "New", score: 5, createdAt: "2026-01-01T00:00:00.000Z" };
    vi.mocked(createStartup).mockResolvedValue(created as never);
    const res = await post(JSON.stringify({ name: "A", industry: "B", stage: "Seed", status: "New", score: 5 }));
    expect(res.status).toBe(201);
  });
});
