import { useEffect, useState, useCallback } from "react";
import { TopBar } from "./components/TopBar";
import { ConversationDrawer } from "./components/ConversationDrawer";
import { ChatPane } from "./components/ChatPane";
import { InspectorPane } from "./components/InspectorPane";
import { ToolLogView } from "./components/ToolLogView";
import { SettingsView } from "./components/SettingsView";
import { api } from "./lib/api";
import { cn } from "./lib/utils";

export default function App() {
  const [view, setView] = useState("chat");
  const [healthy, setHealthy] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [conversations, setConversations] = useState([]);
  const [conversationsLoading, setConversationsLoading] = useState(false);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [lastTrace, setLastTrace] = useState(null);
  const [mobilePane, setMobilePane] = useState("chat");

  const checkHealth = useCallback(async () => {
    try { await api.health(); setHealthy(true); } catch { setHealthy(false); }
  }, []);

  const refreshConversations = useCallback(async () => {
    setConversationsLoading(true);
    try {
      const { data } = await api.listConversations();
      setConversations(data);
    } catch { /* surfaced via health dot */ }
    finally { setConversationsLoading(false); }
  }, []);

  useEffect(() => { checkHealth(); refreshConversations(); }, [checkHealth, refreshConversations]);

  async function loadConversation(id) {
    setActiveId(id);
    setDrawerOpen(false);
    try {
      const { data } = await api.getConversation(id);
      setMessages(data.messages || []);
    } catch (e) {
      setMessages([{ role: "tool", content: `Error loading conversation: ${e.message}` }]);
    }
  }

  async function createConversation() {
    try {
      const { data } = await api.createConversation();
      setActiveId(data.id);
      setMessages([]);
      setLastTrace(null);
      setDrawerOpen(false);
      refreshConversations();
    } catch (e) {
      alert(`Failed to create conversation: ${e.message}`);
    }
  }

  async function deleteConversation(id) {
    try {
      await api.deleteConversation(id);
      if (id === activeId) { setActiveId(null); setMessages([]); }
      refreshConversations();
    } catch (e) {
      alert(`Failed to delete conversation: ${e.message}`);
    }
  }

  async function handleSend(text) {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setSending(true);
    try {
      const { data, trace } = await api.chat({
        messages: [{ role: "user", content: text }],
        conversation_id: activeId,
      });
      setLastTrace(trace);
      setActiveId(data.conversation_id);
      const { data: full } = await api.getConversation(data.conversation_id);
      setMessages(full.messages || []);
      refreshConversations();
    } catch (e) {
      setLastTrace(e.trace || null);
      setMessages((prev) => [...prev, { role: "tool", content: `Error: ${e.message}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <TopBar view={view} onViewChange={setView} onOpenDrawer={() => setDrawerOpen(true)} healthy={healthy} />

      <ConversationDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        conversations={conversations}
        activeId={activeId}
        onSelect={loadConversation}
        onCreate={createConversation}
        onDelete={deleteConversation}
        loading={conversationsLoading}
      />

      {view === "chat" && (
        <>
          {/* Mobile tab switcher */}
          <div className="flex border-b border-zinc-200 lg:hidden">
            {["chat", "inspector"].map((p) => (
              <button
                key={p}
                onClick={() => setMobilePane(p)}
                className={cn(
                  "flex-1 py-2 text-center text-sm font-medium capitalize",
                  mobilePane === p ? "border-b-2 border-zinc-900 text-zinc-900" : "text-zinc-400"
                )}
              >
                {p === "chat" ? "Chat" : "Inspector"}
              </button>
            ))}
          </div>

          <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[1fr_420px]">
            <div className={cn("min-h-0", mobilePane !== "chat" && "hidden lg:block")}>
              <ChatPane messages={messages} onSend={handleSend} sending={sending} />
            </div>
            <div className={cn("min-h-0 border-l border-zinc-800 lg:block", mobilePane !== "inspector" && "hidden lg:block")}>
              <InspectorPane messages={messages} lastTrace={lastTrace} />
            </div>
          </div>
        </>
      )}

      {view === "toolLog" && <ToolLogView />}
      {view === "settings" && <SettingsView onContextChange={() => { checkHealth(); refreshConversations(); }} />}
    </div>
  );
}
