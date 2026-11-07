import pathlib,concurrent.futures
from importlib.machinery import SourceFileLoader
P=pathlib.Path(__file__).resolve().parent
M=SourceFileLoader('extension_advanced',str(P/'extension-advanced.py')).load_module()
jobs=[('C-thermal-SLAM',['thermal','SLAM'],'AND'),('C-underwater-mapping',['underwater','mapping'],'AND'),('C-endoscopic-localization',['endoscopic','localization'],'AND'),('C-neural-radiance-robot',['"neural radiance"','robot'],'AND')]
manifest=[];rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for m,r in pool.map(M.fetch,jobs):
  manifest.append(m);rows+=r;M.save('extension-advanced-applications-manifest.json',manifest);M.save('extension-advanced-applications-candidates.json',rows);print(m['name'],m['total'],m['fetched'],m['exhausted'],m.get('failure'),flush=True)
