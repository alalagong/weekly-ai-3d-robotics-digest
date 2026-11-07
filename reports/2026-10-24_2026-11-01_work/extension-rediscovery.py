import urllib.request,urllib.parse,pathlib,json,time,xml.etree.ElementTree as ET,concurrent.futures
P=pathlib.Path(__file__).resolve().parent
NS={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
F={'A-independent':['"place recognition"','"pose tracking"','"map merging"','"global localization"','"visual localisation"','"inertial navigation"'], 'B-independent':['"metric scale"','"point map"','"multi-view stereo"','"geometric memory"','"camera recovery"','"dense geometry"'], 'C-independent':['"object-goal"','"object navigation"','"scene graph"','"spatial memory"','"semantic exploration"','"language-guided navigation"','"neural radiance" AND robot','thermal AND SLAM','underwater AND mapping','endoscopic AND localization']}
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def query(job):
 name,terms,df=job
 expr=' OR '.join('('+f+':'+t+')' for t in terms for f in ('ti','abs'))
 q='('+expr+') AND '+df+':[202610240817 TO 202611011459]'
 m={'name':name+'-'+df,'source':'arXiv Atom API','fields':'title OR abstract','query':q,'date_predicate':df+':[202610240817 TO 202611011459]','requested_at':now(),'total':None,'fetched':0,'pages':[],'exhausted':False,'status':'pending'}
 rows=[];start=0
 while True:
  url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'start':start,'max_results':200,'sortBy':'submittedDate','sortOrder':'descending'})
  try:
   b=urllib.request.urlopen(url,timeout=35).read();dest=P/('extension-api-'+m['name']+'-'+str(start)+'.xml');dest.write_bytes(b);t=ET.fromstring(b);total=t.findtext('o:totalResults',namespaces=NS)
   if total is None:raise ValueError('Missing totalResults is not a verified zero')
   m['total']=int(total);entries=t.findall('a:entry',NS);m['pages'].append({'url':url,'start':start,'returned':len(entries),'retrieved_at':now(),'raw_path':dest.name})
   for e in entries:
    def g(k):return ' '.join(e.findtext('a:'+k,default='',namespaces=NS).split())
    ident=g('id').rsplit('/',1)[-1];base,_,v=ident.partition('v');rows.append({'id':base,'version':int(v) if v else None,'title':g('title'),'abstract':g('summary'),'v1_utc':g('published'),'updated_utc':g('updated'),'queries':[m['name']],'source_urls':[url,'https://arxiv.org/abs/'+ident],'abstract_read':False})
   m['fetched']+=len(entries)
   if start+len(entries)>=m['total']:m.update(exhausted=True,status='complete');break
   if not entries:raise ValueError('Empty page before total exhausted')
   start+=len(entries);time.sleep(3)
  except Exception as ex:m.update(status='incomplete',failure=str(ex),resume_url=url);break
 if df=='lastUpdatedDate':
  bad=[x['id'] for x in rows if not ('2026-10-24T08:17:00Z'<=x['updated_utc']<='2026-11-01T14:59:59Z')]
  if bad:m.update(status='incomplete',date_semantics_anomaly_ids=bad,needs_advanced_latest_date_recovery=True)
 return m,rows
if __name__=='__main__':
 manifest=[];rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for m,r in pool.map(query,[(n,t,d) for n,t in F.items() for d in ('submittedDate','lastUpdatedDate')]):
   manifest.append(m);rows+=r;save('extension-manifest.json',manifest);save('extension-search.json',{'schema_version':1,'run_at':'2026-11-01T14:59:32Z','coverage_start_utc':'2026-10-24T08:17:58Z','coverage_end_utc':'2026-11-01T14:59:32Z','scope':'Independent A/B/C rediscovery with alternate terms; candidate abstracts not yet model-read','coverage_status':'incomplete','queries':manifest,'papers':rows});print(m['name'],m['total'],m['fetched'],m['status'],flush=True)
