import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { eventsApi } from "../api/cameras";

export default function Events() {
  const { data: events = [] } = useQuery({ queryKey: ["events"], queryFn: () => eventsApi.list({ limit: 200 }) });

  return (
    <div>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b", marginBottom: "1.5rem" }}>Events</h2>

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
            <span style={{ fontFamily: "monospace", fontSize: "0.8rem", color: "#94a3b8" }}>
              {e.camera_id.slice(0, 8)}
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
