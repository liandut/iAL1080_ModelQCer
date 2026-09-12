# Methods and assumptions

## Model and carbon uptake

- Model: repository-relative `../../model/iAL1080.xml`.
- Model SHA256: `42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d`.
- Glucose uptake magnitude: `qglc = 2.8 mmol gDW^-1 h^-1`.
- Derived reference ammonium uptake: `qN,ref = 3.014163714704978 mmol gDW^-1 h^-1`.
- Derived reference oxygen uptake: `qO2,ref = 4.784194697803019 mmol gDW^-1 h^-1`.

The full-precision reference uptakes were derived from the SHA-identified model by minimizing the corresponding uptake magnitude while maintaining at least 99% of the glucose-constrained maximum growth rate.

## Phase-plane calculations

For every normalized N/O2 coordinate, the condition-specific maximum growth rate (`mu_max`) was obtained first. PHB storage capacity was then calculated by fixing growth at `alpha = 0.1` times that condition-specific `mu_max` and maximizing `DM_phb_c`. The displayed phase plane contains 18 normalized ammonium constraints and 22 normalized oxygen constraints (396 complete coordinates).

The four predefined states are:

| State | N fraction | O2 fraction |
|---|---:|---:|
| Control | 1.0 | 1.0 |
| N-limited | 0.5 | 1.0 |
| O2-limited | 1.0 | 0.25 |
| N + low O2 | 0.5 | 0.25 |

The combined coordinate is a manuscript scenario definition. It is not a direct conversion from dissolved-oxygen percentage and is not interpreted as a global interaction optimum.

## FVA state definitions

- **Growth-dominant control:** `N = 1.0 qN,ref`, `O2 = 1.0 qO2,ref`, with growth constrained to at least 99% of the control maximum.
- **Defined dual-limitation storage state:** `N = 0.5 qN,ref`, `O2 = 0.25 qO2,ref`; growth fixed at 10% of the condition-specific maximum; PHB demand constrained to at least 99% of its maximum under that growth constraint.

The main FVA panel contains `PHB_SYN_HB`, `CS`, `MDH`, `CYO1_KT`, `CYTCAA3pp`, `ATPS4rpp`, and `EX_co2_e`. An upward or downward designation is applied only when the two feasible intervals do not overlap at a numerical tolerance of `1e-7` in the original analysis. Each interval is normalized only for within-reaction display; the source table retains the unscaled flux bounds.

`PDH` and `ACACT1r` are provided in `HB_FVA_FSEOF_CROSSCHECK.csv`. Their control and storage intervals overlap, so neither is interpreted as a required FVA shift.

## Scope of inference

The phase planes and FVA results describe feasible steady-state model behavior under imposed constraints. They do not constitute direct flux measurement, time-resolved simulation, or independent discovery of a biological mechanism.
