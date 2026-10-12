"use client";

import {
  useEffect,
  useState,
} from "react";

import type {
  NewStartup,
  Startup,
  StartupStatus,
} from "@/types/startup";

import AddStartupForm from "@/components/AddStartupForm";
import StartupFilters from "@/components/StartupFilters";
import StartupTable from "@/components/StartupTable";
import StatsCard from "@/components/StatsCard";

export default function StartupDashboard() {
  const [startups, setStartups] =
    useState<Startup[]>([]);

  const [searchTerm, setSearchTerm] =
    useState("");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState<
    StartupStatus | "All"
  >("All");

  const [
    isLoading,
    setIsLoading,
  ] = useState(true);

  const [
    fetchError,
    setFetchError,
  ] = useState("");

  useEffect(() => {
    async function fetchStartups() {
      try {
        setIsLoading(true);
        setFetchError("");

        const response =
          await fetch(
            "/api/startups"
          );

        if (!response.ok) {
          throw new Error(
            "Failed to fetch startups."
          );
        }

        const data: Startup[] =
          await response.json();

        setStartups(data);
      } catch (error) {
        setFetchError(
          error instanceof Error
            ? error.message
            : "Unable to load startups."
        );
      } finally {
        setIsLoading(false);
      }
    }

    fetchStartups();
  }, []);

  const total =
    startups.length;

  const reviewing =
    startups.filter(
      (startup) =>
        startup.status ===
        "Reviewing"
    ).length;

  const dueDiligence =
    startups.filter(
      (startup) =>
        startup.status ===
        "Due Diligence"
    ).length;

  const passed =
    startups.filter(
      (startup) =>
        startup.status ===
        "Passed"
    ).length;

  const filteredStartups =
    startups.filter(
      (startup) => {
        const search =
          searchTerm
            .trim()
            .toLowerCase();

        const matchesSearch =
          search === "" ||
          startup.name
            .toLowerCase()
            .includes(search) ||
          startup.industry
            .toLowerCase()
            .includes(search);

        const matchesStatus =
          statusFilter === "All" ||
          startup.status ===
            statusFilter;

        return (
          matchesSearch &&
          matchesStatus
        );
      }
    );

  async function handleAddStartup(
    newStartup: NewStartup
  ) {
    const response =
      await fetch(
        "/api/startups",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify(
              newStartup
            ),
        }
      );

    if (!response.ok) {
      const data =
        await response.json();

      throw new Error(
        data.error ??
          "Failed to create startup."
      );
    }

    const createdStartup: Startup =
      await response.json();

    setStartups(
      (current) => [
        createdStartup,
        ...current,
      ]
    );
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-6xl">
        <div
          role="status"
          className="rounded-xl border p-8 text-center text-gray-500"
        >
          Loading startups...
        </div>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="mx-auto max-w-6xl">
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700"
        >
          <h2 className="font-semibold">
            Unable to load
            startups
          </h2>

          <p className="mt-1 text-sm">
            {fetchError}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
        StartupFlow
      </h1>

      <section className="mt-8">
        <h2 className="text-xl font-semibold">
          Overview
        </h2>

        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Total Startups"
            value={total}
          />

          <StatsCard
            title="Reviewing"
            value={reviewing}
          />

          <StatsCard
            title="Due Diligence"
            value={dueDiligence}
          />

          <StatsCard
            title="Passed"
            value={passed}
          />
        </div>
      </section>

      <section className="mt-8">
        <StartupFilters
          searchTerm={
            searchTerm
          }
          onSearchChange={
            setSearchTerm
          }
          statusFilter={
            statusFilter
          }
          onStatusChange={
            setStatusFilter
          }
        />
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold">
          Add Startup
        </h2>

        <div className="mt-4">
          <AddStartupForm
            onAddStartup={
              handleAddStartup
            }
          />
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold">
          Startups
        </h2>

        <div className="mt-4">
          {filteredStartups.length ===
          0 ? (
            <div className="rounded-xl border border-dashed p-10 text-center">
              <h3 className="font-semibold">
                No startups found
              </h3>

              <p className="mt-2 text-sm text-gray-500">
                Try changing your
                search or status
                filter.
              </p>
            </div>
          ) : (
            <StartupTable
              startups={
                filteredStartups
              }
            />
          )}
        </div>
      </section>
    </div>
  );
}
