# Contributing to NeuroGenesis AI

Thank you for your interest in contributing to NeuroGenesis AI. We are building an evidence-first, autonomous, and assisted research platform for neurodegenerative disease research.

To maintain the highest standards of scientific rigor, software engineering, and reproducible computation, all contributors are expected to adhere to the guidelines set forth in this document.

---

## Table of Contents
1. [Code of Conduct](#1-code-of-conduct)
2. [Branching Strategy & Rules](#2-branching-strategy--rules)
3. [Commit Message Conventions](#3-commit-message-conventions)
4. [Pull Request (PR) Requirements](#4-pull-request-pr-requirements)
5. [Scientific Integrity & Evidence Rules](#5-scientific-integrity--evidence-rules)
6. [Development Workflow & Standards](#6-development-workflow--standards)
7. [Security & Responsible Disclosure](#7-security--responsible-disclosure)

---

## 1. Code of Conduct

All contributors and maintainers must abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report violations to **security@neurogenesis.ai**.

---

## 2. Branching Strategy & Rules

We adhere to a modernized trunk-based branching workflow optimized for high-velocity teams with continuous integration gates.

### 2.1 Branch Topology

```text
main (production-ready, protected, immutable history)
  │
  ├── feat/lit-pubmed-connector-v1
  ├── fix/claim-extractor-offset-bug
  ├── research/exp-ad-001-baseline
  └── chore/upgrade-pydantic-v2
```

- **`main`**: The canonical production branch. Direct pushes and force pushes are strictly prohibited. Every commit in `main` must pass all CI gates and represent a stable checkpoint.
- **`develop`** *(optional during sprint integration)*: Integration branch for larger releases.

### 2.2 Branch Naming Conventions
All branches must follow lowercase hyphen-separated formatting with designated prefixes:

| Prefix | Purpose | Example |
|---|---|---|
| `feat/` | New platform capability or scientific agent feature | `feat/molstar-viewer-adapter` |
| `fix/` | Bug fix in code, pipeline, or UI | `fix/dbsnp-rsid-normalization` |
| `research/` | Scientific experiments, benchmark preregistrations | `research/exp-ad-002-temporal-split` |
| `perf/` | Performance optimizations (speed, memory, tokens) | `perf/vector-search-hnsw-indexing` |
| `refactor/` | Structural code modifications without functional change | `refactor/agent-tool-orchestrator` |
| `test/` | Adding missing unit, integration, or scientific tests | `test/contradiction-nli-benchmark` |
| `docs/` | Architecture, specification, or ADR updates | `docs/adr-004-postgresql-pgvector` |
| `chore/` | Tooling, dependencies, or CI workflow updates | `chore/docker-compose-minio-update` |

### 2.3 Branch Lifecycle Rules
1. Branch from the latest `main`.
2. Keep branches short-lived (aim for < 3 business days from creation to merge).
3. Regularly rebase against `origin/main` (`git fetch origin && git rebase origin/main`).
4. Delete feature branches immediately upon merging.

---

## 3. Commit Message Conventions

We enforce [Conventional Commits v1.0.0](https://www.conventionalcommits.org/). Every commit message is validated in CI.

### 3.1 Format
```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### 3.2 Types
- `feat`: A new feature for researchers or developers.
- `fix`: A bug fix.
- `bio`: Biomedical data changes (ontologies, schemas, normalizers).
- `hyp`: Hypothesis generation or scoring logic.
- `perf`: Performance improvements.
- `refactor`: Code changes that neither fix bugs nor add features.
- `test`: Adding or correcting tests.
- `docs`: Documentation only changes.
- `ci`: CI configuration and scripts.
- `chore`: Maintenance tasks and dependency bumps.

### 3.3 Commit Rules
- Use imperative, present tense: `"add pubmed parser"`, not `"added"` or `"adds"`.
- Do not capitalize the first letter of the description.
- No period (`.`) at the end of the subject line.
- Reference issue IDs in footer: `Closes #42` or `Fixes #18`.

**Example:**
```text
feat(connectors): add rate-limiting and retry logic to pubmed e-utilities

Implements token bucket rate limiting (max 10 requests/sec with API key, 
3 requests/sec without) and exponential backoff with jitter on HTTP 429/5xx.

Closes #14
```

---

## 4. Pull Request (PR) Requirements

All changes reach `main` exclusively through Pull Requests.

### 4.1 PR Checklist
Before submitting a PR, verify:
- [ ] Code passes all linting (`ruff`, `eslint`, `biome`).
- [ ] Code passes static type checking (`mypy --strict`, `tsc --noEmit`).
- [ ] All unit, integration, and scientific regression tests pass (`pytest`, `npm test`).
- [ ] Test coverage does not regress (minimum target: 85% for core libraries).
- [ ] Scientific claims and algorithms adhere to Section 5.
- [ ] Documentation and ADRs updated if architecture changed.
- [ ] PR title adheres to Conventional Commits.
- [ ] PR description follows `.github/PULL_REQUEST_TEMPLATE.md`.

### 4.2 Review and Merge Policy
1. **Approvals**: At least **one code review approval** from a code owner; for changes touching scientific inference or evaluation logic, approval from a scientific advisor/bioinformatician is required.
2. **Merge Method**: **Squash and Merge** or **Rebase and Merge** to maintain a clean, linear git history. Merge commits are disabled.
3. **Branch Protection**: Merging is blocked until all mandatory CI checks are green.

---

## 5. Scientific Integrity & Evidence Rules

Because NeuroGenesis AI operates in biomedical research, strict engineering rules apply to scientific modules:

1. **Zero Hallucinated Attribution**: Code must NEVER fabricate DOIs, PMIDs, author names, sample sizes, or p-values. Any LLM output producing citations must be cross-verified against indexed databases before being committed to the knowledge base.
2. **Association vs. Causation**: Graph edges and agent claims must be explicitly tagged as `observational`, `experimental`, or `causally_inferred`. Never assign directional causality without defensible causal inference structures (DAGs, Mendelian randomization).
3. **Temporal Isolation (No Future Leakage)**: Any backtesting or historical benchmark code (such as EXP-AD-002) must strictly enforce temporal cutoff boundaries on literature corpora, embeddings, and feature matrices.
4. **Reproducibility**: All computational experiments must persist random seeds, dependency lockfiles, dataset hashes, and container environments.

---

## 6. Development Workflow & Standards

### 6.1 Python Stack (`apps/api`, `packages/scientific-core`, `workers/*`)
- Python 3.11+
- Package management & environments: `uv` or `poetry` with pinned lockfiles
- Linter & Formatter: `ruff` (enforcing PEP 8, flake8, isort)
- Type Checker: `mypy --strict`
- Testing: `pytest` with `pytest-asyncio`, `pytest-cov`, and `hypothesis` for property-based testing

### 6.2 TypeScript Stack (`apps/web`, `packages/contracts`, `packages/visualization`)
- Node.js 20+ LTS / pnpm 9+
- Monorepo tooling: Turborepo / pnpm workspaces
- Framework: Next.js 15+ (App Router)
- Linter & Formatter: ESLint + Prettier or Biome
- Type Checker: `tsc --noEmit`
- Testing: Vitest + Playwright for end-to-end testing

### 6.3 Local Verification Commands
Before opening a PR, run locally:
```bash
# Python verification
ruff check . && ruff format --check . && mypy
pytest tests/unit tests/scientific --cov

# TypeScript verification
pnpm lint
pnpm typecheck
pnpm test
```

---

## 7. Security & Responsible Disclosure

Please review our [Security Policy](SECURITY.md). Do not disclose security vulnerabilities, prompt injection exploits, or private clinical dataset exposures publicly. Report them privately to **security@neurogenesis.ai**.
