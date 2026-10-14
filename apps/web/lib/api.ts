import type {
  LiteratureSearchResponse,
  Project,
  ResearchRun,
} from "@neurogenesis/contracts";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}.`, response.status);
  }
  return (await response.json()) as T;
}

export function searchLiterature(query: string): Promise<LiteratureSearchResponse> {
  const parameters = new URLSearchParams({ q: query, limit: "6" });
  return request<LiteratureSearchResponse>(`/v1/literature/search?${parameters}`);
}

export function createProject(): Promise<Project> {
  return request<Project>("/v1/projects", {
    method: "POST",
    body: JSON.stringify({
      name: "Alzheimer — General",
      disease_area: "Alzheimer's disease",
      description: "Evidence-first workspace for general Alzheimer's disease research.",
    }),
  });
}

export function createResearchRun(projectId: string, question: string): Promise<ResearchRun> {
  return request<ResearchRun>("/v1/research-runs", {
    method: "POST",
    body: JSON.stringify({
      project_id: projectId,
      question,
      level: "scientific",
      scope: { species: ["human"] },
      outputs: ["evidence_matrix", "knowledge_graph", "hypotheses"],
    }),
  });
}
