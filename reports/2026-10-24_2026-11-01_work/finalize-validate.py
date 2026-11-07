import json,re,collections,datetime,hashlib
from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import html
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).parent;PREFIX='2026-10-24_2026-11-01'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
ledgerpath=ROOT/'reports'/f'{PREFIX}_paper-ledger.json';L=load(ledgerpath);R=ROOT/L['report_path'];text=R.read_text(encoding='utf8');doc=html.fromstring(text);papers=L['papers'];inc=[r for r in papers if r['disposition'] in ['deep_read','supplemental','revision_tracking']];track=[r for r in inc if r['disposition']!='deep_read'];pres=load(ROOT/'reports'/f'{PREFIX}_presentation.json');errors=[];checks={}
def ck(name,passed):checks[name]=bool(passed);errors.extend([] if passed else [name])
ck('candidate_count_closure',len(papers)==sum(collections.Counter(r['disposition'] for r in papers).values())==2486)
ck('unique_base_ids',len({r['id'] for r in papers})==len(papers))
ck('no_unresolved',all(r['disposition']!='unresolved' for r in papers))
ck('all_included_abstract_and_history',all(r.get('abstract_read') and r.get('history_verified') for r in inc))
ck('excluded_reasons',all(r.get('reason') for r in papers if r['disposition']=='excluded'))
ck('exact_report_id_set',set(doc.xpath('//*[@id]/@id'))&{r['report_anchor'] for r in inc}=={r['report_anchor'] for r in inc})
ck('unique_html_ids',len(doc.xpath('//*[@id]/@id'))==len(set(doc.xpath('//*[@id]/@id'))))
ck('presentation_id_closure',{r['id'] for r in track}=={r['id'] for r in pres['papers']} and len(track)==len(pres['papers'])==441)
ck('takeaway_length',all(40<=len(r['takeaway'])<=100 for r in pres['papers']))
ck('priority_reasons',all(not r['priority'] or r.get('priority_reason') for r in pres['papers']))
ck('no_placeholders','{{' not in text and 'SUPPLEMENTAL_PAPER_ROWS' not in text)
ck('nine_sections',len(doc.xpath('//main/section'))==9)
ck('all_detail_fields',all(len(x.xpath('./div[@class="tracking-paper-body"]//dt'))>=6 for x in doc.xpath('//details[contains(@class,"tracking-paper")]')))
ck('native_nojs_degradation',len(doc.xpath('//details[contains(@class,"tracking-paper")]'))==441 and not doc.xpath('//details[contains(@class,"tracking-paper")][@hidden]'))
missing=[]
for u in doc.xpath('//@href|//@src'):
    parts=urlsplit(u)
    if parts.scheme or parts.netloc or not parts.path:continue
    f=(R.parent/unquote(parts.path)).resolve()
    if f.name==f'{PREFIX}_validation.json':continue
    if not f.exists():missing.append(u)
ck('local_links_and_assets',not missing)
for name in ['main-search-manifest.json','main-advanced-manifest.json','main-category-manifest.json','extension-manifest.json','extension-advanced-manifest.json','extension-advanced-applications-manifest.json','review-query-manifest.json']:
    ck('pagination_'+name,all(x.get('exhausted') for x in load(P/name)))
