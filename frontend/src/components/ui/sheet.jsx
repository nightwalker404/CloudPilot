import { X } from "lucide-react";
import { cn } from "../../lib/utils";

export function Sheet({ open, onClose, title, children, side = "left" }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div
        className={cn(
          "absolute top-0 h-full w-80 bg-white shadow-xl flex flex-col",
          side === "left" ? "left-0" : "right-0"
        )}
      >
        <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3">
          <h2 className="text-sm font-semibold">{title}</h2>
          <button onClick={onClose} className="rounded p-1 hover:bg-zinc-100">
            <X size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
