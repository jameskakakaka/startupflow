-- Enforce domain invariants in the database, not only in Zod.
ALTER TABLE "startups"
  ADD CONSTRAINT "startups_score_range" CHECK ("score" BETWEEN 1 AND 10),
  ADD CONSTRAINT "startups_stage_valid" CHECK ("stage" IN ('Pre-Seed', 'Seed', 'Series A')),
  ADD CONSTRAINT "startups_status_valid" CHECK ("status" IN ('New', 'Reviewing', 'Due Diligence', 'Passed'));
