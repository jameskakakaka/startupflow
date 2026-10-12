import { z } from "zod";

import {
  STARTUP_STAGES,
  STARTUP_STATUSES,
} from "@/types/startup";

export const newStartupSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(
        1,
        "Company name is required."
      ),

    industry: z
      .string()
      .trim()
      .min(
        1,
        "Industry is required."
      ),

    stage: z.enum(
      STARTUP_STAGES
    ),

    status: z.enum(
      STARTUP_STATUSES
    ),

    score: z
      .number()
      .int(
        "Score must be an integer."
      )
      .min(
        1,
        "Score must be at least 1."
      )
      .max(
        10,
        "Score must be at most 10."
      ),
  })
  .strict();

export const updateStartupSchema = z
  .object({
    stage: z
      .enum(STARTUP_STAGES)
      .optional(),

    status: z
      .enum(STARTUP_STATUSES)
      .optional(),

    score: z
      .number()
      .int()
      .min(1)
      .max(10)
      .optional(),
  })
  .strict()
  .refine(
    (data) =>
      Object.keys(data).length > 0,
    {
      message:
        "At least one field must be provided.",
    }
  );
