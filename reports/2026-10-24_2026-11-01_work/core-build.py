import json,pathlib,datetime,collections
P=pathlib.Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text(encoding='utf8'))
S=load('core-selected-raw.json');notes=load('core-notes.json');notes.update(load('core-notes-extra.json'))
if (P/'core-notes-sensors.json').exists():notes.update(load('core-notes-sensors.json'))
H=load('core-official-histories.json');past=json.loads((P.parent/'paper-history.json').read_text(encoding='utf8'))['papers']
START='2026-10-24T08:17:58Z';END='2026-11-01T14:59:32Z';out=[]
for q in S:
 i=q['id'];n=notes[i];h=H.get(i,{});hist=h.get('version_history',[])
 before=[t for t in hist if t['utc']<=END]
 if hist:
  q['v1_utc']=next(t['utc'] for t in hist if t['version']==1)
  chosen=max(before,key=lambda x:x['version']);q['version']=chosen['version'];q['updated_utc']=chosen['utc']
 key='v'+str(q['version']);old=past.get(i,{});prev=old.get('versions',{}).get(key);same=bool(prev and prev.get('status')!='excluded')
 if START<q['v1_utc']<=END:wc='new'
 elif START<q['updated_utc']<=END:wc='revised'
 elif same:wc='previously_reported_same_version'
 elif q['version']>1:wc='historical_revision_backfill'
 else:wc='historical_backfill'
 decision='exclude' if n[0]=='exclude' else ('reference_previous' if same else 'include')
 q.update({'category':n[0],'direction':n[0],'method':n[1],'experiments':n[2], 'abstract_read':True,'evidence_level':'abstract','actual_reading':['Abstract (complete)','Official Submission history'] if hist else ['Abstract (complete)'],'full_text_read':False,'code_read':False,'code_executed':False,'window_class':wc,'decision':decision,'relevance_reason':n[1] if decision=='exclude' else '直接研究'+n[0]+'，核心做法：'+n[1], 'exclusion_reason':n[2] if decision=='exclude' else ('已报道同版本，保留原报告引用避免重复计数。' if same else None),'version_history':hist,'history_verified':h.get('history_verified',False),'history_evidence':h,'prior_history':old,'prior_same_version':prev,'limitations':'本次仅完整摘要与官方版本历史，未读全文/版本diff/源码，摘要结论是作者报告，未运行复现。','follow_up':'核原文实验设置、split、传感器/内参/尺度前提、硬件和全阶段运行时间，检查代码/许可；修订条目需版本diff。'})
 q['source_urls']=list(dict.fromkeys(q.get('source_urls',[])+[f'https://arxiv.org/abs/{i}{key}']))
 out.append(q)
manifest=[]
for fn in ['main-search-manifest.json','main-advanced-manifest.json']:
 for x in load(fn):
  if x.get('family','').startswith('A-'):manifest.append({**x,'inherited_evidence_from':fn})
result={'schema_version':1,'run_at':END,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage_start_utc':START,'coverage_end_utc':END,'scope':'Core A-family SLAM/VIO/SfM/odometry/relocalization/registration/backend and adjacent sensors','status':'complete_for_assigned_candidates' if len(H)>=len(S) else 'in_progress','query_manifest':manifest,'tool_failures':[{'tool':'sider_scholar_arxiv_search','query':'A title/abstract boolean AND submittedDate:[202610240817 TO 202611011459]','started':'2026-11-01','status':'aborted_after_1171.7_seconds_without_response','total':None,'fetched':0,'exhausted':False,'fallback':'Main agent official Atom+Advanced full inventory; official abs histories via native Python urllib'}],'counts':{'candidates':len(out),'complete_abstracts':len(out),'official_histories_verified':sum(x['history_verified'] for x in out),'decisions':dict(collections.Counter(x['decision'] for x in out)),'time_classes':dict(collections.Counter(x['window_class'] for x in out))},'papers':out}
(P/'core-search.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result['counts'],ensure_ascii=False))
