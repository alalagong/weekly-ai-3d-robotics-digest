import pathlib,json,urllib.request,urllib.parse,xml.etree.ElementTree as ET,time
P=pathlib.Path(__file__).resolve().parent;NS={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
pool=json.loads((P/'main-pool.json').read_text(encoding='utf-8'));ids=[x['id'] for x in pool if not x.get('version') or not x.get('v1_utc') or not x.get('updated_utc') or not x.get('abstract')]
manifest=[];out=[]
for start in range(0,len(ids),100):
    batch=ids[start:start+100];url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'id_list':','.join(batch),'max_results':100,'start':0})
    q={'family':'pool-enrichment','url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'requested_ids':batch,'exhausted':False}
    try:
        dest=P/f'main-enrich-{start}.xml';b=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=40).read();dest.write_bytes(b);tree=ET.fromstring(b);rows=[]
        for e in tree.findall('a:entry',NS):
            def g(k):return ' '.join(e.findtext('a:'+k,default='',namespaces=NS).split())
            ident=g('id').rsplit('/',1)[-1];base,_,v=ident.partition('v')
            rows.append({'id':base,'version':int(v) if v else None,'title':g('title'),'abstract':g('summary'),'v1_utc':g('published'),'updated_utc':g('updated'),'source_urls':[url,'https://arxiv.org/abs/'+ident]})
        out+=rows;q.update(returned=len(rows),exhausted=set(x['id'] for x in rows)==set(batch))
    except Exception as ex:q['failure']=str(ex)
    manifest.append(q)
    for name,value in [('main-enrichment.json',out),('main-enrichment-manifest.json',manifest)]: (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(start,q.get('returned'),q.get('failure'),flush=True);time.sleep(3)
byid={x['id']:x for x in out}
for r in pool:
    if r['id'] in byid:
        n=byid[r['id']]
        for k in ['version','v1_utc','updated_utc','title','abstract']:
            if n.get(k):r[k]=n[k]
        r['source_urls']=list(dict.fromkeys(r.get('source_urls',[])+n['source_urls']))
(P/'main-pool-enriched.json').write_text(json.dumps(pool,ensure_ascii=False,indent=2),encoding='utf-8')
for route in ['core','geometry','extension','screen']:
    path=P/f'main-route-{route}.json';rows=json.loads(path.read_text(encoding='utf-8'));mapping={r['id']:r for r in pool};rows=[mapping.get(x['id'],x) for x in rows];(P/f'main-route-{route}-enriched.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('requested',len(ids),'received',len(out),flush=True)
