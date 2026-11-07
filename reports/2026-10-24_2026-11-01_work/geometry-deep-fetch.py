import json, pathlib, re, urllib.request, concurrent.futures, datetime
from lxml import html
def clean(el): return ' '.join(el.text_content().split())
root=pathlib.Path(__file__).parent
ids=['2610.37000','2610.35806','2610.36150','2605.23889']
progress={'run_at':'2026-11-01T14:59:32Z','status':'fetching','papers':[]}
for aid in ids:
 f=next(iter(root.glob('*abs-'+aid+'.html')),None)
 soup=html.fromstring(f.read_bytes()) if f else None
 hist=soup.xpath('//*[contains(@class,"submission-history")]') if soup is not None else []
 txt=clean(hist[0]) if hist else ''
 versions=re.findall(r'\[v(\d+)\]',txt)
 version=max(map(int,versions)) if versions else None
 progress['papers'].append({'id':aid,'version':version,'history':txt,'history_path':str(f),'reading_level':'metadata','status':'fetch_pending'})
(root/'geometry-deep.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
def fetch(p):
 aid=p['id']; v=p['version'];url=f'https://arxiv.org/html/{aid}v{v}'
 try:
  raw=urllib.request.urlopen(url,timeout=25).read()
  dest=root/f'geometry-deep-{aid}v{v}.html';dest.write_bytes(raw)
  soup=html.fromstring(raw)
  for bad in soup.xpath('//nav|//footer|//script|//style'):bad.drop_tree()
  text=clean(soup)
  (root/f'geometry-deep-{aid}v{v}.txt').write_text(text,encoding='utf-8')
  headings=[clean(h) for h in soup.xpath('//h1|//h2|//h3|//h4|//h5')]
  figures=[{'id':f.get('id'),'caption':clean(f),'imgs':[dict(i.attrib) for i in f.xpath('.//img')]} for f in soup.xpath('//figure')]
  meta={'id':aid,'version':v,'url':url,'path':str(dest),'char_count':len(text),'headings':headings,'figures':figures,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  (root/f'geometry-deep-{aid}v{v}-structure.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
  return meta
 except Exception as e:return {'id':aid,'version':v,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for result in ex.map(fetch,progress['papers']): print(json.dumps(result,ensure_ascii=False))
