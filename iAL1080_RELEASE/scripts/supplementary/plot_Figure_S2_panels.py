from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'source_data' / 'HB_N_SCAN_QGLC2p8_ROUND2.tsv'
OUT = ROOT / 'figures' / 'supplementary'
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, sep='\t')

# Panel A: condition-specific maximum growth capacity.
growth = (df[['N_fraction_of_qref', 'condition_max_growth_h-1']]
          .drop_duplicates()
          .sort_values('N_fraction_of_qref'))
plt.figure(figsize=(6.2, 4.2))
plt.plot(growth['N_fraction_of_qref'], growth['condition_max_growth_h-1'], marker='o', markersize=3)
plt.xlabel('Normalized ammonium availability (qN / qN,ref)')
plt.ylabel('Maximum growth capacity (h$^{-1}$)')
plt.title('Figure S2A: nitrogen-dependent growth capacity')
plt.tight_layout()
plt.savefig(OUT / 'Figure_S2A_reproduced.png', dpi=300)
plt.close()

# Panel B: PHB capacity at three residual-growth fractions.
plt.figure(figsize=(6.2, 4.2))
for alpha, part in df.groupby('residual_growth_fraction'):
    part = part.sort_values('N_fraction_of_qref')
    plt.plot(part['N_fraction_of_qref'], part['PHB_mass_rate_g_gDW_h'],
             marker='o', markersize=3, label=f'alpha = {alpha:g}')
plt.xlabel('Normalized ammonium availability (qN / qN,ref)')
plt.ylabel('Maximum PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)')
plt.title('Figure S2B: nitrogen and residual-growth sensitivity')
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'Figure_S2B_reproduced.png', dpi=300)
plt.close()
