import clsx from 'clsx';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}

export function Skeleton({ className, variant = 'rectangular', width, height }: SkeletonProps) {
  return (
    <div
      className={clsx(
        "bg-gray-800/50 anim-shimmer rounded",
        variant === 'circular' && "rounded-full",
        className
      )}
      style={{ width, height }}
    />
  );
}
