---
name: reproducible-biomedical-experiments
description: Plan, implement, run, or audit computational biomedical experiments and hypothesis evaluations for NeuroGenesis AI, including temporal benchmarks and multi-omic analyses. Not for clinical validation or treatment decisions.
---

# Reproducible Biomedical Experiments

Turn a hypothesis into a falsifiable, auditable computational protocol and report results at their actual evidence level.

## Protocol

1. State the question, hypothesis, biological scope, primary endpoint, alternative explanations, and falsification criteria before inspecting final evaluation results.
2. Pin eligible sources, datasets, ontology versions, preprocessing, inclusion/exclusion rules, covariates, statistical tests, multiple-testing correction, metrics, and success thresholds.
3. Define baselines, negative controls, sensitivity analyses, and an independent holdout or replication cohort where feasible. Justify power or sample-size constraints.
4. For historical evaluation, enforce the cutoff across documents, metadata, embeddings, pretrained artifacts, features, and labels. Audit rather than assume temporal isolation.
5. Separate train, validation, and test decisions. Do not tune model choices, scoring weights, or thresholds on the final test set.
6. Record code hash, parameters, seeds, input hashes and versions, model identifiers, dependency lockfile or container image, runtime environment, and generated artifact hashes.
7. Report effect sizes and uncertainty alongside significance tests. Check assumptions, batch effects, missingness, confounding, calibration, and cohort dependence as applicable.
8. Re-execute from the recorded environment or provide a precise reason reproducibility could not be verified.

## Interpretation rules

- Label outputs as computational results until independently replicated; replication is still not wet-lab or clinical validation.
- Distinguish exploratory from confirmatory analysis and disclose deviations from the preregistered plan.
- Report negative and inconclusive results. Do not select only favorable metrics or cohorts.
- Never claim therapeutic efficacy, diagnosis, causality, novelty, or validated discovery beyond what the design establishes.
- Require qualified human review before external dissemination of preliminary scientific results.

## Deliverables

Produce a versioned protocol, machine-readable run manifest, logs, metrics, plots or tables with provenance, a limitations and counter-evidence section, and an epistemic status. Keep heavy or restricted artifacts outside Git and reference them through approved versioned storage.

