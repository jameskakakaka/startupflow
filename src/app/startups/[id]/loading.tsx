export default function Loading() {
  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-3xl">
        <div
          role="status"
          className="rounded-xl border p-8 text-gray-500"
        >
          Loading startup...
        </div>
      </div>
    </main>
  );
}
