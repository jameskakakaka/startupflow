import { NextResponse } from "next/server";

import {
  createStartup,
  getStartups,
} from "@/lib/startups";

import {
  newStartupSchema,
} from "@/lib/startup-validation";

export async function GET() {
  try {
    const startups =
      await getStartups();

    return NextResponse.json(
      startups,
      {
        status: 200,
      }
    );
  } catch (error) {
    console.error(
      "GET /api/startups failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to load startups.",
      },
      {
        status: 500,
      }
    );
  }
}

export async function POST(
  request: Request
) {
  try {
    let body: unknown;

    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        {
          error:
            "Invalid JSON body.",
        },
        {
          status: 400,
        }
      );
    }

    const validation =
      newStartupSchema.safeParse(
        body
      );

    if (!validation.success) {
      return NextResponse.json(
        {
          error:
            "Validation failed.",

          fieldErrors:
            validation.error
              .flatten()
              .fieldErrors,
        },
        {
          status: 400,
        }
      );
    }

    const startup =
      await createStartup(
        validation.data
      );

    return NextResponse.json(
      startup,
      {
        status: 201,
      }
    );
  } catch (error) {
    console.error(
      "POST /api/startups failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to create startup.",
      },
      {
        status: 500,
      }
    );
  }
}
