import { NextResponse } from "next/server";

import {
  deleteStartup,
  getStartupById,
  updateStartup,
} from "@/lib/startups";

import {
  updateStartupSchema,
} from "@/lib/startup-validation";

type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};

export async function GET(
  _request: Request,
  { params }: RouteContext
) {
  try {
    const { id } = await params;

    const startup =
      await getStartupById(id);

    if (!startup) {
      return NextResponse.json(
        {
          error:
            "Startup not found.",
        },
        {
          status: 404,
        }
      );
    }

    return NextResponse.json(
      startup,
      {
        status: 200,
      }
    );
  } catch (error) {
    console.error(
      "GET startup failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to load startup.",
      },
      {
        status: 500,
      }
    );
  }
}

export async function PATCH(
  request: Request,
  { params }: RouteContext
) {
  try {
    const { id } = await params;

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
      updateStartupSchema.safeParse(
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
      await updateStartup(
        id,
        validation.data
      );

    if (!startup) {
      return NextResponse.json(
        {
          error:
            "Startup not found.",
        },
        {
          status: 404,
        }
      );
    }

    return NextResponse.json(
      startup,
      {
        status: 200,
      }
    );
  } catch (error) {
    console.error(
      "PATCH startup failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to update startup.",
      },
      {
        status: 500,
      }
    );
  }
}

export async function DELETE(
  _request: Request,
  { params }: RouteContext
) {
  try {
    const { id } = await params;

    const deleted =
      await deleteStartup(id);

    if (!deleted) {
      return NextResponse.json(
        {
          error:
            "Startup not found.",
        },
        {
          status: 404,
        }
      );
    }

    return new Response(null, {
      status: 204,
    });
  } catch (error) {
    console.error(
      "DELETE startup failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Failed to delete startup.",
      },
      {
        status: 500,
      }
    );
  }
}
