import Link from "next/link";

import type { Startup } from "@/types/startup";

type StartupTableProps = {
  startups: Startup[];
};

export default function StartupTable({
  startups,
}: StartupTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-left">
        <thead className="border-b bg-gray-50">
          <tr>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Industry</th>
            <th className="px-4 py-3">Stage</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Score</th>
          </tr>
        </thead>

        <tbody>
          {startups.map((startup) => (
            <tr
              key={startup.id}
              className="border-b last:border-b-0"
            >
              <td className="px-4 py-3">
                <Link
                  href={`/startups/${startup.id}`}
                  className="font-medium hover:underline"
                >
                  {startup.name}
                </Link>
              </td>

              <td className="px-4 py-3">
                {startup.industry}
              </td>

              <td className="px-4 py-3">
                {startup.stage}
              </td>

              <td className="px-4 py-3">
                {startup.status}
              </td>

              <td className="px-4 py-3">
                {startup.score}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
