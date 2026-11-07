import pathlib,json,urllib.request,urllib.parse,xml.etree.ElementTree as ET,time,concurrent.futures
P=pathlib.Path(__file__).resolve().parent;NS={'a':'http://www.w3.org/2005/Atom'}
rd=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
known={x['id']:x for x in rd('main-pool-enriched.json')};source=rd('review-independent-unique.json');ids=[x['id'] for x in source if x['id'] not in known]
def get(job):
    start,batch=job;url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'id_list':','.join(batch),'max_results':100,'start':0});q={'family':'independent-ID-metadata-enrichment','url':url,'requested_ids':batch,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exhausted':False};out=[]
    try:
        dest=P/f'review-enrich-{start}.xml';b=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=35).read();dest.write_bytes(b);tree=ET.fromstring(b)
        for e in tree.findall('a:entry',NS):
            def g(k):return ' '.join(e.findtext('a:'+k,default='',namespaces=NS).split())
            ident=g('id').rsplit('/',1)[-1];base,_,v=ident.partition('v');out.append({'id':base,'version':int(v) if v else None,'title':g('title'),'abstract':g('summary'),'v1_utc':g('published'),'updated_utc':g('updated'),'metadata_retrieved_at':q['retrieved_at'],'metadata_source_url':url,'metadata_after_run_at':True})
        q.update(returned=len(out),exhausted=set(r['id'] for r in out)==set(batch),raw_path=dest.name)
    except Exception as ex:q['failure']=str(ex)
    return q,out
old=P/'review-enrichment-manifest.json';backup=P/'review-enrichment-initial-attempts.json'
if old.exists() and not backup.exists():backup.write_bytes(old.read_bytes())
manifest=[];rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for q,rs in pool.map(get,[(s,ids[s:s+100]) for s in range(0,len(ids),100)]):
        manifest.append(q);rows+=rs
        for n,value in [('review-enrichment-manifest.json',manifest),('review-enrichment.json',rows)]:(P/n).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
        print(len(rows),'/',len(ids),q.get('failure'),flush=True)
        time.sleep(3)
