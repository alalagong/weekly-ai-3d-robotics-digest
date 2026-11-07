import pathlib,json,urllib.request,re,html,time
P=pathlib.Path(__file__).resolve().parent;i='2610.34921';url='https://arxiv.org/abs/'+i;raw=P/('review-abs-'+i+'.html')
b=raw.read_bytes() if raw.exists() else urllib.request.urlopen(url,timeout=35).read();raw.write_bytes(b);s=b.decode('utf8');seg=s[s.find('<div class="submission-history">'):];seg=seg[:seg.find('</div>')];plain=html.unescape(re.sub('<[^>]*>',' ',seg));plain=re.sub(r'\s+',' ',plain).strip();hist=[]
for v,dt in re.findall(r'\[v(\d+)\]\s*([A-Za-z]{3},\s*\d+\s+[A-Za-z]{3}\s+\d{4}\s+\d\d:\d\d:\d\d\s+UTC)',plain):hist.append({'version':int(v),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.strptime(dt,'%a, %d %b %Y %H:%M:%S UTC'))})
assert hist
d={'url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'history_raw':plain,'version_history':hist,'history_verified':True,'raw_path':raw.name}
allhist=json.loads((P/'review-official-histories.json').read_text(encoding='utf8'));allhist[i]=d;(P/'review-official-histories.json').write_text(json.dumps(allhist,ensure_ascii=False,indent=2),encoding='utf8');print(d)
