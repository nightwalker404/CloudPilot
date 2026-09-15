import { cn } from "../../lib/utils";

const variants = {
  default: "bg-zinc-900 text-white hover:bg-zinc-800",
  outline: "border border-zinc-300 bg-white text-zinc-900 hover:bg-zinc-100",
  ghost: "text-zinc-700 hover:bg-zinc-100",
  destructive: "bg-rose-600 text-white hover:bg-rose-500",
  subtle: "bg-zinc-100 text-zinc-700 hover:bg-zinc-200",
};

const sizes = {
  default: "h-9 px-3 text-sm",
  sm: "h-7 px-2 text-xs",
  icon: "h-9 w-9",
};

export function Button({ className, variant = "default", size = "default", ...props }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors disabled:opacity-40 disabled:pointer-events-none",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  );
}
