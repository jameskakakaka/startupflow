import {
  notFound,
} from "next/navigation";

import StartupDetail from "@/components/StartupDetail";

import {
  getStartupById,
} from "@/lib/startups";

type StartupPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function StartupPage({
  params,
}: StartupPageProps) {
  const { id } =
    await params;

  const startup =
    await getStartupById(id);

  if (!startup) {
    notFound();
  }

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8">
      <StartupDetail
        startup={startup}
      />
    </main>
  );
}
