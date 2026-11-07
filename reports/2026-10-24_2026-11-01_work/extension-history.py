import pathlib,json,urllib.request,re,html,concurrent.futures,time
P=pathlib.Path(__file__).resolve().parent
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
D=json.loads((P/'extension-search.json').read_text(encoding='utf8'));U={x['id']:x for x in D['papers']+json.loads((P/'extension-advanced-candidates.json').read_text(encoding='utf8'))}
U.update({x['id']:x for x in json.loads((P/'extension-advanced-applications-candidates.json').read_text(encoding='utf8'))})
def fetch(ident):
 url='https://arxiv.org/abs/'+ident
 try:
  b=urllib.request.urlopen(url,timeout=25).read();(P/('extension-abs-'+ident+'.html')).write_bytes(b);s=b.decode('utf8');seg=s[s.find('<div class="submission-history">'):];seg=seg[:seg.find('</div>')];plain=html.unescape(re.sub('<[^>]*>',' ',seg));plain=re.sub(r'\s+',' ',plain).strip();hist=[]
  for v,dt in re.findall(r'\[v(\d+)\]\s*([A-Za-z]{3},\s*\d+\s+[A-Za-z]{3}\s+\d{4}\s+\d\d:\d\d:\d\d\s+UTC)',plain):
   hist.append({'version':int(v),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.strptime(dt,'%a, %d %b %Y %H:%M:%S UTC'))})
  return ident,{'url':url,'retrieved_at':now(),'history_raw':plain,'version_history':hist,'history_verified':bool(hist),'raw_path':'extension-abs-'+ident+'.html'}
 except Exception as ex:return ident,{'url':url,'retrieved_at':now(),'history_verified':False,'failure':str(ex)}
out=json.loads((P/'extension-official-histories.json').read_text(encoding='utf8')) if (P/'extension-official-histories.json').exists() else {}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for ident,d in pool.map(fetch,[ident for ident in U if ident not in out or not out[ident].get('history_verified')]):
  out[ident]=d;(P/'extension-official-histories.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('histories',len(out),'verified',sum(x['history_verified'] for x in out.values()))
