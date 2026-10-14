export function formatEvidenceCount(reviewed: number, total: number): string {
  if (total <= 0) return "No evidence reviewed";
  const percent = Math.round((reviewed / total) * 100);
  return `${reviewed} of ${total} reviewed · ${percent}%`;
}
