import { useEffect, useRef, useState } from "react";
import { ArrowUp, Wrench, Loader2 } from "lucide-react";
import { Textarea } from "./ui/primitives";
import { Button } from "./ui/button";
import { cn } from "../lib/utils";

function Bubble({ role, content }) {
  if (role === "tool") {
    return (
      <div className="mb-3 flex justify-start">
        <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          <Wrench size={13} className="mt-0.5 shrink-0" />
          <pre className="whitespace-pre-wrap font-mono">{content}</pre>
        </div>
      </div>
    );
  }
  const isUser = role === "user";
  return (
    <div className={cn("mb-3 flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser ? "bg-zinc-900 text-white rounded-br-sm" : "bg-zinc-100 text-zinc-900 rounded-bl-sm"
        )}
      >
        {content}
      </div>
    </div>
  );
}

export function ChatPane({ messages, onSend, sending }) {
  const [input, setInput] = useState("");
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  function handleSend() {
    const text = input.trim();
    if (!text || sending) return;
    onSend(text);
    setInput("");
  }

  return (
    <div className="flex h-full flex-col">
      <div ref={logRef} className="flex-1 overflow-y-auto px-4 py-4 sm:px-8">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-center text-sm text-zinc-400">
            Start a conversation — try "i want a vps with 5gb ram and 20gb storage and 2 core, name rtx234, ubuntu"
          </div>
        )}
        {messages.map((m, i) => (
          <Bubble key={i} role={m.role} content={m.content} />
        ))}
        {sending && (
          <div className="mb-3 flex items-center gap-2 text-xs text-zinc-400">
            <Loader2 size={13} className="animate-spin" /> thinking…
          </div>
        )}
      </div>

      <div className="border-t border-zinc-200 p-3 sm:p-4">
        <div className="flex items-end gap-2 rounded-xl border border-zinc-300 bg-white p-2 shadow-sm">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
            }}
            placeholder="Message CloudPilot…"
            className="min-h-[40px] border-0 shadow-none focus:ring-0 px-1"
            rows={1}
          />
          <Button size="icon" onClick={handleSend} disabled={sending || !input.trim()}>
            <ArrowUp size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
}
