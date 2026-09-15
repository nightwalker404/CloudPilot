import { Menu, MessageSquare, ListTree, Settings as SettingsIcon, Circle } from "lucide-react";
import { Button } from "./ui/button";
import { cn } from "../lib/utils";

const NAV = [
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "toolLog", label: "Tool Call Log", icon: ListTree },
  { id: "settings", label: "Settings", icon: SettingsIcon },
];

export function TopBar({ view, onViewChange, onOpenDrawer, healthy }) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={onOpenDrawer} title="Conversations">
          <Menu size={18} />
        </Button>
        <span className="font-semibold text-zinc-900">CloudPilot</span>
        <span className="text-xs text-zinc-400">agent inspector</span>
      </div>

      <nav className="flex items-center gap-1">
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onViewChange(id)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              view === id ? "bg-zinc-900 text-white" : "text-zinc-600 hover:bg-zinc-100"
            )}
          >
            <Icon size={14} />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </nav>

      <div className="flex items-center gap-1.5 text-xs text-zinc-500">
        <Circle
          size={8}
          className={cn("fill-current", healthy ? "text-emerald-500" : "text-rose-500")}
        />
        {healthy ? "connected" : "unreachable"}
      </div>
    </header>
  );
}
