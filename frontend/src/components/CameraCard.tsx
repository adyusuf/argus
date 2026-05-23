import { Camera as CameraIcon, Wifi, WifiOff } from "lucide-react";
import type { Camera } from "../api/cameras";

interface Props {
  camera: Camera;
  onSelect: (id: string) => void;
  selected: boolean;
}

export default function CameraCard({ camera, onSelect, selected }: Props) {
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
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <CameraIcon size={20} color="#475569" />
          <span style={{ fontWeight: 600, color: "#1e293b" }}>{camera.name}</span>
        </div>
        {online ? <Wifi size={16} color="#22c55e" /> : <WifiOff size={16} color="#ef4444" />}
      </div>
      <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
        {camera.location ?? "No location"}
      </div>
      <div
        style={{
          marginTop: 8,
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
