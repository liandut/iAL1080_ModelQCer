from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'source_data' / 'supplementary'
OUT = ROOT / 'figures' / 'supplementary'
OUT.mkdir(exist_ok=True)

# S4A: display only informative nonzero rows.
# GLCDpp and gluconate export are intentionally omitted from the heatmap because
# they were numerical zero across all three plotted states. Their full values are
# retained in Figure_S4A_full_flux_source.tsv and Figure_S4A_gluconate_FVA.tsv.
flux = pd.read_csv(DATA / 'Figure_S4A_displayed_fluxes.tsv', sep='\t')
order = [
    'R_EX_o2_e', 'R_Growth', 'R_PDH', 'R_CS', 'R_ACACT1r',
    'R_PHB_SYN_HB', 'R_ATPS4rpp', 'R_CYO1_KT'
]
labels = {
    'R_EX_o2_e': 'O$_2$ uptake',
    'R_Growth': 'Biomass',
    'R_PDH': 'PDH',
    'R_CS': 'Citrate synthase',
    'R_ACACT1r': 'ACACT1r/PhaA',
    'R_PHB_SYN_HB': 'PHB synthase',
    'R_ATPS4rpp': 'ATP synthase',
    'R_CYO1_KT': 'Respiratory ETC',
}
states = ['Low O2', 'PHB-optimal O2', 'High O2']
mat = (flux.pivot(index='reaction_id', columns='state', values='reported_flux')
       .reindex(index=order, columns=states))
scale = mat.abs().max(axis=1).replace(0, 1)
norm = mat.div(scale, axis=0)

plt.figure(figsize=(7.2, 5.3))
im = plt.imshow(norm.values, aspect='auto')
plt.xticks(range(len(states)), ['Low O$_2$', 'PHB-optimal O$_2$', 'High O$_2$'])
plt.yticks(range(len(order)), [labels[r] for r in order])
plt.title('Selected parsimonious fluxes across O$_2$ states')
plt.colorbar(im, label='Flux normalized within each reaction')
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        value = mat.iloc[i, j]
        text = '0' if abs(value) < 5e-6 else f'{value:.3f}'
        plt.text(j, i, text, ha='center', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(OUT / 'Figure_S4A_reproduced.png', dpi=300)
plt.close()

# S4B: relative-growth normalization versus fixed absolute growth floor.
normcheck = pd.read_csv(DATA / 'Figure_S4B_source.tsv', sep='\t')
plt.figure(figsize=(7.2, 5.0))
plt.plot(normcheck['O2_fraction'], normcheck['PHB_relative_protocol_g_gDW_h'],
         marker='o', markersize=3, linewidth=1.6,
         label='Relative growth: 0.1 x condition-specific mu_max')
plt.plot(normcheck['O2_fraction'], normcheck['PHB_fixed_growth_g_gDW_h'],
         marker='s', markersize=3, linewidth=1.6,
         label='Fixed absolute growth floor')
plt.xlabel('O$_2$ uptake capacity / baseline $q_{O2,ref}$')
plt.ylabel('Maximum PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)')
plt.title('Effect of growth normalization on the O$_2$-PHB response')
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(OUT / 'Figure_S4B_reproduced.png', dpi=300)
plt.close()
