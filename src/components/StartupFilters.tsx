import type { StartupStatus } from "@/types/startup";

type StartupFiltersProps = {
  searchTerm: string;
  onSearchChange: (value: string) => void;

  statusFilter: StartupStatus | "All";
  onStatusChange: (
    status: StartupStatus | "All"
  ) => void;
};

export default function StartupFilters({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusChange,
}: StartupFiltersProps) {
  return (
    <div className="flex flex-col gap-4 md:flex-row">
      <input
        type="text"
        value={searchTerm}
        onChange={(event) =>
          onSearchChange(event.target.value)
        }
        placeholder="Search startups..."
        className="w-full rounded-lg border px-4 py-2"
      />

      <select
        value={statusFilter}
        onChange={(event) =>
          onStatusChange(
            event.target.value as
              | StartupStatus
              | "All"
          )
        }
        className="rounded-lg border px-4 py-2"
      >
        <option value="All">All Status</option>
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
  );
}
