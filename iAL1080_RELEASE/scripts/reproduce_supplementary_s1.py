from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
d=pd.read_csv(root/'source_data/S1_FINAL_SOURCE.tsv',sep='\t')
fig,ax=plt.subplots(3,1,figsize=(6.7,6.7),sharex=True,constrained_layout=True)
cols=['normalized_N_availability','model_growth_capacity_h-1','model_PHB_capacity_g_gDW_h']
labels=['Normalized N availability','Growth capacity (h$^{-1}$)','PHB capacity (g gDW$^{-1}$ h$^{-1}$)']
for a,c,l in zip(ax,cols,labels):a.plot(d.time_h,d[c]);a.axvline(30,ls='--',color='0.4');a.set_ylabel(l);a.spines[['top','right']].set_visible(False)
ax[-1].set_xlabel('Time (h)');fig.savefig(root/'figures/PHB_SUPP_FIGURE_S1_REPRODUCED.png',dpi=600,bbox_inches='tight')
