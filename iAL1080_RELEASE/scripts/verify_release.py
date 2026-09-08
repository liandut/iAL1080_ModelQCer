from pathlib import Path
import hashlib
try:
    import cobra
except ImportError:
    cobra=None
root=Path(__file__).resolve().parents[1]
model=root/'model/iAL1080.xml'
sha=hashlib.sha256(model.read_bytes()).hexdigest()
assert sha=='42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d'
if cobra is not None:
    m=cobra.io.read_sbml_model(str(model));assert (len(m.genes),len(m.reactions),len(m.metabolites))==(1080,2377,1662)
print('PASS',sha)
