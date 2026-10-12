import { db } from "@/lib/db";

import type {
  NewStartup,
  Startup,
  StartupStage,
  StartupStatus,
  UpdateStartup,
} from "@/types/startup";

type DatabaseStartup = {
  id: string;
  name: string;
  industry: string;
  stage: string;
  status: string;
  score: number;
  createdAt: Date;
};

function toStartup(
  startup: DatabaseStartup
): Startup {
  return {
    id: startup.id,
    name: startup.name,
    industry: startup.industry,
    stage: startup.stage as StartupStage,
    status: startup.status as StartupStatus,
    score: startup.score,
    createdAt: startup.createdAt.toISOString(),
  };
}

export async function getStartups(): Promise<
  Startup[]
> {
  const startups =
    await db.startup.findMany({
      orderBy: {
        createdAt: "desc",
      },
    });

  return startups.map(toStartup);
}

export async function getStartupById(
  id: string
): Promise<Startup | null> {
  const startup =
    await db.startup.findUnique({
      where: {
        id,
      },
    });

  return startup
    ? toStartup(startup)
    : null;
}

export async function createStartup(
  data: NewStartup
): Promise<Startup> {
  const startup =
    await db.startup.create({
      data: {
        name: data.name,
        industry: data.industry,
        stage: data.stage,
        status: data.status,
        score: data.score,
      },
    });

  return toStartup(startup);
}

export async function updateStartup(
  id: string,
  data: UpdateStartup
): Promise<Startup | null> {
  const existing =
    await db.startup.findUnique({
      where: {
        id,
      },
    });

  if (!existing) {
    return null;
  }

  const startup =
    await db.startup.update({
      where: {
        id,
      },

      data,
    });

  return toStartup(startup);
}

export async function deleteStartup(
  id: string
): Promise<boolean> {
  const existing =
    await db.startup.findUnique({
      where: {
        id,
      },
    });

  if (!existing) {
    return false;
  }

  await db.startup.delete({
    where: {
      id,
    },
  });

  return true;
}
