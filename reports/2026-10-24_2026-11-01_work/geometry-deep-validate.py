import pathlib,json,datetime,re,urllib.parse
from lxml import html
P=pathlib.Path(__file__).parent
j=json.loads((P/'geometry-deep.json').read_text(encoding='utf-8'));checks=[];errors=[]
def ck(name,value):
 checks.append({'check':name,'passed':bool(value)})
 if not value:errors.append(name)
ck('exact4papers',len(j['papers'])==4)
ck('locked_versions',sorted((p['id'],p['version']) for p in j['papers'])==sorted([('2610.37000',2),('2610.35806',1),('2610.36150',1),('2605.23889',2)]))
cut=datetime.datetime.fromisoformat(j['run_at'].replace('Z','+00:00'))
start=datetime.datetime.fromisoformat(j['coverage_start_utc'].replace('Z','+00:00'))
for p in j['papers']:
 aid=p['id'];d=html.fromstring(pathlib.Path(p['source']['html_path']).read_bytes());ids=set(d.xpath('//@id'))
 # Validate the numbered sections actually present in this source, not an arbitrary minimum count.
 source_sections={m.group(1) for h in d.xpath('//h2[contains(@class, "ltx_title_section")]') if (m:=re.match(r'^\s*(\d+)\s',h.text_content()))}
 declared_sections={m.group(1) for text in p['actual_read_sections'] if (m:=re.match(r'^\s*(\d+)\s',text))}
 ck(aid+' fullmain_sections',bool(source_sections) and source_sections.issubset(declared_sections) and p['full_main_text_read'])
 ck(aid+' realhtml',p['source']['char_count']>30000)
 ck(aid+' frozenversion',datetime.datetime.fromisoformat(p['updated_utc'].replace('Z','+00:00'))<=cut)
 ck(aid+' noexecutionclaim',p['ran_experiments'] is False and p['downloaded_weights_or_datasets'] is False)
 ck(aid+' exactnumeric_sources',all(e.get('source') and e.get('source_url') for e in p['experiments']))
 for e in p['experiments']:
  anchor=urllib.parse.urlparse(e['source_url']).fragment
  if anchor:ck(aid+' anchor '+anchor,anchor in ids)
 f=p['system_figure']
 if f['embed_allowed']:
  ck(aid+' captionqualifies',bool(re.search(r'overview|pipeline|framework',f['caption'],re.I)))
  ck(aid+' imageviewconfirmed',f['visually_verified'] and pathlib.Path(f['path']).exists())
 else:ck(aid+' nofakefigure','2610.35806'==aid)
 if p['window_class']=='revised':ck(aid+' oldrevisionwindow',datetime.datetime.fromisoformat(p['v1_utc'].replace('Z','+00:00'))<=start<datetime.datetime.fromisoformat(p['updated_utc'].replace('Z','+00:00')))
ck('no_major_revision_claim',all('重大' not in p['revision_comparison'] or '不评价重大' in p['revision_comparison'] for p in j['papers']))
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':not errors,'check_count':len(checks),'errors':errors,'checks':checks}
(P/'geometry-deep-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':not errors,'check_count':len(checks),'errors':errors},ensure_ascii=False))
