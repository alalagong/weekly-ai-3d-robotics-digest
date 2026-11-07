import pathlib,json,urllib.request,re,html,concurrent.futures,time
P=pathlib.Path(__file__).resolve().parent
IDS='2610.40530 2610.40525 2610.39609 2610.32220 2606.22617 2610.31797 2610.31490 2610.38926 2610.30799 2609.03919 2610.36785 2610.36625 2610.35417 2610.22335 2610.18005 2608.25302 2610.27049 2604.21926 2610.33135 2610.31834 2610.26659 2610.11105 2610.37309 2610.33764'.split()
def fetch(i):
 url='https://arxiv.org/abs/'+i;raw=P/('review-abs-'+i+'.html')
 try:
  b=raw.read_bytes() if raw.exists() else urllib.request.urlopen(url,timeout=35).read();raw.write_bytes(b);s=b.decode('utf8');seg=s[s.find('<div class="submission-history">'):];seg=seg[:seg.find('</div>')];plain=html.unescape(re.sub('<[^>]*>',' ',seg));plain=re.sub(r'\s+',' ',plain).strip();hist=[]
  for v,dt in re.findall(r'\[v(\d+)\]\s*([A-Za-z]{3},\s*\d+\s+[A-Za-z]{3}\s+\d{4}\s+\d\d:\d\d:\d\d\s+UTC)',plain):hist.append({'version':int(v),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.strptime(dt,'%a, %d %b %Y %H:%M:%S UTC'))})
  return i,{'url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'history_raw':plain,'version_history':hist,'history_verified':bool(hist),'raw_path':raw.name}
 except Exception as ex:return i,{'url':url,'history_verified':False,'failure':str(ex)}
out={}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for i,d in pool.map(fetch,IDS):
  out[i]=d;(P/'review-official-histories.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(i,d.get('version_history',d.get('failure')),flush=True)
