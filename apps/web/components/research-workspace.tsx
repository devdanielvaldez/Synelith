"use client";

import type { LiteratureSearchResponse, ResearchRun } from "@neurogenesis/contracts";
import { FormEvent, useState } from "react";

import { createResearchRun, searchLiterature } from "../lib/api";
import { BookIcon, FlaskIcon, GraphIcon, MarkIcon, SearchIcon } from "./icons";

const DEFAULT_QUESTION =
  "How do APOE-associated lipid states relate to microglial activation in Alzheimer's disease?";

const activity = [
  { code: "SRC", label: "Seed corpus", value: "24", detail: "curated records · demo" },
  { code: "CLM", label: "Evidence claims", value: "—", detail: "awaiting extraction" },
  { code: "RUN", label: "Active runs", value: "0", detail: "no execution started" },
];

export function ResearchWorkspace() {
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const [query, setQuery] = useState("APOE microglia Alzheimer's disease");
  const [run, setRun] = useState<ResearchRun | null>(null);
  const [search, setSearch] = useState<LiteratureSearchResponse | null>(null);
  const [busy, setBusy] = useState<"plan" | "search" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function planRun() {
    setBusy("plan");
    setError(null);
    try {
      setRun(await createResearchRun(question));
    } catch {
      setError("The API is unavailable. Start the local API and try again.");
    } finally {
      setBusy(null);
    }
  }

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("search");
    setError(null);
    try {
      setSearch(await searchLiterature(query));
    } catch {
      setError("PubMed metadata could not be retrieved. No result was recorded as complete.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark"><MarkIcon /></span>
          <span>NeuroGenesis <b>AI</b></span>
        </div>

        <nav aria-label="Primary navigation" className="nav-list">
          <a className="nav-item active" href="#workspace"><span>⌁</span>Workspace</a>
          <a className="nav-item" href="#literature"><BookIcon />Literature</a>
          <a className="nav-item" href="#graph"><GraphIcon />Knowledge graph</a>
          <a className="nav-item" href="#experiments"><FlaskIcon />Experiments</a>
        </nav>

        <div className="sidebar-note">
          <span className="eyebrow">Research mode</span>
          <strong>Evidence first</strong>
          <p>Computational outputs require independent expert validation.</p>
        </div>
      </aside>

      <main id="workspace" className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">Project / Alzheimer — General</span>
            <h1>Research workspace</h1>
          </div>
          <div className="status-pill"><span /> API-backed prototype</div>
        </header>

        <section className="hero-grid">
          <article className="question-card">
            <div className="section-heading">
              <div>
                <span className="eyebrow">New investigation</span>
                <h2>What should we investigate?</h2>
              </div>
              <span className="step-label">01 / PLAN</span>
            </div>
            <textarea
              aria-label="Research question"
              onChange={(event) => setQuestion(event.target.value)}
              value={question}
            />
            <div className="card-actions">
              <p>Creates an auditable plan. It does not execute an experiment.</p>
              <button disabled={busy !== null || question.trim().length < 10} onClick={planRun}>
                {busy === "plan" ? "Planning…" : "Build research plan"}<span>→</span>
              </button>
            </div>
          </article>

          <article className="signal-card">
            <span className="eyebrow">Scientific boundary</span>
            <div className="signal-graphic" aria-hidden="true">
              <i className="node n1" /><i className="node n2" /><i className="node n3" />
              <i className="node n4" /><i className="node n5" /><i className="line l1" />
              <i className="line l2" /><i className="line l3" /><i className="line l4" />
            </div>
            <h3>Trace every claim.</h3>
            <p>Findings, predictions, and hypotheses remain visibly separate throughout the workflow.</p>
          </article>
        </section>

        {error ? <div className="notice error" role="alert">{error}</div> : null}

        {run ? (
          <section className="run-panel" aria-live="polite">
            <div className="section-heading">
              <div><span className="eyebrow">Run {run.id.slice(0, 8)}</span><h2>Plan ready for review</h2></div>
              <span className="state-badge">{run.status}</span>
            </div>
            <div className="task-list">
              {run.tasks.map((task) => (
                <div className="task" key={task.order}>
                  <span>{String(task.order).padStart(2, "0")}</span>
                  <div><strong>{task.agent}</strong><p>{task.objective}</p></div>
                  <em>{task.status}</em>
                </div>
              ))}
            </div>
            <p className="disclaimer">{run.disclaimer}</p>
          </section>
        ) : null}

        <section className="metrics" aria-label="Workspace summary">
          {activity.map((item) => (
            <article key={item.code}>
              <span className="metric-code">{item.code}</span>
              <div><span>{item.label}</span><strong>{item.value}</strong><small>{item.detail}</small></div>
            </article>
          ))}
        </section>

        <section id="literature" className="literature-panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Live metadata / NCBI PubMed</span>
              <h2>Literature search</h2>
            </div>
            <span className="step-label">02 / RETRIEVE</span>
          </div>
          <form className="search-form" onSubmit={submitSearch}>
            <SearchIcon />
            <input
              aria-label="Search PubMed"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search terms, genes, mechanisms…"
              value={query}
            />
            <button disabled={busy !== null || query.trim().length < 2} type="submit">
              {busy === "search" ? "Searching…" : "Search PubMed"}
            </button>
          </form>

          {search ? (
            <div className="results" aria-live="polite">
              <div className="results-meta">
                <span>{search.total.toLocaleString()} indexed matches · showing {search.returned}</span>
                <span>Retrieved {new Date(search.provenance.retrieved_at).toLocaleString()}</span>
              </div>
              {search.articles.map((article) => (
                <article className="paper" key={article.pmid}>
                  <div className="paper-id">PMID<br /><b>{article.pmid}</b></div>
                  <div>
                    <h3>{article.title}</h3>
                    <p>{article.authors.slice(0, 4).join(", ") || "Authors unavailable"}</p>
                    <div className="paper-meta">
                      <span>{article.journal ?? "Journal unavailable"}</span>
                      <span>{article.publication_date ?? "Date unavailable"}</span>
                      <span>{article.doi ? `DOI ${article.doi}` : "DOI unavailable"}</span>
                    </div>
                  </div>
                  <span className="access-badge">metadata only</span>
                </article>
              ))}
              <p className="provenance">Source hash: {search.provenance.source_hash.slice(0, 28)}… · External metadata is treated as untrusted input.</p>
            </div>
          ) : (
            <div className="empty-state">
              <SearchIcon />
              <p>Run a search to retrieve traceable publication metadata.</p>
              <span>No evidence claims have been extracted.</span>
            </div>
          )}
        </section>

        <footer>
          <span>NeuroGenesis AI · research software prototype</span>
          <span>Not for diagnosis or clinical decision-making</span>
        </footer>
      </main>
    </div>
  );
}
