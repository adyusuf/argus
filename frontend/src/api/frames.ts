const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export function frameUrl(filename: string | null): string | null {
  if (!filename) return null;
  return `${API_BASE}/api/frames/${filename}`;
}
