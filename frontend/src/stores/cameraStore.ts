import { create } from "zustand";
import type { Camera } from "../api/cameras";

interface CameraState {
  selectedCameraId: string | null;
  setSelectedCamera: (id: string | null) => void;
  cameras: Camera[];
  setCameras: (cameras: Camera[]) => void;
}

export const useCameraStore = create<CameraState>((set) => ({
  selectedCameraId: null,
  setSelectedCamera: (id) => set({ selectedCameraId: id }),
  cameras: [],
  setCameras: (cameras) => set({ cameras }),
}));
