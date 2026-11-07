import pathlib,urllib.request,urllib.parse,time,re,json,datetime,concurrent.futures
from lxml import html
P=pathlib.Path(__file__).resolve().parent
F={
'A-localization':['"place recognition"','"visual localization"','"view graph"','"camera pose"','"scene change detection"'],
'A-geometry':['"geometric prior"','correspondence','"image registration"','"point cloud registration"','"multi-view geometry"','"ego motion"'],
'B-dense':['"dense geometry"','"geometry foundation"','"geometry prediction"','"3D scene understanding"','"pointmap"','"point map"','"geometry transformer"'],
'C-simulator':['"world simulator"','"world action"','"action world"','"spatial memory"','"embodied mapping"','"semantic map"'],
'C-sensors':['"robot localization"','"radar localization"','"event camera"','"endoscopic reconstruction"','"underwater reconstruction"','"visual navigation"'],
}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def clean(s):return re.sub(r'\s+',' ',s).strip()
def fetch(job):
 n,terms,df=job;m={'name':'review-'+n+'-'+df,'family':n,'channel':'arXiv Advanced Search independent terms','fields':'all metadata','terms':terms,'predicate':df+':2026-10-22..2026-11-01; exact abs history later: (2026-10-24T08:17:58Z,2026-11-01T14:59:32Z]','retrieved_at':now(),'total':None,'pages':[],'fetched':0,'exhausted':False};rows=[];start=0
 while True:
  params={'advanced':'','classification-include_cross_list':'include','date-filter_by':'date_range','date-from_date':'2026-10-22','date-to_date':'2026-11-01','date-date_type':df,'abstracts':'show','size':200,'order':'-submitted_date','start':start}
  for i,t in enumerate(terms):params.update({f'terms-{i}-operator':'AND' if i==0 else 'OR',f'terms-{i}-term':t,f'terms-{i}-field':'all'})
  url='https://arxiv.org/search/advanced?'+urllib.parse.urlencode(params)
  try:
   dest=P/(m['name']+'-'+str(start)+'.html');b=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=50).read();dest.write_bytes(b);tree=html.fromstring(b);plain=clean(tree.text_content());total=re.search(r'of\s+([\d,]+)\s+results',plain)
   if total:m['total']=int(total[1].replace(',',''))
   elif re.search('no results',plain,re.I):m['total']=0
   else:raise ValueError('Explicit total missing')
   entries=tree.xpath('//li[@class="arxiv-result"]');m['pages'].append({'url':url,'start':start,'returned':len(entries),'raw_path':dest.name})
   for e in entries:
    link=e.xpath('.//p[contains(@class,"list-title")]//a');mid=re.search(r'(\d{4}\.\d{4,5})',link[0].text_content() if link else '')
    if not mid:continue
    title=e.xpath('.//p[contains(@class,"title is-5")]');abstract=e.xpath('.//span[contains(@class,"abstract-full")]');dates=e.xpath('.//p[contains(@class,"is-size-7")]')
    rows.append({'id':mid[1],'title':clean(title[0].text_content()) if title else '', 'abstract':clean(abstract[0].text_content()).removesuffix('△ Less').strip() if abstract else '', 'search_date_text':[clean(x.text_content()) for x in dates], 'query_hits':[m['name']],'source_urls':[url,'https://arxiv.org/abs/'+mid[1]],'reading_level':'metadata + abstract available; not yet screened','history_unverified':True})
   m['fetched']+=len(entries)
   if start+len(entries)>=m['total']:m['exhausted']=True;break
   if not entries:raise ValueError('Empty before total')
   start+=len(entries);time.sleep(2)
  except Exception as ex:m['failure']=str(ex);break
 return m,rows
if __name__=='__main__':
 jobs=[(n,t,d) for n,t in F.items() for d in ('submitted_date_first','submitted_date')];manifest=[];rows=[]
 save('review-query-plan.json',{'run_at':'2026-11-01T14:59:32Z','window_open':'2026-10-24T08:17:58Z','window_closed':'2026-11-01T14:59:32Z','independent_before_main_pool':True,'jobs':jobs})
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for m,r in pool.map(fetch,jobs):
   manifest.append(m);rows+=r;save('review-query-manifest.json',manifest);save('review-discovered-raw.json',rows);print(m['name'],m['total'],m['fetched'],m['exhausted'],m.get('failure'),flush=True)
