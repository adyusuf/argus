import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { camerasApi, type CameraCreate } from "../api/cameras";
import CameraCard from "../components/CameraCard";
import { useCameraStore } from "../stores/cameraStore";

export default function Cameras() {
  const queryClient = useQueryClient();
  const { selectedCameraId, setSelectedCamera } = useCameraStore();
  const { data: cameras = [] } = useQuery({ queryKey: ["cameras"], queryFn: camerasApi.list });
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<CameraCreate>({ name: "", rtsp_url: "" });

  const createMutation = useMutation({
    mutationFn: camerasApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras"] });
      setShowForm(false);
      setForm({ name: "", rtsp_url: "" });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(form);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e293b" }}>Cameras</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            display: "flex", alignItems: "center", gap: 6,
            background: "#3b82f6", color: "#fff", border: "none",
            borderRadius: 8, padding: "0.5rem 1rem", cursor: "pointer",
            fontSize: "0.875rem", fontWeight: 500,
          }}
        >
          <Plus size={16} /> Add Camera
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ background: "#fff", borderRadius: 12, padding: "1.25rem", marginBottom: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <input
              placeholder="Camera name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              style={{ padding: "0.5rem 0.75rem", border: "1px solid #e2e8f0", borderRadius: 6, fontSize: "0.875rem" }}
            />
            <input
              placeholder="RTSP URL (rtsp://...)"
              value={form.rtsp_url}
              onChange={(e) => setForm({ ...form, rtsp_url: e.target.value })}
              required
              style={{ padding: "0.5rem 0.75rem", border: "1px solid #e2e8f0", borderRadius: 6, fontSize: "0.875rem" }}
            />
            <input
              placeholder="Location (optional)"
              value={form.location ?? ""}
              onChange={(e) => setForm({ ...form, location: e.target.value || undefined })}
              style={{ padding: "0.5rem 0.75rem", border: "1px solid #e2e8f0", borderRadius: 6, fontSize: "0.875rem" }}
            />
          </div>
          <button
            type="submit"
            disabled={createMutation.isPending}
            style={{
              background: "#22c55e", color: "#fff", border: "none",
              borderRadius: 6, padding: "0.5rem 1.25rem", cursor: "pointer",
              fontSize: "0.875rem", fontWeight: 500,
            }}
          >
            {createMutation.isPending ? "Saving..." : "Save Camera"}
          </button>
        </form>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {cameras.map((cam) => (
          <CameraCard key={cam.id} camera={cam} onSelect={setSelectedCamera} selected={selectedCameraId === cam.id} />
        ))}
        {cameras.length === 0 && (
          <p style={{ color: "#94a3b8", gridColumn: "1 / -1", textAlign: "center", padding: "3rem" }}>
            No cameras added yet. Click "Add Camera" to get started.
          </p>
        )}
      </div>
    </div>
  );
}
