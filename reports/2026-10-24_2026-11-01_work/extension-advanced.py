import urllib.request,urllib.parse,pathlib,json,time,re,html,concurrent.futures
from importlib.machinery import SourceFileLoader
P=pathlib.Path(__file__).resolve().parent
F=SourceFileLoader('extension_rediscovery',str(P/'extension-rediscovery.py')).load_module().F
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',s))).strip()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def fetch(job):
 name,terms=job[:2];mode=job[2] if len(job)>2 else 'OR';terms=[t for t in terms if ' AND ' not in t];m={'name':'extension-advanced-'+name+'-latest','source':'arXiv Advanced Search','field':'all fields exact phrase alternatives' if mode=='OR' else 'all fields conjunction','date_predicate':'Submission date (most recent), date-date_type=submitted_date, 2026-10-24 through 2026-11-01 inclusive whole days; official history exact postfilter','requested_at':now(),'pages':[],'total':None,'fetched':0,'exhausted':False};rows=[];start=0
 while True:
  args={'advanced':'','classification-include_cross_list':'include','date-filter_by':'date_range','date-from_date':'2026-10-24','date-to_date':'2026-11-01','date-date_type':'submitted_date','abstracts':'show','size':'200','order':'-submitted_date','start':start}
  for i,t in enumerate(terms):args.update({f'terms-{i}-operator':'AND' if i==0 else mode,f'terms-{i}-term':t,f'terms-{i}-field':'all'})
  url='https://arxiv.org/search/advanced?'+urllib.parse.urlencode(args)
  try:
   s=urllib.request.urlopen(url,timeout=35).read().decode();dest=P/(m['name']+'-'+str(start)+'.html');dest.write_text(s,encoding='utf8');txt=clean(s)
   mt=re.search(r'Showing\s+[\d,]+\s*[–-]\s*[\d,]+\s+of\s+([\d,]+)\s+results',txt)
   if mt:m['total']=int(mt[1].replace(',',''))
   elif 'Sorry, your query returned no results' in txt:m['total']=0
   else:raise ValueError('No parseable official result count; never treat as zero')
   blocks=re.split(r'<li class="arxiv-result">',s)[1:];page=[]
   for b in blocks:
    ident=re.search(r'https://arxiv.org/abs/(\d{4}\.\d{4,5})(?:v\d+)?',b)
    if not ident:continue
    title=re.search(r'<p class="title is-5 mathjax">(.*?)</p>',b,re.S);abstract=re.search(r'<span class="abstract-full[^\"]*"[^>]*>(.*?)<a class="is-size-7"',b,re.S)
    page.append({'id':ident[1],'title':clean(title[1]) if title else '', 'abstract':clean(abstract[1]).removesuffix('△ Less').strip() if abstract else '', 'queries':[m['name']],'source_urls':[url,'https://arxiv.org/abs/'+ident[1]],'abstract_read':False})
   rows+=page;m['fetched']+=len(page);m['pages'].append({'url':url,'start':start,'returned':len(page),'retrieved_at':now(),'raw_path':dest.name})
   if start+len(page)>=m['total']:m['exhausted']=True;break
   if not page:raise ValueError('Empty page before total exhausted')
   start+=len(page);time.sleep(3)
  except Exception as ex:m.update(failure=str(ex),resume_url=url);break
 return m,rows
if __name__=='__main__':
 manifest=[];rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for m,r in pool.map(fetch,F.items()):
   manifest.append(m);rows+=r;save('extension-advanced-manifest.json',manifest);save('extension-advanced-candidates.json',rows);print(m['name'],m['total'],m['fetched'],m['exhausted'],m.get('failure'),flush=True)
