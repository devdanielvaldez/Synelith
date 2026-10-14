## Description

<!-- Provide a clear and concise summary of the changes introduced in this PR. -->

Closes #<!-- Issue Number -->

---

## Type of Change

- [ ] `feat`: New platform feature or capability
- [ ] `fix`: Bug fix
- [ ] `bio`: Bioinformatics, ontology, or data schema update
- [ ] `hyp`: Hypothesis generation or scoring algorithm modification
- [ ] `perf`: Performance or memory optimization
- [ ] `refactor`: Code refactoring without behavioral modification
- [ ] `test`: New or updated tests
- [ ] `docs`: Documentation, ADR, or specification updates
- [ ] `infra`: Infrastructure, Docker, or CI/CD workflow changes

---

## Scientific Rigor & Evidence Checklist

*(Required for any PR modifying data ingestion, knowledge graph, or hypothesis generation)*

- [ ] **No Hallucinated Citations:** All sources, PMIDs, DOIs, and claims resolve to authentic publications.
- [ ] **Epistemological Integrity:** New graph edges or claims explicitly distinguish between `observational`, `experimental`, and `causally_inferred` relationships.
- [ ] **Temporal Isolation:** No future data leakage introduced into temporal benchmarks or evaluation splits (EXP-AD-002 compliant).
- [ ] **Reproducibility:** Seed configurations, container specifications, and dataset version hashes are recorded.

---

## Code Quality & Engineering Checklist

- [ ] My code adheres to the project's style guidelines (`ruff`, `biome` / `eslint`).
- [ ] I have executed static type checking (`mypy --strict`, `tsc --noEmit`) with zero errors.
- [ ] I have written unit and/or integration tests covering the new functionality.
- [ ] All automated tests pass locally (`pytest`, `pnpm test`).
- [ ] No sensitive credentials, API keys, or private patient datasets are exposed or committed.
- [ ] Documentation and architectural decision records (ADRs) have been updated where appropriate.
- [ ] PR title adheres to [Conventional Commits](https://www.conventionalcommits.org/).

---

## Verification & Screenshots

<!-- Provide CLI output, test execution summaries, or UI screenshots demonstrating functionality. -->
