export function frameUrl(filename: string | null): string | null {
  if (!filename) return null;
  return `/api/frames/${filename}`;
}
