"""Run portable panel-wise plotting scripts for Supplementary Figures S1-S4."""
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
for script in [
    'plot_Figure_S1_panels.py',
    'plot_Figure_S2_panels.py',
    'plot_Figure_S3_panels.py',
    'plot_Figure_S4_panels.py',
]:
    runpy.run_path(HERE / script, run_name='__main__')
print('Finished plotting Supplementary Figures S1-S4 panels.')
