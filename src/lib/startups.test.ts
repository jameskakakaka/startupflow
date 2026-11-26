import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/db", () => ({
  db: { startup: { update: vi.fn(), delete: vi.fn() } },
}));

import { db } from "@/lib/db";
import { deleteStartup, updateStartup } from "@/lib/startups";

const notFound = Object.assign(new Error("not found"), { code: "P2025" });

describe("data access: not-found handling", () => {
  beforeEach(() => vi.resetAllMocks());

  it("updateStartup returns null when the row is gone (P2025)", async () => {
    vi.mocked(db.startup.update).mockRejectedValue(notFound);
    await expect(updateStartup("x", { score: 2 })).resolves.toBeNull();
  });

  it("deleteStartup returns false when the row is gone (P2025)", async () => {
    vi.mocked(db.startup.delete).mockRejectedValue(notFound);
    await expect(deleteStartup("x")).resolves.toBe(false);
  });

  it("rethrows other database errors", async () => {
    vi.mocked(db.startup.delete).mockRejectedValue(new Error("connection reset"));
    await expect(deleteStartup("x")).rejects.toThrow("connection reset");
  });
});
