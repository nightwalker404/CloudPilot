import { Terminal, CheckCircle2, XCircle, ChevronRight } from "lucide-react";
import { useState } from "react";
import { extractToolExecutions } from "../lib/parseTools";
import { cn } from "../lib/utils";

function ExecutionCard({ exec }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="mb-2 rounded-lg border border-zinc-800 bg-zinc-950/60">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-3 py-2 text-left"
      >
        <div className="flex items-center gap-2">
          <ChevronRight size={13} className={cn("text-zinc-500 transition-transform", open && "rotate-90")} />
          <span className="font-mono text-xs text-emerald-400">{exec.name}</span>
          {exec.isError ? (
            <XCircle size={13} className="text-rose-400" />
          ) : (
            <CheckCircle2 size={13} className="text-emerald-400" />
          )}
        </div>
      </button>
      {open && (
        <div className="space-y-2 border-t border-zinc-800 px-3 py-2">
          <div>
            <p className="mb-1 text-[10px] uppercase tracking-wide text-zinc-500">arguments</p>
            <pre className="overflow-x-auto rounded bg-black/40 p-2 font-mono text-[11px] text-zinc-300">
{JSON.stringify(exec.arguments, null, 2)}
            </pre>
          </div>
          <div>
            <p className="mb-1 text-[10px] uppercase tracking-wide text-zinc-500">result</p>
            <pre className={cn(
              "overflow-x-auto whitespace-pre-wrap rounded bg-black/40 p-2 font-mono text-[11px]",
              exec.isError ? "text-rose-300" : "text-zinc-300"
            )}>
{exec.result ?? "(no result captured)"}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export function InspectorPane({ messages, lastTrace }) {
  const executions = extractToolExecutions(messages);

  return (
    <div className="flex h-full flex-col bg-zinc-900 text-zinc-100">
      <div className="flex items-center gap-2 border-b border-zinc-800 px-4 py-3">
        <Terminal size={14} className="text-emerald-400" />
        <span className="font-mono text-xs font-semibold tracking-wide text-zinc-300">
          AGENT EXECUTION INSPECTOR
        </span>
      </div>

      <div className="flex-1 overflow-y-auto dark-scroll px-3 py-3">
        <p className="mb-2 px-1 text-[10px] uppercase tracking-wide text-zinc-500">
          Tool executions ({executions.length})
        </p>
        {executions.length === 0 && (
          <p className="px-1 text-xs text-zinc-500">
            No tools called yet in this conversation.
          </p>
        )}
        {executions.map((exec, i) => (
          <ExecutionCard key={i} exec={exec} />
        ))}

        <p className="mb-2 mt-5 px-1 text-[10px] uppercase tracking-wide text-zinc-500">
          Last raw trace
        </p>
        {!lastTrace && <p className="px-1 text-xs text-zinc-500">No requests sent yet.</p>}
        {lastTrace && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-3 font-mono text-[11px]">
            <div className="mb-1 flex items-center justify-between text-zinc-400">
              <span>{lastTrace.method} {lastTrace.url.replace(/^https?:\/\/[^/]+/, "")}</span>
              <span className={lastTrace.ok ? "text-emerald-400" : "text-rose-400"}>
                {lastTrace.status} · {lastTrace.durationMs}ms
              </span>
            </div>
            <p className="mt-2 mb-1 text-[10px] uppercase text-zinc-500">request body</p>
            <pre className="overflow-x-auto text-zinc-300">{JSON.stringify(lastTrace.requestBody, null, 2)}</pre>
            <p className="mt-2 mb-1 text-[10px] uppercase text-zinc-500">response</p>
            <pre className="overflow-x-auto whitespace-pre-wrap text-zinc-300">{JSON.stringify(lastTrace.response, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
