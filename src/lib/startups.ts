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

/**
 * Prisma throws P2025 when the row to update/delete does not exist.
 * Catching it (instead of a separate findUnique first) avoids a
 * check-then-act race between concurrent PATCH and DELETE requests.
 */
function isRecordNotFound(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    (error as { code: unknown }).code === "P2025"
  );
}

export async function updateStartup(
  id: string,
  data: UpdateStartup
): Promise<Startup | null> {
  try {
    const startup = await db.startup.update({
      where: { id },
      data,
    });
    return toStartup(startup);
  } catch (error) {
    if (isRecordNotFound(error)) {
      return null;
    }
    throw error;
  }
}

export async function deleteStartup(
  id: string
): Promise<boolean> {
  try {
    await db.startup.delete({ where: { id } });
    return true;
  } catch (error) {
    if (isRecordNotFound(error)) {
      return false;
    }
    throw error;
  }
}
