import { useState } from "react";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { api, getBaseUrl, setBaseUrl, getUserId, setUserId } from "../lib/api";
import { Card } from "./ui/primitives";
import { Input } from "./ui/primitives";
import { Button } from "./ui/button";

export function SettingsView({ onContextChange }) {
  const [baseUrl, setBaseUrlLocal] = useState(getBaseUrl());
  const [userId, setUserIdLocal] = useState(getUserId());
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  function save() {
    setBaseUrl(baseUrl.trim());
    setUserId(userId.trim() || "demo-user");
    onContextChange?.();
  }

  async function testConnection() {
    setTesting(true);
    setTestResult(null);
    save();
    try {
      await api.health();
      setTestResult("ok");
    } catch {
      setTestResult("fail");
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="mb-1 text-lg font-semibold">Settings</h1>
      <p className="mb-6 text-sm text-zinc-500">
        This is a demo tool — auth is a single header, not real accounts. Switch it here to act as a different user.
      </p>

      <Card className="max-w-lg p-5">
        <div className="mb-4">
          <label className="mb-1 block text-xs font-medium text-zinc-600">API Base URL</label>
          <Input value={baseUrl} onChange={(e) => setBaseUrlLocal(e.target.value)} placeholder="http://localhost:8000" />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-xs font-medium text-zinc-600">X-User-ID</label>
          <Input value={userId} onChange={(e) => setUserIdLocal(e.target.value)} placeholder="demo-user" />
          <p className="mt-1 text-[11px] text-zinc-400">
            Sent as the X-User-ID header on every request — the backend has no real login yet.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button onClick={save}>Save</Button>
          <Button variant="outline" onClick={testConnection} disabled={testing}>
            {testing && <Loader2 size={14} className="animate-spin" />}
            Test connection
          </Button>
          {testResult === "ok" && (
            <span className="flex items-center gap-1 text-xs text-emerald-600">
              <CheckCircle2 size={14} /> reachable
            </span>
          )}
          {testResult === "fail" && (
            <span className="flex items-center gap-1 text-xs text-rose-600">
              <XCircle size={14} /> unreachable
            </span>
          )}
        </div>
      </Card>
    </div>
  );
}
