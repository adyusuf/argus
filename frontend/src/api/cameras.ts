import { api } from "./client";

export interface Camera {
  id: string;
  name: string;
  rtsp_url: string;
  onvif_host: string | null;
  onvif_port: number;
  location: string | null;
  is_active: boolean;
  status: string;
}

export interface CameraCreate {
  name: string;
  rtsp_url: string;
  onvif_host?: string;
  onvif_port?: number;
  location?: string;
}

export interface Event {
  id: string;
  camera_id: string;
  event_type: string;
  confidence: number;
  details: Record<string, unknown> | null;
  frame_path: string | null;
  ai_provider: string;
}

export const camerasApi = {
  list: () => api.get<Camera[]>("/cameras"),
  create: (data: CameraCreate) => api.post<Camera>("/cameras", data),
  get: (id: string) => api.get<Camera>(`/cameras/${id}`),
  delete: (id: string) => api.delete(`/cameras/${id}`),
};

export const eventsApi = {
  list: (params?: { camera_id?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.camera_id) qs.set("camera_id", params.camera_id);
    if (params?.limit) qs.set("limit", String(params.limit));
    const query = qs.toString();
    return api.get<Event[]>(`/events${query ? `?${query}` : ""}`);
  },
};
