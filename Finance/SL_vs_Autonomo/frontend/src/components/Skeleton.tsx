export function ResultSkeleton() {
  return (
    <div className="mt-12 space-y-8 animate-pulse">
      {/* Hero skeleton */}
      <div className="rounded-xl border-l-4 border-gray-200 bg-gray-50 p-6">
        <div className="h-3 w-28 bg-gray-200 rounded mb-3" />
        <div className="h-9 w-44 bg-gray-200 rounded mb-2" />
        <div className="h-3 w-20 bg-gray-200 rounded" />
      </div>
      {/* Rate badges skeleton */}
      <div className="flex gap-4">
        <div className="flex-1 rounded-lg bg-gray-50 p-4 h-20" />
        <div className="flex-1 rounded-lg bg-gray-50 p-4 h-20" />
      </div>
      {/* Bar skeleton */}
      <div className="h-10 w-full bg-gray-200 rounded-full" />
      {/* Chart skeleton */}
      <div className="h-64 w-full bg-gray-50 rounded-xl" />
    </div>
  );
}
