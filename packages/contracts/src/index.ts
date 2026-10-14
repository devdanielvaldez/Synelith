export type EvidenceStatus =
  | "unreviewed"
  | "reviewed"
  | "contradicted"
  | "retracted";

export interface PubMedArticle {
  pmid: string;
  title: string;
  authors: string[];
  journal: string | null;
  publication_date: string | null;
  doi: string | null;
  source_access: "metadata_only";
}

export interface RetrievalProvenance {
  provider: "NCBI PubMed";
  database: "pubmed";
  query: string;
  retrieved_at: string;
  provider_url: string;
  schema_version: "pubmed-search/v1";
  source_hash: string;
  complete: boolean;
  content_trust: "untrusted_source_metadata";
}

export interface LiteratureSearchResponse {
  total: number;
  returned: number;
  offset: number;
  articles: PubMedArticle[];
  provenance: RetrievalProvenance;
}

export interface Paper {
  id: string;
  title: string;
  doi: string | null;
  pmid: string | null;
  publication_date: string | null;
  review_status: "unreviewed";
  source_id: string;
  source_access: "metadata_only";
  source_hash: string;
  created_at: string;
}

export interface PubMedImportResponse {
  query: string;
  retrieved: number;
  created: number;
  existing: number;
  library_total: number;
  complete: true;
  papers: Paper[];
  disclaimer: string;
}

export interface ResearchRun {
  id: string;
  project_id: string;
  question: string;
  level: "basic" | "intermediate" | "advanced" | "scientific";
  status: "planned";
  created_at: string;
  tasks: Array<{
    order: number;
    agent: string;
    objective: string;
    status: "pending";
  }>;
  disclaimer: string;
}

export interface Project {
  id: string;
  name: string;
  disease_area: string;
  description: string | null;
  status: "active";
  created_at: string;
  updated_at: string;
}
