import { Camera as CameraIcon, Wifi, WifiOff, Trash2 } from "lucide-react";
import type { Camera } from "../api/cameras";

interface Props {
  camera: Camera;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  selected: boolean;
}

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function CameraCard({ camera, onSelect, onDelete, selected }: Props) {
  const online = camera.status === "online";

  return (
    <div
      onClick={() => onSelect(camera.id)}
      style={{
        background: "#fff",
        borderRadius: 12,
        padding: "1.25rem",
        cursor: "pointer",
        border: selected ? "2px solid #38bdf8" : "2px solid transparent",
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        transition: "border-color 0.15s",
        position: "relative",
      }}
    >
      <button
        onClick={(e) => { e.stopPropagation(); onDelete(camera.id); }}
        style={{
          position: "absolute", top: 10, right: 10,
          background: "none", border: "none", cursor: "pointer",
          padding: 4, borderRadius: 4, opacity: 0.4,
        }}
        title="Delete camera"
      >
        <Trash2 size={14} color="#ef4444" />
      </button>

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <CameraIcon size={20} color="#475569" />
        <span style={{ fontWeight: 600, color: "#1e293b" }}>{camera.name}</span>
        {online ? <Wifi size={16} color="#22c55e" /> : <WifiOff size={16} color="#ef4444" />}
      </div>
      <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: 4 }}>
        {camera.location ?? "No location"}
      </div>
      {camera.last_seen && (
        <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: 6 }}>
          Last seen: {timeAgo(camera.last_seen)}
        </div>
      )}
      <div
        style={{
          display: "inline-block",
          padding: "2px 8px",
          borderRadius: 9999,
          fontSize: "0.75rem",
          fontWeight: 500,
          background: online ? "#dcfce7" : "#fee2e2",
          color: online ? "#166534" : "#991b1b",
        }}
      >
        {camera.status}
      </div>
    </div>
  );
}
