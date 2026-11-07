import json,pathlib,urllib.request,time,concurrent.futures
P=pathlib.Path(__file__).resolve().parent
ids=['2610.37602','2610.36853','2610.36454']
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
hist=json.loads((P/'main-official-histories.json').read_text(encoding='utf8'))
progress={'run_at':'2026-11-01T14:59:32Z','started_at':now(),'status':'acquiring_full_text','papers':[]}
(P/'core-deep-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf8')
def fetch(i):
 d={'id':i,'version':1,'locked_url':'https://arxiv.org/html/'+i+'v1','attempts':[],'read_sections':[]}
 for kind in ['html','pdf']:
  url='https://arxiv.org/'+kind+'/'+i+'v1';path=P/('core-deep-'+i+'v1.'+kind)
  try:
   b=urllib.request.urlopen(url,timeout=30).read();path.write_bytes(b)
   d['attempts'].append({'url':url,'retrieved_at':now(),'bytes':len(b),'path':path.name,'status':'success'})
  except Exception as ex:d['attempts'].append({'url':url,'retrieved_at':now(),'status':'failed','error':str(ex)})
 return d
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for d in ex.map(fetch,ids):
  progress['papers'].append(d);(P/'core-deep-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(d))
