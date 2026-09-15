import { Plus, Trash2 } from "lucide-react";
import { Sheet } from "./ui/sheet";
import { Button } from "./ui/button";
import { cn } from "../lib/utils";

export function ConversationDrawer({
  open, onClose, conversations, activeId, onSelect, onCreate, onDelete, loading,
}) {
  return (
    <Sheet open={open} onClose={onClose} title="Conversations">
      <div className="p-3">
        <Button className="w-full" onClick={onCreate}>
          <Plus size={14} /> New conversation
        </Button>
      </div>
      <div className="px-2 pb-3">
        {loading && <p className="px-2 text-xs text-zinc-400">Loading…</p>}
        {!loading && conversations.length === 0 && (
          <p className="px-2 text-xs text-zinc-400">No conversations yet.</p>
        )}
        {conversations.map((c) => (
          <div
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={cn(
              "group flex cursor-pointer items-center justify-between rounded-md px-2 py-2 text-sm",
              c.id === activeId ? "bg-zinc-100" : "hover:bg-zinc-50"
            )}
          >
            <div className="min-w-0">
              <p className="truncate font-medium text-zinc-800">{c.title || "Untitled"}</p>
              <p className="truncate font-mono text-[10px] text-zinc-400">{c.id}</p>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(c.id); }}
              className="hidden rounded p-1 text-zinc-400 hover:bg-rose-50 hover:text-rose-500 group-hover:block"
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>
    </Sheet>
  );
}
