"use client";

import { useState } from "react";

import type {
  NewStartup,
  StartupStage,
  StartupStatus,
} from "@/types/startup";

type AddStartupFormProps = {
  onAddStartup: (
    newStartup: NewStartup
  ) => Promise<void>;
};

const initialFormData: NewStartup = {
  name: "",
  industry: "",
  stage: "Pre-Seed",
  status: "New",
  score: 5,
};

export default function AddStartupForm({
  onAddStartup,
}: AddStartupFormProps) {
  const [formData, setFormData] =
    useState<NewStartup>(initialFormData);

  const [error, setError] = useState("");

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    // -------------------------
    // Client validation
    // -------------------------

    if (formData.name.trim() === "") {
      setError("Company name is required.");
      return;
    }

    if (formData.industry.trim() === "") {
      setError("Industry is required.");
      return;
    }

    if (
      formData.score < 1 ||
      formData.score > 10
    ) {
      setError(
        "Score must be between 1 and 10."
      );
      return;
    }

    // -------------------------
    // POST
    // -------------------------

    try {
      setIsSubmitting(true);
      setError("");

      await onAddStartup({
        ...formData,
        name: formData.name.trim(),
        industry: formData.industry.trim(),
      });

      setFormData(initialFormData);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError(
          "Something went wrong while adding the startup."
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border p-6"
    >
      <div>
        <label
          htmlFor="name"
          className="mb-1 block font-medium"
        >
          Company
        </label>

        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={(event) =>
            setFormData({
              ...formData,
              name: event.target.value,
            })
          }
          className="w-full rounded-lg border px-4 py-2"
        />
      </div>

      <div>
        <label
          htmlFor="industry"
          className="mb-1 block font-medium"
        >
          Industry
        </label>

        <input
          id="industry"
          type="text"
          value={formData.industry}
          onChange={(event) =>
            setFormData({
              ...formData,
              industry: event.target.value,
            })
          }
          className="w-full rounded-lg border px-4 py-2"
        />
      </div>

      <div>
        <label
          htmlFor="stage"
          className="mb-1 block font-medium"
        >
          Stage
        </label>

        <select
          id="stage"
          value={formData.stage}
          onChange={(event) =>
            setFormData({
              ...formData,
              stage:
                event.target.value as StartupStage,
            })
          }
          className="w-full rounded-lg border px-4 py-2"
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
        <label
          htmlFor="status"
          className="mb-1 block font-medium"
        >
          Status
        </label>

        <select
          id="status"
          value={formData.status}
          onChange={(event) =>
            setFormData({
              ...formData,
              status:
                event.target.value as StartupStatus,
            })
          }
          className="w-full rounded-lg border px-4 py-2"
        >
          <option value="New">New</option>

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
        <label
          htmlFor="score"
          className="mb-1 block font-medium"
        >
          Score
        </label>

        <input
          id="score"
          type="number"
          min="1"
          max="10"
          value={formData.score}
          onChange={(event) =>
            setFormData({
              ...formData,
              score: Number(
                event.target.value
              ),
            })
          }
          className="w-full rounded-lg border px-4 py-2"
        />
      </div>

      {error && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-lg bg-black px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting
          ? "Adding..."
          : "Add Startup"}
      </button>
    </form>
  );
}

  
