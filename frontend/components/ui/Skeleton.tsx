export function Skeleton({ className = '', height = 'h-40' }: { className?: string; height?: string }) {
  return (
    <div className={`skeleton ${height} ${className}`} />
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`skeleton h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`} />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="card p-6 space-y-4">
      <div className="skeleton h-6 w-1/3" />
      <SkeletonText lines={3} />
      <div className="skeleton h-48" />
    </div>
  );
}
