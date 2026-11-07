import urllib.request,urllib.parse,pathlib,json,re,html,time,concurrent.futures,xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent
NS={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
F={
'A-state':['SLAM','"simultaneous localization"','"simultaneous localisation"','VIO','"visual-inertial"','odometry','SfM','"structure from motion"'],
'A-backend':['"loop closure"','relocalization','relocalisation','registration','"bundle adjustment"','"pose graph"'],
'A-sensors':['LiDAR','radar','"RGB-D"','monocular','"multi-camera"'],
'B-foundation':['VGGT','"VGGT-Ω"','OmniVGGT','"geometry foundation"','"visual geometry transformer"','DUSt3R','MASt3R','pi3','"π³"','DA3','"Depth Anything"'],
'B-reconstruction':['"feed-forward"','feedforward','"3D reconstruction"','pointmap','"Gaussian splatting"','3DGS'],
'B-streaming':['"long-sequence"','"long-horizon"','streaming','"efficient attention"','"online reconstruction"'],
'C-navigation':['"embodied navigation"','VLN','"vision-language navigation"','"active mapping"','"semantic mapping"','"open-vocabulary mapping"'],
'C-world':['"world model"','"world-action"','"world action"','"world modeling"'],
'C-applications':['"underwater localization"','"underwater state estimation"','"thermal localization"','"endoscopic reconstruction"']}
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def clean(x):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',x))).strip()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def api(job):
    name,terms,df=job
    expr=' OR '.join('('+':'.join((f,t))+')' for t in terms for f in ('ti','abs'))
    if name=='A-sensors':expr='('+expr+') AND (ti:odometry OR abs:odometry OR ti:SLAM OR abs:SLAM OR ti:localization OR abs:localization OR ti:calibration OR abs:calibration)'
    q='('+expr+') AND '+df+':[202610220000 TO 202611011459]'
    m={'name':'main-api-'+name+'-'+df,'family':name,'source':'arXiv Atom API','field':'ti OR abs','query':q,'date_predicate':df+':[202610220000 TO 202611011459]','retrieved_at':now(),'pages':[],'fetched':0,'total':None,'exhausted':False};rows=[];start=0
    while True:
        url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'start':start,'max_results':200,'sortBy':'submittedDate','sortOrder':'descending'})
        try:
            b=urllib.request.urlopen(url,timeout=30).read();dest=P/(m['name']+'-'+str(start)+'.xml');dest.write_bytes(b);tree=ET.fromstring(b)
            total=tree.findtext('o:totalResults',namespaces=NS)
            if total is None:raise ValueError('No totalResults; not a confirmed zero')
            m['total']=int(total);entries=tree.findall('a:entry',NS)
            m['pages'].append({'url':url,'start':start,'returned':len(entries),'raw_path':dest.name})
            for e in entries:
                def g(k):return ' '.join(e.findtext('a:'+k,default='',namespaces=NS).split())
                ident=g('id').rsplit('/',1)[-1];base,_,v=ident.partition('v')
                rows.append({'id':base,'version':int(v) if v else None,'title':g('title'),'abstract':g('summary'),'v1_utc':g('published'),'updated_utc':g('updated'),'query_hits':[m['name']],'source_urls':[url,'https://arxiv.org/abs/'+ident],'abstract_read':False})
            m['fetched']+=len(entries)
            if start+len(entries)>=m['total']:m['exhausted']=True;break
            if not entries:m['failure']='Empty page before reported total';break
            start+=len(entries);time.sleep(3)
        except Exception as ex:m['failure']=str(ex);break
    if df=='lastUpdatedDate':
        bad=[x['id'] for x in rows if x['updated_utc']<'2026-10-22T00:00:00Z' or x['updated_utc']>'2026-11-01T14:59:59Z']
        if bad:m.update(date_semantics_anomaly_ids=bad,coverage_valid=False,requires_advanced_latest_recovery=True)
    return m,rows
if __name__=='__main__':
    manifest=[];rows=[]
    jobs=[(n,t,d) for n,t in F.items() for d in ('submittedDate','lastUpdatedDate')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for m,r in pool.map(api,jobs):
            manifest.append(m);rows+=r;save('main-search-manifest.json',manifest);save('main-search-candidates.json',rows)
            print(m['name'],m['total'],m['fetched'],m['exhausted'],m.get('failure'),flush=True)
