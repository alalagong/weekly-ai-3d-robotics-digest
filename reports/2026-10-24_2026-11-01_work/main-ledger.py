import pathlib,json,re,collections,datetime
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parent.parent
PREFIX='2026-10-24_2026-11-01';RUN='2026-11-01T14:59:32Z';START='2026-10-24T08:17:58Z'
REPORT='reports/'+PREFIX+'_RESPLE2-GPA-VGGT-OctWorld.html'
def rd(n,default=None):
    f=P/n
    return json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else default
def rows(n):
    x=rd(n,[])
    if isinstance(x,dict):
        if 'papers' in x:return x['papers']
        if x and all(isinstance(v,dict) for v in x.values()):return [dict(v,id=k) for k,v in x.items()]
        return []
    return x
def save(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
history=json.loads((ROOT/'reports/paper-history.json').read_text(encoding='utf-8-sig'))['papers']
pool={};annotations=collections.defaultdict(list)
def ingest(rs,name,annotate=False):
    for r in rs:
        if not r.get('id'):continue
        ident=r['id'];item=pool.setdefault(ident,{'id':ident,'source_urls':[],'query_hits':[],'input_files':[]})
        for k in ['title','abstract','version','v1_utc','updated_utc']:
            if r.get(k) and not item.get(k):item[k]=r[k]
        item['source_urls']=list(dict.fromkeys(item['source_urls']+r.get('source_urls',[])))
        item['query_hits']=list(dict.fromkeys(item['query_hits']+r.get('query_hits',r.get('hit_queries',[]))))
        item['input_files']=list(dict.fromkeys(item['input_files']+[name]))
        if annotate:annotations[ident].append(dict(r,annotation_source=name))
ingest(rows('main-pool-enriched.json'),'main-pool-enriched.json')
ingest(rows('review-independent-unique.json'),'review-independent-unique.json')
ingest(rows('review-enrichment.json'),'review-enrichment.json')
for n in ['core-search.json','geometry-search.json','extension-screened.json','main-offscope-decisions.json','review-all-dispositions.json','review-candidates-screened.json']:
    ingest(rows(n),n,True)
# Independent C-channel discoveries outside the shared pool remain auditable.
for n in ['extension-search.json']:
    x=rd(n,[])
    if isinstance(x,dict):rs=x.get('papers',x.get('candidates',[]))
    else:rs=x
    ingest(rs,n,True)
official={}
for n in ['core-official-histories.json','extension-official-histories.json','review-official-histories.json','main-official-histories.json']:
    for r in rows(n):
        ident=r.get('id')
        if ident and r.get('history_verified',bool(r.get('version_history') or r.get('submission_history'))):official[ident]=r
catmap={'navigation':'embodied-navigation','localization':'localization-registration','registration':'localization-registration','matching-registration':'localization-registration','sfm':'localization-registration','calibration':'localization-registration','optimization':'localization-registration','feedforward-3d':'geometry-foundation','multi-view':'geometry-foundation','depth-geometry':'geometry-foundation','sensor-application':'sensor-applications','sensors-applications':'sensor-applications','simulation':'simulation-evaluation','semantic-map':'semantic-mapping','neural-reconstruction':'gaussian-reconstruction'}
includes={'include','included','supplemental','revision_tracking','deep_read'}
covered={'reference_previous','already_covered','already_reported_same_version','same_version_processed'}
out=[];conflicts=[]
for ident,item in pool.items():
    records=annotations.get(ident,[])
    incl=[r for r in records if r.get('disposition',r.get('decision')) in includes]
    cov=[r for r in records if r.get('disposition',r.get('decision')) in covered]
    exc=[r for r in records if r.get('disposition',r.get('decision')) in ['exclude','excluded']]
    # Prefer the annotation written for its field; the four C-scope conflicts were manually adjudicated.
    chosen=(incl[-1] if incl else cov[0] if cov else exc[0] if exc else records[0] if records else {})
    r=dict(item)
    for k in ['problem','method','insight_math','experiments','takeaway','priority','priority_reason','follow_up','category','direction','limitations','canonical_abstract_source','metadata_conflict','source_conflict','abstract_source_url','abstract']:
        if chosen.get(k) is not None:r[k]=chosen[k]
    r.update(abstract_read=any(a.get('abstract_read') for a in records),reading_sections=['Abstract (complete)'] if any(a.get('abstract_read') for a in records) else ['Title / official metadata'],annotation_sources=[a['annotation_source'] for a in records],annotation_decisions=[{'source':a['annotation_source'],'disposition':a.get('disposition',a.get('decision')),'reason':a.get('reason') or a.get('relevance_reason') or a.get('exclusion_reason')} for a in records])
    o=official.get(ident)
    if o:
        for k in ['version','v1_utc','updated_utc']:
            if o.get(k) is not None:r[k]=o[k]
        versions=o.get('submission_history',o.get('version_history',[]));r.update(history_verified=True,submission_history=versions,history_evidence=o)
        if not r.get('v1_utc') and versions:r['v1_utc']=next((v.get('utc') for v in versions if v.get('version')==1),None)
        if not r.get('updated_utc') and versions:r['updated_utc']=max((v.get('utc','') for v in versions),default=None)
        if not r.get('version') and versions:r['version']=max(v['version'] for v in versions)
    else:r['history_verified']=False
    for k in ['version','v1_utc','updated_utc']:r.setdefault(k,None)
    old=history.get(ident,{});vkey='v'+str(r['version']);prior=old.get('versions',{}).get(vkey)
    r['prior_same_version']=prior
    if prior and prior.get('status') in ['deep_read','supplemental','revision_tracking']:
        r.update(disposition='excluded',reason='already-covered: 精确ID+版本已在原报告处理；本轮保留检索命中与原报告引用，不重复计为历史补漏。',original_report=prior.get('report_path'),original_anchor=prior.get('report_anchor'),previous_evidence_level=prior.get('evidence_level'),evidence_level='abstract' if r['abstract_read'] else 'metadata_history')
    elif incl:
        r.update(disposition='supplemental',reason=chosen.get('reason') or chosen.get('relevance_reason') or '完整摘要确认属于报告范围；非固定篇数筛选。',evidence_level='abstract',report_anchor='paper-'+ident.replace('.','-'),report_path=REPORT)
        if not r['abstract_read']:r.update(disposition='unresolved',reason='In-scope annotation lacks confirmed complete abstract reading',evidence_level='metadata')
    elif cov or exc:
        reason=chosen.get('reason') or chosen.get('exclusion_reason') or chosen.get('relevance_reason') or '范围外，见逐项annotation_decisions。'
        if cov:
            original=chosen.get('prior_same_version') or chosen.get('previous_version_record') or prior or {}
            reason='already-covered / previously-processed: '+str(reason);r['original_report']=original.get('report_path') or chosen.get('original_report');r['original_anchor']=original.get('report_anchor')
        r.update(disposition='excluded',reason=reason,evidence_level='abstract' if r['abstract_read'] else chosen.get('evidence_level','metadata_title'))
    else:r.update(disposition='unresolved',reason='检索ID尚无人工范围处置，需续跑，不得推进覆盖边界。',evidence_level='metadata')
    if r['disposition'] in ['supplemental','deep_read','revision_tracking']:
        v1=r.get('v1_utc');upd=r.get('updated_utc')
        if v1 and START<v1<=RUN:w='new'
        elif upd and START<upd<=RUN:w='revised'
        elif v1 and v1>RUN:w='after_cutoff'
        elif old.get('versions') or old.get('legacy_mentions'):w='historical_revision_backfill'
        else:w='historical_backfill'
        r['window_class']=w
        if w=='revised':r['disposition']='revision_tracking';r['follow_up']=str(r.get('follow_up') or '')+' 未比较新旧正文时仅跟踪版本，不称重大修订。'
        if w=='after_cutoff':r.update(disposition='excluded',reason='首次提交晚于冻结run_at；保留发现，转下期时间窗口。')
        if not r.get('problem'):
            r['problem']='研究对象：'+r['title']+'；摘要所述具体结构与目标见方法条目。'
        if not r.get('insight_math'):r['insight_math']='摘要设计洞见：'+str(r.get('method',''))+' 数学推导、成立条件与优化细节未深读全文，不补写未给出的公式。'
        r['category']=catmap.get(r.get('category',r.get('direction')),r.get('category',r.get('direction')))
        r['direction']=r['category']
        if not r.get('takeaway'):
            s=str(r.get('method') or r['title']).strip();s=s if len(s)>=40 else s.rstrip('。')+'；本条基于完整摘要跟踪，具体协议与适用边界仍需全文核验。';r['takeaway']=s
        r.setdefault('experiments','摘要未提供可核验的具体数值；未深读全文。')
        r.setdefault('priority',False);r.setdefault('priority_reason','')
    else:r.setdefault('window_class',None);r.setdefault('report_anchor',None);r.setdefault('report_path',None)
    if incl and exc:conflicts.append({'id':ident,'resolution':r['disposition'],'reason':r['reason'],'records':r['annotation_decisions']})
    out.append(r)
out.sort(key=lambda r:r['id'])
counts=collections.Counter(r['disposition'] for r in out);included=[r for r in out if r['disposition'] in ['supplemental','revision_tracking','deep_read']]
stats={'candidates':len(out),'dispositions':dict(counts),'included':len(included),'included_windows':dict(collections.Counter(r['window_class'] for r in included)),'abstracts_read_unique':sum(r['abstract_read'] for r in out),'included_history_verified':sum(r['history_verified'] for r in included),'included_missing_history':[r['id'] for r in included if not r['history_verified']],'unresolved_ids':[r['id'] for r in out if r['disposition']=='unresolved'],'legacy_mentions_need_inspection':[r['id'] for r in included if history.get(r['id'],{}).get('legacy_mentions') and not history.get(r['id'],{}).get('versions')]}
ledger={'schema_version':2,'run_at':RUN,'coverage_start_exclusive':START,'coverage_end_inclusive':RUN,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage_status':'in_progress_reading_and_validation','report_path':REPORT,'count_definitions':'Candidate universe is deduplicated union of all primary and independent discovery IDs; categories and exclusion evidence are explicit. Not a domain recall denominator.','stats':stats,'papers':out}
save(ROOT/'reports'/f'{PREFIX}_paper-ledger.json',ledger);save(P/'main-scope-conflict-reconciliation.json',conflicts);save(P/'main-ledger-stats.json',stats)
print(json.dumps(stats,ensure_ascii=False,indent=2))
