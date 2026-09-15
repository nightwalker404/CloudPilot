import { cn } from "../../lib/utils";

export function Table({ className, ...props }) {
  return (
    <div className="w-full overflow-x-auto">
      <table className={cn("w-full text-sm border-collapse", className)} {...props} />
    </div>
  );
}
export function Thead({ className, ...props }) {
  return <thead className={cn("border-b border-zinc-200 text-left text-xs uppercase tracking-wide text-zinc-500", className)} {...props} />;
}
export function Tr({ className, ...props }) {
  return <tr className={cn("border-b border-zinc-100 last:border-0", className)} {...props} />;
}
export function Th({ className, ...props }) {
  return <th className={cn("py-2 px-3 font-medium", className)} {...props} />;
}
export function Td({ className, ...props }) {
  return <td className={cn("py-2 px-3 align-top", className)} {...props} />;
}
