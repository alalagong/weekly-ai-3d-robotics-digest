import pathlib,json,urllib.request,re,html,concurrent.futures,time
P=pathlib.Path(__file__).resolve().parent
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
S=json.loads((P/'core-selected-raw.json').read_text(encoding='utf8'))
def fetch(q):
 ident=q['id'];url='https://arxiv.org/abs/'+ident
 try:
  cached=list(P.glob('*abs-'+ident+'.html'))
  if cached: raw=cached[0];b=raw.read_bytes()
  else:
   b=urllib.request.urlopen(url,timeout=20).read();raw=P/('core-abs-'+ident+'.html');raw.write_bytes(b)
  s=b.decode('utf8');seg=s[s.find('<div class="submission-history">'):];seg=seg[:seg.find('</div>')];plain=html.unescape(re.sub('<[^>]*>',' ',seg));plain=re.sub(r'\s+',' ',plain).strip();hist=[]
  for v,dt in re.findall(r'\[v(\d+)\]\s*([A-Za-z]{3},\s*\d+\s+[A-Za-z]{3}\s+\d{4}\s+\d\d:\d\d:\d\d\s+UTC)',plain):
   hist.append({'version':int(v),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.strptime(dt,'%a, %d %b %Y %H:%M:%S UTC'))})
  return ident,{'url':url,'retrieved_at':now(),'history_raw':plain,'version_history':hist,'history_verified':bool(hist),'raw_path':raw.name,'cached':bool(cached)}
 except Exception as ex:return ident,{'url':url,'retrieved_at':now(),'history_verified':False,'failure':str(ex)}
out={}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for ident,d in pool.map(fetch,S):
  out[ident]=d;(P/'core-official-histories.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('histories',len(out),'verified',sum(x['history_verified'] for x in out.values()))
