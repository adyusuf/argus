import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Radio } from "lucide-react";
import { camerasApi, eventsApi } from "../api/cameras";
import { useWebSocket } from "../hooks/useWebSocket";

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function Events() {
  const queryClient = useQueryClient();
  const { data: events = [] } = useQuery({ queryKey: ["events"], queryFn: () => eventsApi.list({ limit: 200 }) });
  const { data: cameras = [] } = useQuery({ queryKey: ["cameras"], queryFn: camerasApi.list });

  const cameraMap = Object.fromEntries(cameras.map((c) => [c.id, c.name]));

  const onWsMessage = useCallback(
    (msg: { type: string }) => {
      if (msg.type === "new_event") {
        queryClient.invalidateQueries({ queryKey: ["events"] });
      }
    },
    [queryClient],
  );

  const { connected } = useWebSocket(onWsMessage);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b" }}>Events</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8rem" }}>
          <Radio size={14} color={connected ? "#22c55e" : "#ef4444"} />
          <span style={{ color: connected ? "#22c55e" : "#ef4444" }}>
            {connected ? "Live" : "Connecting..."}
          </span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {events.map((e) => (
          <div
            key={e.id}
            style={{
              background: "#fff",
              borderRadius: 10,
              padding: "1rem 1.25rem",
              display: "flex",
              alignItems: "center",
              gap: 12,
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}
          >
            <AlertTriangle
              size={18}
              color={e.event_type === "person" ? "#ef4444" : "#f59e0b"}
            />
            <div style={{ flex: 1 }}>
              <span style={{ fontWeight: 600, color: "#1e293b" }}>{e.event_type}</span>
              <span style={{ color: "#64748b", fontSize: "0.8rem", marginLeft: 8 }}>
                {(e.confidence * 100).toFixed(0)}% — {e.ai_provider}
              </span>
            </div>
            <span style={{ fontSize: "0.8rem", color: "#475569" }}>
              {cameraMap[e.camera_id] ?? e.camera_id.slice(0, 8)}
            </span>
            <span style={{ fontSize: "0.75rem", color: "#94a3b8", minWidth: 60, textAlign: "right" }}>
              {e.created_at ? timeAgo(e.created_at) : "—"}
            </span>
          </div>
        ))}
        {events.length === 0 && (
          <p style={{ color: "#94a3b8", textAlign: "center", padding: "3rem" }}>
            No events detected yet.
          </p>
        )}
      </div>
    </div>
  );
}
