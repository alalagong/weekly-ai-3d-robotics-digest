import pathlib,json,time,collections
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
now=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
S=read('extension-screened.json');rows=S['papers'];byid={x['id']:x for x in rows}
independent=[x for x in rows if any(q.startswith('independent-') for q in x['input_origins'])]
api=read('extension-manifest.json');latest=read('extension-advanced-manifest.json')+read('extension-advanced-applications-manifest.json')
for m in api:
 if 'lastUpdatedDate' in m['name']:
  m.update(coverage_valid=False,status='superseded_by_verified_advanced_latest',reason='API lastUpdatedDate predicate reproduced submittedDate set; not accepted as proof of updated coverage.',replacement_queries=[x['name'] for x in latest if x['name'].split('advanced-')[-1][0]==m['name'][0]])
queries=api+latest
closed=all(x['exhausted'] for x in api if 'submittedDate' in x['name']) and all(x['exhausted'] for x in latest)
assert closed
assert all(x.get('history_verified') for x in independent)
assert not S['unresolved']
checks=[]
for f in ['main-route-extension-enriched.json','main-extra-extension.json']:
 source=read(f);missing=sorted({x['id'] for x in source}-set(byid));checks.append({'source_file':f,'source_unique':len({x['id'] for x in source}),'missing_ids':missing,'closed':not missing});assert not missing
mainc=[x for x in read('main-search-candidates.json') if any('C-' in q for q in x.get('query_hits',[]))]
missing=sorted({x['id'] for x in mainc}-set(byid));checks.append({'source_file':'main-search-candidates.json C-family','source_unique':len({x['id'] for x in mainc}),'missing_ids':missing,'closed':not missing});assert not missing
required=['problem','method','insight_math','experiments','category','takeaway','priority_reason']
field_errors=[{'id':x['id'],'missing':[k for k in required if not x.get(k)]} for x in rows if x['disposition']!='excluded' and any(not x.get(k) for k in required)]
length_errors=[{'id':x['id'],'length':len(x.get('takeaway',''))} for x in rows if x['disposition']!='excluded' and not 40<=len(x.get('takeaway',''))<=100]
assert not field_errors and not length_errors
assert all(x['abstract_read'] and x.get('abstract') for x in rows)
initial_api={x['id'] for x in independent if 'independent-api' in x['input_origins']}
initial_known={x['id'] for x in read('main-search-candidates.json')}|{x['id'] for x in read('main-cross-metadata.json')}
pool_known={x['id'] for x in read('main-pool-enriched.json')}
closure={'schema_version':1,'run_at':'2026-11-01T14:59:32Z','validation_at':now,'window_utc':{'left_exclusive':'2026-10-24T08:17:58Z','right_inclusive':'2026-11-01T14:59:32Z'},'display_timezone':'Asia/Shanghai','screened_unique':len(rows),'counts':S['counts'],'abstract_read_unique':len(rows),'full_text_read':0,'set_checks':checks,'unresolved':[],'takeaway_length_errors':length_errors,'required_field_errors':field_errors,'independent_unique':len(independent),'independent_counts':dict(collections.Counter(x['disposition'] for x in independent)),'independent_first_api_delta_against_initial_search_and_cross':sorted(initial_api-initial_known),'independent_delta_against_current_main_pool':[{'id':x['id'],'disposition':x['disposition'],'reason':x['reason']} for x in independent if x['id'] not in pool_known],'note':'A/B independent overlap is intentionally retained for parent deduplication; these are unique ID records within this artifact, not additive report counts. Official history checked for all independent IDs; parent retains responsibility for remaining shared main metadata histories. 37330 HTML Abstract only resolved conflict; no Method/Experiments full-text reading.'}
save('extension-closure.json',closure)
save('extension-search.json',{'schema_version':2,'run_at':'2026-11-01T14:59:32Z','generated_at':now,'coverage_start_utc':'2026-10-24T08:17:58Z','coverage_end_utc':'2026-11-01T14:59:32Z','scope':'Independent alternate-term A/B/C discovery only; shared main-C screening is in extension-screened.json','coverage_status':'query_set_exhausted_with_verified_latest_date_recovery','queries':queries,'papers':independent,'counts':dict(collections.Counter(x['disposition'] for x in independent)),'boundary':'Abstract-level only; all independent versions/times verified from official submission history; source pages and query raw bodies persist beside this file.'})
save('extension-query-evidence.json',{'generated_at':now,'queries':queries,'initial_failed_probes':[{'source':'web.open arXiv API','url':'https://export.arxiv.org/api/query?search_query=all%3A%22vision-language%20navigation%22%20AND%20submittedDate%3A%5B202610240817%20TO%20202611011459%5D&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending','status':'tool_access_error','total':None,'fetched':0,'exhausted':False,'resolution':'Public API became accessible through approved Windows Python urllib; parent main-C-navigation covers original VLN family, independent alternate terms completed separately.'},{'source':'Scholar arxiv_search','query':'(all:"world model" OR all:"world action" OR all:"embodied navigation" OR all:"vision-language navigation" OR all:"semantic mapping" OR all:"open-vocabulary") AND submittedDate:[202610240817 TO 202611011459]','status':'interrupted_no_result','elapsed_seconds_observed':921.4,'total':None,'fetched':None,'exhausted':False,'resolution':'Not used as zero or coverage evidence; parent directed no further Scholar calls.'}],'exploratory_web_fallback':[{'query':'site:arxiv.org/abs/2610 "navigation" "October" "2026"','total':None,'exhausted':False},{'query':'site:arxiv.org/abs/2610 "world model" "3D"','total':None,'exhausted':False},{'query':'site:arxiv.org/abs/2610 "SLAM" "Oct"','total':None,'exhausted':False}],'exploratory_web_note':'Open web returned old non-window-scoped examples; it was not treated as an exhausted dated candidate source or proof of absence.'})
print(json.dumps(closure,ensure_ascii=False,indent=2))
