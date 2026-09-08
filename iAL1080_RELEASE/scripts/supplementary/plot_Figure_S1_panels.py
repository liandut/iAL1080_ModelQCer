from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'source_data' / 'S1_FINAL_SOURCE.tsv'
OUT = ROOT / 'figures' / 'supplementary'
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, sep='\t')
series = [
    ('normalized_N_availability', 'Normalized N availability', 'Figure_S1A_reproduced.png'),
    ('model_growth_capacity_h-1', 'Growth capacity (h$^{-1}$)', 'Figure_S1B_reproduced.png'),
    ('model_PHB_capacity_g_gDW_h', 'PHB capacity (g gDW$^{-1}$ h$^{-1}$)', 'Figure_S1C_reproduced.png'),
]
for col, ylabel, filename in series:
    plt.figure(figsize=(6.5, 3.8))
    plt.plot(df['time_h'], df[col], linewidth=1.6)
    plt.axvline(30, linestyle='--')
    plt.xlabel('Time (h)')
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=300)
    plt.close()
