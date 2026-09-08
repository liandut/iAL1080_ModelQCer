# Reconstruction framework release note

- The framework contains 16 ordered notebooks and reusable modules covering the registered CarveMe draft through controlled model release.
- Notebooks 00–09 implement automated preparation and stop at the formal manual-review gate.
- Notebooks 10–15 require explicit expert decisions before controlled reintegration, regression/QC, phenotype testing, and release export.
- The bundled draft has SHA256 `913c075da67845ff638fc054ce06e9b8db34a3586a03e429f73a6cb295b604c1`.
- The canonical final model is outside this workflow folder at `../../model/iAL1080.xml`, SHA256 `42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d`.
- Existing biological decisions are represented as frozen evidence/review inputs; this public packaging step did not change reaction chemistry, GPRs, bounds, objective, Biomass coefficients, or gap-fill decisions.
- No donor/universal GPR transfer is permitted, and candidate generation never equals automatic approval.
- Notebook outputs were cleared for a clean public repository; compiled caches, local environment reports, and duplicate generated candidate XML files were excluded.
- The canonical human-review interface is the TSV file; the optional historical XLSX was excluded because it contained a private machine path.
- Configuration paths are repository-relative and contain no user-specific machine path.
- Status: `PUBLIC_WORKFLOW_PACKAGE_READY — MANUAL_REVIEW_REQUIRED_BEFORE_REINTEGRATION`.
