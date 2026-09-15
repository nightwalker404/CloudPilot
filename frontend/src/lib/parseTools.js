// The backend doesn't attach a tool_call_id to `role: "tool"` messages, so we
// pair each assistant message that has tool_calls with the very next message
// (which should be the tool's result) on a best-effort, order basis.
export function extractToolExecutions(messages) {
  const executions = [];
  for (let i = 0; i < messages.length; i++) {
    const m = messages[i];
    const calls = m.tool_calls;
    if (m.role === "assistant" && Array.isArray(calls) && calls.length > 0) {
      const next = messages[i + 1];
      const result = next && next.role === "tool" ? next.content : null;
      calls.forEach((call) => {
        const fn = call.function || call;
        executions.push({
          name: fn.name || "unknown_tool",
          arguments: fn.arguments || {},
          result,
          isError: typeof result === "string" && result.toLowerCase().startsWith("error"),
        });
      });
    }
  }
  return executions;
}
