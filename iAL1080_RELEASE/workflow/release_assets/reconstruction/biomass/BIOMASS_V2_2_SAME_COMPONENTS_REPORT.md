# Biomass V2.2 same-components report

## Core result
- Biomass metabolite set identical to old `R_Growth`: YES
- Added biomass metabolites: none
- Removed biomass metabolites: none
- Protein: 0.550000000000 g/gDW
- RNA: 0.210000000000 g/gDW
- DNA: 0.031000000000 g/gDW
- Residual: 0.209000000000 g/gDW
- Total structural mass: 1.000000000000 g/gDW
- Net biomass MW: 1.000000000000 g/gDW
- GAM retained: 53.950000 mmol ATP/gDW
- Residual scaling factor: 1.023732994277

## Growth in current glucose minimal/default medium
- Old biomass: 0.323628128497 h^-1
- New V2.2 biomass: 0.328443617112 h^-1
- Change: 1.4880%

## Verification
- SBML reload: PASS
- `R_PHB_SYN_HB`: preserved
- `R_DM_phb_c`: preserved
- Objective remains `R_Growth`
- Source SHA256: 9d5bb822f3a023e318ecc260fd16c87438cbd10bbebe6425f2418d56eb89570e
- Output SHA256: 9caecc9a6205ef69a426a4f3ae8dc70d8f1b7f84fde782cc278c29a33fea4761

## Active uptake bounds
- R_EX_ca2_e: LB=-1000, UB=1000
- R_EX_cl_e: LB=-1000, UB=1000
- R_EX_co2_e: LB=-1000, UB=1000
- R_EX_cobalt2_e: LB=-1000, UB=1000
- R_EX_cu2_e: LB=-1000, UB=1000
- R_EX_fe2_e: LB=-1000, UB=1000
- R_EX_fe3_e: LB=-1000, UB=1000
- R_EX_glc__D_e: LB=-10, UB=1000
- R_EX_h2o_e: LB=-1000, UB=1000
- R_EX_h_e: LB=-1000, UB=1000
- R_EX_k_e: LB=-1000, UB=1000
- R_EX_mg2_e: LB=-1000, UB=1000
- R_EX_mn2_e: LB=-1000, UB=1000
- R_EX_mobd_e: LB=-1000, UB=1000
- R_EX_na1_e: LB=-1000, UB=1000
- R_EX_nh4_e: LB=-1000, UB=1000
- R_EX_ni2_e: LB=-1000, UB=1000
- R_EX_o2_e: LB=-1000, UB=1000
- R_EX_pi_e: LB=-1000, UB=1000
- R_EX_sel_e: LB=-1000, UB=1000
- R_EX_slnt_e: LB=-1000, UB=1000
- R_EX_so4_e: LB=-1000, UB=1000
- R_EX_zn2_e: LB=-1000, UB=1000
