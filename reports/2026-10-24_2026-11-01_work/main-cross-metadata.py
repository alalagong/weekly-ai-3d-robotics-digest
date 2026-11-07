import pathlib,json,urllib.request,urllib.parse,xml.etree.ElementTree as ET,time
P=pathlib.Path(__file__).resolve().parent
ids=list(dict.fromkeys([x['id'] for x in json.loads((P/'main-category-candidates.json').read_text(encoding='utf-8'))]+[x['id'] for x in json.loads((P/'main-audit-seeds.json').read_text(encoding='utf-8'))]))
manifest=[];out=[];ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
for start in range(0,len(ids),100):
    batch=ids[start:start+100];url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'id_list':','.join(batch),'max_results':100,'start':0})
    q={'family':'official-id-cross-metadata','url':url,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'requested_ids':batch,'exhausted':False}
    try:
        b=urllib.request.urlopen(url,timeout=40).read();(P/f'main-cross-api-{start}.xml').write_bytes(b);tree=ET.fromstring(b)
        rows=[]
        for e in tree.findall('a:entry',ns):
            def get(k):return ' '.join((e.findtext('a:'+k,default='',namespaces=ns)).split())
            ident=get('id').rsplit('/',1)[-1];base,_,version=ident.partition('v')
            rows.append({'id':base,'version':int(version) if version else None,'title':get('title'),'v1_utc':get('published'),'updated_utc':get('updated'),'abstract':get('summary'),'abstract_read':False,'source_urls':[url,'https://arxiv.org/abs/'+ident],'metadata_source':'arXiv Atom id_list; official abs submission history still required for selected versions'})
        out+=rows;q.update(returned=len(rows),total=tree.findtext('o:totalResults',namespaces=ns),exhausted=set(x['id'] for x in rows)==set(batch))
    except Exception as ex:q['failure']=str(ex)
    manifest.append(q)
    (P/'main-cross-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(P/'main-cross-metadata.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(start,q.get('returned'),q.get('failure'),flush=True);time.sleep(3)
