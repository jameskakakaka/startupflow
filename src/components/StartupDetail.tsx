 "use client";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import { useState } from "react";

import type {
  Startup,
  StartupStage,
  StartupStatus,
} from "@/types/startup";

type StartupDetailProps = {
  startup: Startup;
};

export default function StartupDetail({
  startup,
}: StartupDetailProps) {
  const router = useRouter();

  const [stage, setStage] =
    useState<StartupStage>(
      startup.stage
    );

  const [status, setStatus] =
    useState<StartupStatus>(
      startup.status
    );

  const [score, setScore] =
    useState(
      startup.score
    );

  const [error, setError] =
    useState("");

  const [
    successMessage,
    setSuccessMessage,
  ] = useState("");

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    isDeleting,
    setIsDeleting,
  ] = useState(false);

  async function handleSave(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    try {
      setIsSaving(true);
      setError("");
      setSuccessMessage("");

      const response =
        await fetch(
          `/api/startups/${startup.id}`,
          {
            method: "PATCH",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                stage,
                status,
                score,
              }),
          }
        );

      if (!response.ok) {
        const data =
          await response.json();

        throw new Error(
          data.error ??
            "Failed to update startup."
        );
      }

      await response.json();

      setSuccessMessage(
        "Changes saved successfully."
      );

      router.refresh();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to update startup."
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    const confirmed =
      window.confirm(
        `Delete ${startup.name}?`
      );

    if (!confirmed) {
      return;
    }

    try {
      setIsDeleting(true);
      setError("");
      setSuccessMessage("");

      const response =
        await fetch(
          `/api/startups/${startup.id}`,
          {
            method: "DELETE",
          }
        );

      if (!response.ok) {
        let message =
          "Failed to delete startup.";

        try {
          const data =
            await response.json();

          message =
            data.error ??
            message;
        } catch {}

        throw new Error(
          message
        );
      }

      router.push("/");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete startup."
      );

      setIsDeleting(false);
    }
  }

  const fieldClasses =
    "w-full rounded-lg border px-4 py-2.5 outline-none transition focus:border-black focus:ring-2 focus:ring-black/10 disabled:opacity-50";

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-bold tracking-tight">
        {startup.name}
      </h1>

      <p className="mt-2 text-gray-600">
        {startup.industry}
      </p>

      <form
        onSubmit={handleSave}
        className="mt-8 space-y-6 rounded-xl border bg-white p-6"
      >
        <div>
          <label className="mb-1 block font-medium">
            Stage
          </label>

          <select
            value={stage}
            disabled={isSaving}
            onChange={(event) =>
              setStage(
                event.target
                  .value as StartupStage
              )
            }
            className={
              fieldClasses
            }
          >
            <option value="Pre-Seed">
              Pre-Seed
            </option>

            <option value="Seed">
              Seed
            </option>

            <option value="Series A">
              Series A
            </option>
          </select>
        </div>

        <div>
          <label className="mb-1 block font-medium">
            Status
          </label>

          <select
            value={status}
            disabled={isSaving}
            onChange={(event) =>
              setStatus(
                event.target
                  .value as StartupStatus
              )
            }
            className={
              fieldClasses
            }
          >
            <option value="New">
              New
            </option>

            <option value="Reviewing">
              Reviewing
            </option>

            <option value="Due Diligence">
              Due Diligence
            </option>

            <option value="Passed">
              Passed
            </option>
          </select>
        </div>

        <div>
          <label className="mb-1 block font-medium">
            Score
          </label>

          <input
            type="number"
            min="1"
            max="10"
            value={score}
            disabled={isSaving}
            onChange={(event) =>
              setScore(
                Number(
                  event.target
                    .value
                )
              )
            }
            className={
              fieldClasses
            }
          />
        </div>

        {error && (
          <p
            role="alert"
            className="text-red-600"
          >
            {error}
          </p>
        )}

        {successMessage && (
          <p
            role="status"
            className="text-green-700"
          >
            {successMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={isSaving}
          className="rounded-lg bg-black px-5 py-2.5 text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSaving
            ? "Saving..."
            : "Save Changes"}
        </button>
      </form>

      <div className="mt-8 border-t pt-6">
        <button
          type="button"
          onClick={
            handleDelete
          }
          disabled={
            isDeleting
          }
          className="rounded-lg border border-red-600 px-5 py-2.5 text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isDeleting
            ? "Deleting..."
            : "Delete Startup"}
        </button>
      </div>

      <Link
        href="/"
        className="mt-8 inline-block font-medium hover:underline"
      >
        ← Back to Dashboard
      </Link>
    </div>
  );
}     
