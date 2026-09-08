# Human review interface

Human review is a formal workflow stage. It is never interpreted from missing values.

Edit only `manual_decision`, `manual_value`, and `manual_notes` (plus reviewer/date when available).

Allowed decisions:

- `APPROVE`: accept the proposed candidate state.
- `REJECT`: retain the current state.
- `REVISE`: apply the explicit replacement in `manual_value`.
- `DEFER`: do not apply; retain as an open issue.
- `UNRESOLVED`: evidence is insufficient; do not apply.

For GPR revision, `manual_value` is the final GPR. For direction revision, use `lower_bound,upper_bound`. For reaction status, use `KEEP` or `REMOVE`. For biomass, use `APPROVE_AS_IS` or an explicit coefficient. Blank decisions are never treated as approval.

`HUMAN_REVIEW_PACKAGE.tsv` is the canonical machine-readable interface. The workbook is the human-facing view; review IDs must remain unchanged.
