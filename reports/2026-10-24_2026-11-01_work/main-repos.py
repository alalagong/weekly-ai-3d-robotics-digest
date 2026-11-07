import json,pathlib,urllib.request,urllib.parse,time
P=pathlib.Path(__file__).resolve().parent
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
queries=['SLAM created:2026-10-24..2026-11-01','VGGT pushed:2026-10-24..2026-11-01','odometry pushed:2026-10-24..2026-11-01','"3D reconstruction" created:2026-10-24..2026-11-01']
manifest=[];repos={}
for qi,q in enumerate(queries):
    page=1;fetched=0
    while True:
        url='https://api.github.com/search/repositories?'+urllib.parse.urlencode({'q':q,'per_page':100,'page':page,'sort':'updated','order':'desc'})
        m={'family':'repo-public-rest-fallback','query':q,'url':url,'page':page,'per_page':100,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exhausted':False}
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'slam-weekly-research','Accept':'application/vnd.github+json'})
            raw=urllib.request.urlopen(req,timeout=35).read().decode();(P/f'repo-search-{qi}-{page}.json').write_text(raw,encoding='utf-8');x=json.loads(raw)
            items=x['items'];fetched+=len(items);m.update(total=x['total_count'],returned=len(items),fetched=fetched,incomplete_results=x.get('incomplete_results'),exhausted=fetched>=x['total_count'] and not x.get('incomplete_results'))
            for r in items:repos[r['full_name']]=r
        except Exception as ex:m['failure']=str(ex)
        manifest.append(m);save('repo-manifest.json',manifest);save('repo-candidates.json',list(repos.values()));print(q,page,m.get('total'),m.get('returned'),m.get('failure'),flush=True)
        if m.get('failure') or m['exhausted'] or not m.get('returned') or fetched>=1000:break
        page+=1;time.sleep(7)
    time.sleep(4)
url='https://github.com/trending?since=weekly'
m={'family':'repo-trending','url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exhausted':False,'scope':'GitHub weekly trending snapshot; no growth inference'}
try:
    b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read();(P/'repo-trending.html').write_bytes(b);m.update(status=200,bytes=len(b))
except Exception as ex:m['failure']=str(ex)
manifest.append(m);save('repo-manifest.json',manifest)
