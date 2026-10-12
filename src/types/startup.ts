export const STARTUP_STAGES = [
  "Pre-Seed",
  "Seed",
  "Series A",
] as const;

export const STARTUP_STATUSES = [
  "New",
  "Reviewing",
  "Due Diligence",
  "Passed",
] as const;

export type StartupStage =
  (typeof STARTUP_STAGES)[number];

export type StartupStatus =
  (typeof STARTUP_STATUSES)[number];

export type Startup = {
  id: string;
  name: string;
  industry: string;
  stage: StartupStage;
  status: StartupStatus;
  score: number;
  createdAt: string;
};

export type NewStartup = Omit<
  Startup,
  "id" | "createdAt"
>;

export type UpdateStartup = Partial<
  Pick<
    Startup,
    "stage" | "status" | "score"
  >
>;
