import importlib.util,pathlib,urllib.request,urllib.parse,time,re,json,concurrent.futures
from lxml import html
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('main_search',P/'main-search.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def clean(s):return re.sub(r'\s+',' ',s).strip()
def fetch(job):
    name,terms,df=job;m={'name':'main-advanced-'+name+'-'+df,'family':name,'source':'arXiv Advanced Search','field':'all metadata; complementary to ti/abs API','terms':terms,'date_predicate':df+':2026-10-22..2026-11-01','retrieved_at':mod.now(),'total':None,'fetched':0,'pages':[],'exhausted':False};rows=[];start=0
    while True:
        params={'advanced':'','classification-include_cross_list':'include','date-filter_by':'date_range','date-from_date':'2026-10-22','date-to_date':'2026-11-01','date-date_type':df,'abstracts':'show','size':200,'order':'-submitted_date','start':start}
        for i,t in enumerate(terms):params.update({f'terms-{i}-operator':'AND' if i==0 else 'OR',f'terms-{i}-term':t,f'terms-{i}-field':'all'})
        url='https://arxiv.org/search/advanced?'+urllib.parse.urlencode(params)
        try:
            dest=P/(m['name']+'-'+str(start)+'.html');b=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=40).read();dest.write_bytes(b);tree=html.fromstring(b);plain=clean(tree.text_content())
            total=re.search(r'of\s+([\d,]+)\s+results',plain)
            if total:m['total']=int(total[1].replace(',',''))
            elif re.search('no results',plain,re.I):m['total']=0
            else:raise ValueError('No explicit result total; cannot claim exhausted')
            entries=tree.xpath('//li[@class="arxiv-result"]');m['pages'].append({'url':url,'start':start,'returned':len(entries),'raw_path':dest.name})
            for e in entries:
                link=e.xpath('.//p[contains(@class,"list-title")]//a');mid=re.search(r'(\d{4}\.\d{4,5})',link[0].text_content() if link else '')
                if not mid:continue
                title=e.xpath('.//p[contains(@class,"title is-5")]');abstract=e.xpath('.//span[contains(@class,"abstract-full")]')
                rows.append({'id':mid[1],'title':clean(title[0].text_content()) if title else '', 'abstract':clean(abstract[0].text_content()).removesuffix('△ Less').strip() if abstract else '', 'query_hits':[m['name']],'source_urls':[url,'https://arxiv.org/abs/'+mid[1]],'abstract_read':False,'date_metadata_unverified':True})
            m['fetched']+=len(entries)
            if start+len(entries)>=m['total']:m['exhausted']=True;break
            if not entries:m['failure']='Empty page before reported total';break
            start+=len(entries);time.sleep(3)
        except Exception as ex:m['failure']=str(ex);break
    return m,rows
if __name__=='__main__':
    old=P/'main-advanced-manifest.json';failed=P/'main-advanced-parser-failures.json'
    if old.exists() and not failed.exists():failed.write_bytes(old.read_bytes())
    manifest=[];rows=[];jobs=[(n,t,d) for n,t in mod.F.items() for d in ('submitted_date_first','submitted_date')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for m,r in pool.map(fetch,jobs):
            manifest.append(m);rows+=r;mod.save('main-advanced-manifest.json',manifest);mod.save('main-advanced-candidates.json',rows)
            print(m['name'],m['total'],m['fetched'],m['exhausted'],m.get('failure'),flush=True)
