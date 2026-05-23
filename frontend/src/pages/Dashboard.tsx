import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Camera, AlertTriangle, Activity, Wifi, Radio } from "lucide-react";
import { camerasApi, eventsApi } from "../api/cameras";
import { useWebSocket } from "../hooks/useWebSocket";

function StatCard({ icon: Icon, label, value, color }: { icon: typeof Camera; label: string; value: number; color: string }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, padding: "1.25rem", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <Icon size={20} color={color} />
        <span style={{ fontSize: "0.85rem", color: "#64748b" }}>{label}</span>
      </div>
      <div style={{ fontSize: "2rem", fontWeight: 700, color: "#1e293b" }}>{value}</div>
    </div>
  );
}

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function Dashboard() {
  const queryClient = useQueryClient();
  const { data: cameras = [] } = useQuery({ queryKey: ["cameras"], queryFn: camerasApi.list });
  const { data: events = [] } = useQuery({ queryKey: ["events"], queryFn: () => eventsApi.list({ limit: 100 }) });

  const onWsMessage = useCallback(
    (msg: { type: string }) => {
      if (msg.type === "new_event") {
        queryClient.invalidateQueries({ queryKey: ["events"] });
      }
      if (msg.type === "camera_status") {
        queryClient.invalidateQueries({ queryKey: ["cameras"] });
      }
    },
    [queryClient],
  );

  const { connected } = useWebSocket(onWsMessage);
  const online = cameras.filter((c) => c.status === "online").length;
  const personEvents = events.filter((e) => e.event_type === "person").length;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b" }}>Dashboard</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8rem" }}>
          <Radio size={14} color={connected ? "#22c55e" : "#ef4444"} />
          <span style={{ color: connected ? "#22c55e" : "#ef4444" }}>
            {connected ? "Live" : "Connecting..."}
          </span>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16, marginBottom: "2rem" }}>
        <StatCard icon={Camera} label="Total Cameras" value={cameras.length} color="#3b82f6" />
        <StatCard icon={Wifi} label="Online" value={online} color="#22c55e" />
        <StatCard icon={AlertTriangle} label="Detections" value={events.length} color="#f59e0b" />
        <StatCard icon={Activity} label="Person Alerts" value={personEvents} color="#ef4444" />
      </div>

      <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#1e293b", marginBottom: "1rem" }}>Recent Events</h3>
      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", textAlign: "left" }}>
              <th style={{ padding: "0.75rem 1rem", color: "#64748b", fontWeight: 500 }}>Type</th>
              <th style={{ padding: "0.75rem 1rem", color: "#64748b", fontWeight: 500 }}>Confidence</th>
              <th style={{ padding: "0.75rem 1rem", color: "#64748b", fontWeight: 500 }}>Provider</th>
              <th style={{ padding: "0.75rem 1rem", color: "#64748b", fontWeight: 500 }}>Camera</th>
              <th style={{ padding: "0.75rem 1rem", color: "#64748b", fontWeight: 500 }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {events.slice(0, 15).map((e) => (
              <tr key={e.id} style={{ borderTop: "1px solid #f1f5f9" }}>
                <td style={{ padding: "0.75rem 1rem", fontWeight: 500 }}>{e.event_type}</td>
                <td style={{ padding: "0.75rem 1rem" }}>{(e.confidence * 100).toFixed(0)}%</td>
                <td style={{ padding: "0.75rem 1rem" }}>{e.ai_provider}</td>
                <td style={{ padding: "0.75rem 1rem", color: "#64748b", fontFamily: "monospace", fontSize: "0.8rem" }}>
                  {e.camera_id.slice(0, 8)}...
                </td>
                <td style={{ padding: "0.75rem 1rem", color: "#94a3b8", fontSize: "0.8rem" }}>
                  {e.created_at ? timeAgo(e.created_at) : "—"}
                </td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: "2rem", textAlign: "center", color: "#94a3b8" }}>
                  No events yet — waiting for AI detections
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
