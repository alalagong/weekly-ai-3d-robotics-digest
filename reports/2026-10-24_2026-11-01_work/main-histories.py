import pathlib,json,re,urllib.request,time,datetime,concurrent.futures,hashlib
from lxml import html
P=pathlib.Path(__file__).resolve().parent
def rd(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
ids=[]
for name in ['core-search.json','geometry-search.json','extension-screened.json','review-candidates-screened.json']:
    if not (P/name).exists():continue
    data=rd(name);data=data.get('papers',[]) if isinstance(data,dict) else data
    for r in data:
        if r.get('decision')=='include' or r.get('disposition') in ['included','supplemental','revision_tracking','unresolved','deep_read']:ids.append(r['id'])
ids+=['2610.37330'];ids=list(dict.fromkeys(ids))
def fetch(ident):
    url='https://arxiv.org/abs/'+ident;row={'id':ident,'url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'history_verified':False}
    try:
        caches=list(P.glob('*-abs-'+ident+'.html'));dest=caches[0] if caches else P/('main-abs-'+ident+'.html')
        b=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=35).read();dest.write_bytes(b);tree=html.fromstring(b);s=' '.join(tree.text_content().split())
        versions=[]
        for v,d in re.findall(r'\[v(\d+)\]\s*(\w{3},\s+\d{1,2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+UTC)',s):
            dt=datetime.datetime.strptime(d,'%a, %d %b %Y %H:%M:%S UTC').replace(tzinfo=datetime.timezone.utc);versions.append({'version':int(v),'utc':dt.isoformat().replace('+00:00','Z')})
        assert versions,'No Submission history parsed'
        versions=list({x['version']:x for x in versions}.values());v1=next(x for x in versions if x['version']==1);available=[x for x in versions if x['utc']<='2026-11-01T14:59:32Z'];latest=max(available,key=lambda x:x['version']) if available else max(versions,key=lambda x:x['version'])
        newer_versions=[x for x in versions if x['version']>latest['version']]
        if newer_versions:
            locked=P/('main-abs-'+ident+'v'+str(latest['version'])+'.html')
            locked_b=locked.read_bytes() if locked.exists() else urllib.request.urlopen(url+'v'+str(latest['version']),timeout=35).read();locked.write_bytes(locked_b);tree=html.fromstring(locked_b)
            row.update(post_cutoff_versions=newer_versions,abstract_source_url=url+'v'+str(latest['version']),abstract_raw_path=locked.name)
        title=tree.xpath('//h1[contains(@class,"title")]');abstract=tree.xpath('//blockquote[contains(@class,"abstract")]')
        row.update(history_verified=True,version=latest['version'],v1_utc=v1['utc'],updated_utc=latest['utc'],submission_history=versions,raw_path=dest.name,sha256=hashlib.sha256(b).hexdigest(),official_title=' '.join(title[0].text_content().split()).removeprefix('Title:').strip() if title else None,official_abstract=' '.join(abstract[0].text_content().split()).removeprefix('Abstract:').strip() if abstract else None)
    except Exception as ex:row['failure']=str(ex)
    return row
initial=P/'main-official-histories-initial.json'
if (P/'main-official-histories.json').exists() and not initial.exists():initial.write_bytes((P/'main-official-histories.json').read_bytes())
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for row in pool.map(fetch,ids):
        out.append(row);save('main-official-histories.json',out)
        if len(out)%30==0:print(len(out),'/',len(ids),'verified',sum(x['history_verified'] for x in out),flush=True)
print('total',len(out),'verified',sum(x['history_verified'] for x in out),'fail',[x['id'] for x in out if not x['history_verified']],flush=True)
