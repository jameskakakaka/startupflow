export type StartupStage =
  | "Pre-Seed"
  | "Seed"
  | "Series A";

export type StartupStatus =
  | "New"
  | "Reviewing"
  | "Due Diligence"
  | "Passed";

export type Startup = {
  id: string;
  name: string;
  industry: string;
  stage: StartupStage;
  status: StartupStatus;
  score: number;
};
