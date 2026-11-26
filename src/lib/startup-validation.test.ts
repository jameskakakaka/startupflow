import { describe, expect, it } from "vitest";

import {
  newStartupSchema,
  updateStartupSchema,
} from "@/lib/startup-validation";

const valid = {
  name: "  MoMo Lite ",
  industry: "Fintech",
  stage: "Seed",
  status: "New",
  score: 7,
};

describe("newStartupSchema", () => {
  it("accepts a valid startup and trims strings", () => {
    const result = newStartupSchema.parse(valid);
    expect(result.name).toBe("MoMo Lite");
  });

  it("rejects unknown keys (mass-assignment guard)", () => {
    expect(
      newStartupSchema.safeParse({ ...valid, id: "x" }).success
    ).toBe(false);
  });

  it.each([0, 11, 5.5])("rejects score %s", (score) => {
    expect(
      newStartupSchema.safeParse({ ...valid, score }).success
    ).toBe(false);
  });

  it("rejects blank name and unknown stage", () => {
    expect(newStartupSchema.safeParse({ ...valid, name: "   " }).success).toBe(false);
    expect(newStartupSchema.safeParse({ ...valid, stage: "IPO" }).success).toBe(false);
  });
});

describe("updateStartupSchema", () => {
  it("requires at least one field", () => {
    expect(updateStartupSchema.safeParse({}).success).toBe(false);
  });

  it("does not allow changing name", () => {
    expect(updateStartupSchema.safeParse({ name: "x" }).success).toBe(false);
  });

  it("accepts a partial update", () => {
    expect(updateStartupSchema.safeParse({ score: 3 }).success).toBe(true);
  });
});
