import json,pathlib,re,sys
from lxml import html
sys.stdout.reconfigure(encoding='utf-8');P=pathlib.Path(__file__).parent
out=[]
patterns=['Co-VGGT','RayTun3R','G-ray','OmniPoint','HTTM','Co-Me','QuantVGGT','QVGGT','LongStream','Lingbot','LoGeR','ReVar3R']
for f in P.glob('geometry-deep-*v*.html'):
 d=html.fromstring(f.read_bytes())
 for b in d.xpath('//*[contains(@class,"ltx_bibitem")]'):
  t=' '.join(b.text_content().split())
  if any(p.lower() in t.lower() for p in patterns) or ('2610.35806' in f.name and t.startswith('[28]')) or ('2610.37000' in f.name and t.startswith('[7]')):out.append({'source_paper':f.stem,'reference_id':b.get('id'),'text':t,'urls':b.xpath('.//a/@href')})
(P/'geometry-deep-cross-references.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for o in out: print(json.dumps(o,ensure_ascii=False))
