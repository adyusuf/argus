import { useQuery } from "@tanstack/react-query";
import { Camera, AlertTriangle, Activity, Wifi } from "lucide-react";
import { camerasApi, eventsApi } from "../api/cameras";

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

export default function Dashboard() {
  const { data: cameras = [] } = useQuery({ queryKey: ["cameras"], queryFn: camerasApi.list });
  const { data: events = [] } = useQuery({ queryKey: ["events"], queryFn: () => eventsApi.list({ limit: 100 }) });

  const online = cameras.filter((c) => c.status === "online").length;
  const personEvents = events.filter((e) => e.event_type === "person").length;

  return (
    <div>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b", marginBottom: "1.5rem" }}>Dashboard</h2>

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
            </tr>
          </thead>
          <tbody>
            {events.slice(0, 10).map((e) => (
              <tr key={e.id} style={{ borderTop: "1px solid #f1f5f9" }}>
                <td style={{ padding: "0.75rem 1rem", fontWeight: 500 }}>{e.event_type}</td>
                <td style={{ padding: "0.75rem 1rem" }}>{(e.confidence * 100).toFixed(0)}%</td>
                <td style={{ padding: "0.75rem 1rem" }}>{e.ai_provider}</td>
                <td style={{ padding: "0.75rem 1rem", color: "#64748b", fontFamily: "monospace", fontSize: "0.8rem" }}>
                  {e.camera_id.slice(0, 8)}...
                </td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: "2rem", textAlign: "center", color: "#94a3b8" }}>
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
