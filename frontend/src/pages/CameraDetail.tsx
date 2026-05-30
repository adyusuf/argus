import { useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Wifi, WifiOff, MapPin, Radio, AlertTriangle } from "lucide-react";
import { camerasApi, eventsApi } from "../api/cameras";
import { frameUrl } from "../api/frames";
import { useWebSocket } from "../hooks/useWebSocket";

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function CameraDetail() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data: camera } = useQuery({
    queryKey: ["camera", id],
    queryFn: () => camerasApi.get(id!),
    enabled: !!id,
    refetchInterval: 5000,
  });

  const { data: events = [] } = useQuery({
    queryKey: ["events", { camera_id: id }],
    queryFn: () => eventsApi.list({ camera_id: id!, limit: 50 }),
    enabled: !!id,
  });

  const onWsMessage = useCallback(
    (msg: { type: string }) => {
      if (msg.type === "new_event" || msg.type === "camera_status") {
        queryClient.invalidateQueries({ queryKey: ["camera", id] });
        queryClient.invalidateQueries({ queryKey: ["events", { camera_id: id }] });
      }
    },
    [queryClient, id],
  );

  const { connected } = useWebSocket(onWsMessage);

  if (!camera) {
    return <div style={{ color: "#94a3b8", padding: "3rem", textAlign: "center" }}>Loading...</div>;
  }

  const online = camera.status === "online";
  const fUrl = frameUrl(camera.last_frame);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Link to="/cameras" style={{ color: "#64748b", display: "flex" }}>
            <ArrowLeft size={20} />
          </Link>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b" }}>{camera.name}</h2>
          {online ? <Wifi size={18} color="#22c55e" /> : <WifiOff size={18} color="#ef4444" />}
          <span style={{
            padding: "2px 10px", borderRadius: 9999, fontSize: "0.75rem", fontWeight: 500,
            background: online ? "#dcfce7" : "#fee2e2",
            color: online ? "#166534" : "#991b1b",
          }}>
            {camera.status}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8rem" }}>
          <Radio size={14} color={connected ? "#22c55e" : "#ef4444"} />
          <span style={{ color: connected ? "#22c55e" : "#ef4444" }}>
            {connected ? "Live" : "Connecting..."}
          </span>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20, marginBottom: "2rem" }}>
        <div style={{ background: "#0f172a", borderRadius: 12, overflow: "hidden", position: "relative" }}>
          {fUrl ? (
            <img src={fUrl} alt={camera.name} style={{ width: "100%", display: "block" }} />
          ) : (
            <div style={{ height: 400, display: "flex", alignItems: "center", justifyContent: "center", color: "#475569" }}>
              No frame available
            </div>
          )}
          {camera.last_seen && (
            <div style={{
              position: "absolute", bottom: 12, right: 12,
              background: "rgba(0,0,0,0.7)", color: "#fff",
              padding: "4px 10px", borderRadius: 6, fontSize: "0.75rem",
            }}>
              {timeAgo(camera.last_seen)}
            </div>
          )}
        </div>

        <div style={{ background: "#fff", borderRadius: 12, padding: "1.25rem", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#1e293b", marginBottom: "1rem" }}>Info</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12, fontSize: "0.875rem" }}>
            {camera.location && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#64748b" }}>
                <MapPin size={16} />
                {camera.location}
              </div>
            )}
            <div style={{ color: "#64748b" }}>
              <span style={{ fontWeight: 500, color: "#475569" }}>RTSP: </span>
              <span style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>{camera.rtsp_url.replace(/\/\/([^:]+):([^@]+)@/, "//***:***@")}</span>
            </div>
            <div style={{ color: "#64748b" }}>
              <span style={{ fontWeight: 500, color: "#475569" }}>Events: </span>
              {events.length}
            </div>
            <div style={{ color: "#64748b" }}>
              <span style={{ fontWeight: 500, color: "#475569" }}>Detections: </span>
              {(() => {
                const counts: Record<string, number> = {};
                events.forEach(e => { counts[e.event_type] = (counts[e.event_type] || 0) + 1; });
                return Object.entries(counts).map(([k, v]) => `${k}: ${v}`).join(", ") || "none";
              })()}
            </div>
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#1e293b", marginBottom: "1rem" }}>
        Event History ({events.length})
      </h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
        {events.map((e) => {
          const evtFrame = frameUrl(e.frame_path);
          return (
            <div key={e.id} style={{
              background: "#fff", borderRadius: 10, overflow: "hidden",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}>
              {evtFrame ? (
                <img src={evtFrame} alt={e.event_type} style={{ width: "100%", height: 130, objectFit: "cover", display: "block" }} />
              ) : (
                <div style={{ height: 130, background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <AlertTriangle size={24} color="#cbd5e1" />
                </div>
              )}
              <div style={{ padding: "0.5rem 0.75rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600, fontSize: "0.85rem", color: "#1e293b" }}>{e.event_type}</span>
                  <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>{(e.confidence * 100).toFixed(0)}%</span>
                </div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8", marginTop: 2 }}>
                  {e.created_at ? timeAgo(e.created_at) : "—"}
                </div>
              </div>
            </div>
          );
        })}
        {events.length === 0 && (
          <p style={{ color: "#94a3b8", gridColumn: "1 / -1", textAlign: "center", padding: "2rem" }}>
            No events for this camera yet.
          </p>
        )}
      </div>
    </div>
  );
}
