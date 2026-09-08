from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'source_data' / 'supplementary'
OUT = ROOT / 'figures' / 'supplementary'
OUT.mkdir(exist_ok=True)

# S3A: growth-PHB trade-off across GAM values.
g = pd.read_csv(DATA / 'Figure_S3A_source.tsv', sep='\t')
plt.figure(figsize=(7.2, 5.2))
for gam, part in g.groupby('GAM'):
    label = '53.95 (baseline)' if np.isclose(gam, 53.95) else f'{gam:g}'
    plt.plot(part['minimum_growth_rate_h_1'], part['PHB_mass_rate_g_gDW_h'],
             marker='o', markersize=3, linewidth=1.5, label=label)
plt.xlabel('Minimum growth-rate constraint (h$^{-1}$)')
plt.ylabel('Maximum PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)')
plt.title('GAM sensitivity of the growth-PHB trade-off')
plt.legend(title='GAM (mmol ATP gDW$^{-1}$)', fontsize=8, title_fontsize=8)
plt.tight_layout()
plt.savefig(OUT / 'Figure_S3A_reproduced.png', dpi=300)
plt.close()

# S3B: O2-PHB response across GAM values.
o2 = pd.read_csv(DATA / 'Figure_S3B_source.tsv', sep='\t')
plt.figure(figsize=(7.2, 5.2))
for gam, part in o2.groupby('GAM'):
    label = '53.95 (baseline)' if np.isclose(gam, 53.95) else f'{gam:g}'
    plt.plot(part['O2_fraction_of_baseline_qref'], part['PHB_mass_rate_g_gDW_h'],
             linewidth=1.5, label=label)
plt.xlabel('O$_2$ uptake capacity / baseline $q_{O2,ref}$')
plt.ylabel('Maximum PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)')
plt.title('GAM sensitivity of the O$_2$-PHB response')
plt.legend(title='GAM (mmol ATP gDW$^{-1}$)', fontsize=8, title_fontsize=8)
plt.tight_layout()
plt.savefig(OUT / 'Figure_S3B_reproduced.png', dpi=300)
plt.close()

# S3C: key FSEOF slopes across GAM values.
fseof = pd.read_csv(DATA / 'Figure_S3C_source.tsv', sep='\t')
plt.figure(figsize=(7.0, 4.8))
for rid, label in {'R_ACACT1r': 'ACACT1r/PhaA', 'R_PDH': 'PDH'}.items():
    part = fseof[fseof['reaction_id'] == rid]
    plt.plot(part['GAM'], part['slope'], marker='o', linewidth=1.6, label=label)
plt.xlabel('GAM (mmol ATP gDW$^{-1}$)')
plt.ylabel('FSEOF slope')
plt.title('GAM sensitivity of key FSEOF candidates')
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'Figure_S3C_reproduced.png', dpi=300)
plt.close()
