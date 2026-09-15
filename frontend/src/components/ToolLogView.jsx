import { useEffect, useState } from "react";
import { RefreshCw, Loader2 } from "lucide-react";
import { api } from "../lib/api";
import { extractToolExecutions } from "../lib/parseTools";
import { Button } from "./ui/button";
import { Badge } from "./ui/primitives";
import { Table, Thead, Tr, Th, Td } from "./ui/table";

export function ToolLogView() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const { data: conversations } = await api.listConversations();
      const collected = [];
      for (const c of conversations) {
        const { data: full } = await api.getConversation(c.id);
        const execs = extractToolExecutions(full.messages || []);
        execs.forEach((exec) =>
          collected.push({ ...exec, conversationId: c.id, conversationTitle: c.title, updatedAt: full.updated_at })
        );
      }
      collected.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
      setRows(collected);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Tool Call Log</h1>
          <p className="text-sm text-zinc-500">
            Every tool execution found across all conversations for the current user.
          </p>
        </div>
        <Button variant="outline" onClick={load} disabled={loading}>
          {loading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          Refresh
        </Button>
      </div>

      <p className="mb-3 text-xs text-zinc-400">
        Note: the backend doesn't timestamp individual messages, so "Updated" reflects the
        conversation's last update, not the exact moment the tool ran.
      </p>

      {error && <p className="mb-3 text-sm text-rose-600">{error}</p>}

      <div className="rounded-lg border border-zinc-200 bg-white">
        <Table>
          <Thead>
            <Tr>
              <Th>Tool</Th>
              <Th>Conversation</Th>
              <Th>Arguments</Th>
              <Th>Result</Th>
              <Th>Status</Th>
              <Th>Updated</Th>
            </Tr>
          </Thead>
          <tbody>
            {rows.map((r, i) => (
              <Tr key={i}>
                <Td className="font-mono text-xs">{r.name}</Td>
                <Td className="max-w-[140px] truncate text-xs text-zinc-500">{r.conversationTitle || r.conversationId}</Td>
                <Td className="max-w-[220px]">
                  <pre className="whitespace-pre-wrap font-mono text-[11px] text-zinc-600">
                    {JSON.stringify(r.arguments)}
                  </pre>
                </Td>
                <Td className="max-w-[280px]">
                  <pre className="whitespace-pre-wrap font-mono text-[11px] text-zinc-600">{r.result}</pre>
                </Td>
                <Td>
                  <Badge variant={r.isError ? "error" : "success"}>{r.isError ? "error" : "ok"}</Badge>
                </Td>
                <Td className="whitespace-nowrap text-xs text-zinc-400">
                  {r.updatedAt ? new Date(r.updatedAt).toLocaleString() : "—"}
                </Td>
              </Tr>
            ))}
          </tbody>
        </Table>
        {!loading && rows.length === 0 && (
          <p className="px-4 py-6 text-center text-sm text-zinc-400">No tool calls recorded yet.</p>
        )}
      </div>
    </div>
  );
}