review=load(P/'review-summary.json');ck('independent_rediscovery',review['independent_discovery_completed_before_main_pool_read'] and review['unique_ids']==1404 and review['queries_exhausted'])
ck('geometry_fulltext_validation',load(P/'geometry-deep-validation.json')['passed'])
out={'run_at':L['run_at'],'validated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':not errors,'checks':checks,'errors':errors,'missing_local_links':missing,'stats':L['stats'],'browser_checks':load(P/'browser-validation.json') if (P/'browser-validation.json').exists() else {'status':'pending'},'nojs_limit':'原生details/summary与无hidden条目的静态退化已检查；未在禁用JS浏览器实测。','external_link_limit':'源链接获取证据保存在manifest；未对所有449条外链重新请求，避免把后续站点状态混为冻结窗口证据。'}
save(ROOT/'reports'/f'{PREFIX}_validation.json',out)
print(json.dumps({'passed':not errors,'errors':errors,'checks':len(checks),'missing':missing},ensure_ascii=False))
if errors:raise SystemExit(1)
if out['browser_checks'].get('passed') is not True:raise SystemExit('browser validation pending')
L['coverage_status']='complete_with_known_limits';save(ledgerpath,L)
H=load(ROOT/'reports/paper-history.json')
for r in inc:
    entry=H['papers'].setdefault(r['id'],{'id':r['id'],'legacy_mentions':[],'versions':{}});versions=entry.setdefault('versions',{});key='v'+str(r['version']);old=versions.get(key)
    record={'version':r['version'],'status':r['disposition'],'evidence_level':r['evidence_level'],'report_path':L['report_path'],'report_anchor':r['report_anchor'],'v1_utc':r['v1_utc'],'updated_utc':r['updated_utc'],'run_at':L['run_at'],'abstract_read':True,'reading_sections':r.get('actual_reading', ['abstract']),'follow_up':r.get('follow_up') or '核对发布权重/数据及本机复现；本轮未运行。','ledger_path':str(ledgerpath.relative_to(ROOT)).replace('\\','/')}
    if old and old.get('report_path')!=L['report_path']:record['previous_processing_record']=old
    versions[key]=record
    if r.get('legacy_report_inspection'):entry['legacy_inspection']=r['legacy_report_inspection']
H['generated_at']=out['validated_at'];H.setdefault('runs',[])
if isinstance(H['runs'],list) and not any(isinstance(r,dict) and r.get('run_at')==L['run_at'] for r in H['runs']):H['runs'].append({'run_at':L['run_at'],'report_path':L['report_path'],'ledger_path':str(ledgerpath.relative_to(ROOT)).replace('\\','/'),'stats':L['stats']})
save(ROOT/'reports/paper-history.json',H)
S=load(ROOT/'.cache/slam-3d-state.json');prev={k:S.get(k) for k in ['run_at','coverage_start','coverage_end','report_path','ledger_path','search_manifest_path','coverage_status']}
if S.get('coverage_end')!=L['run_at']:S.setdefault('coverage_history',[]).append(prev)
S.update(run_at=L['run_at'],coverage_start=L['coverage_start_exclusive'],coverage_end=L['coverage_end_inclusive'],report_path=L['report_path'],ledger_path=f'reports/{PREFIX}_paper-ledger.json',search_manifest_path=f'reports/{PREFIX}_search-manifest.json',presentation_path=f'reports/{PREFIX}_presentation.json',paper_history_path='reports/paper-history.json',validation_path=f'reports/{PREFIX}_validation.json',coverage_status='complete_with_known_limits',last_refresh_at=out['validated_at'],backlog={'unresolved_count':0,'ids':[],'evidence_followups_path':'reports/paper-history.json','access_limits':['未下载数据/权重或运行代码；441摘要条目保留全文待办。','SVIn+数据待发布、LingGS源码待发布；不计源码深读。','2610.37330官方abs/Atom摘要错配，使用同版本官方HTML摘要并保留原始冲突。'],'independent_review_status':'独立重新发现1404并全处置，写后独立集合/数字复核通过；见work/review-final-check.json。'},git_delivery={'target':'origin/main','report_run_at':L['run_at'],'result_path':f'reports/{PREFIX}_work/git-delivery.json','status':'pending_commit_push'})
save(ROOT/'.cache/slam-3d-state.json',S)
index=ROOT/'reports/index.html';s=index.read_text(encoding='utf8');name=R.name
if name not in s:
    item='<article class="report"><a href="./'+name+'">2026-10-24 至 2026-11-01：RESPLE2、GPA-VGGT 与 OctWorld</a><p>全文深读8篇、摘要/修订跟踪441篇、源码静态审计2个。候选2486、排除2037、未决0；新文252 / 修订123 / 历史补漏64 / 历史版本补跟踪10。关键词查询分页与独立重新发现已对账；不承诺领域零遗漏。</p></article>\n\n    '
    s=s.replace('<article class="report">',item+'<article class="report">',1);index.write_text(s,encoding='utf8')
