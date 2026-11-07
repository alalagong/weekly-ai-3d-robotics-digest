import json,re,shutil,importlib.util,collections,datetime
from pathlib import Path
from html import escape as e
ROOT=Path(__file__).resolve().parents[2]; P=Path(__file__).parent; PREFIX='2026-10-24_2026-11-01'
def load(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def save(f,x):Path(f).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def read(n):return load(P/n)
def render(x):
    if x is None:return '未提供'
    if isinstance(x,bool):return '是' if x else '否'
    if isinstance(x,list):return '<ul>'+''.join('<li>'+render(v)+'</li>' for v in x)+'</ul>'
    if isinstance(x,dict):
        if 'text' in x:return render(x['text'])+(' <small>'+', '.join('<a href="'+e(u)+'">正文证据</a>' for u in x.get('evidence_urls',[]))+'</small>' if x.get('evidence_urls') else '')
        return '<dl>'+''.join('<dt>'+e(str(k))+'</dt><dd>'+render(v)+'</dd>' for k,v in x.items() if k not in ['sources','raw_path'])+'</dl>'
    s=str(x)
    if s.startswith('https://') and ' ' not in s:return '<a href="'+e(s)+'">'+e(s)+'</a>'
    return e(s)
def row(cells,anchor=None):return '<tr'+(' id="'+e(anchor)+'"' if anchor else '')+'>'+''.join('<td>'+x+'</td>' for x in cells)+'</tr>'
ledger=load(ROOT/'reports'/f'{PREFIX}_paper-ledger.json'); papers=ledger['papers']; by={r['id']:r for r in papers}
deep=read('core-deep.json')['papers']+read('geometry-deep.json')['papers']+read('main-deep.json')['papers']
overrides={}
for n in ['main-chinese-detail-overrides.json','presentation-final-overrides.json']:
    if (P/n).exists():
        for r in read(n)['papers']:overrides.setdefault(r['id'],{}).update(r)
legacy={r['id']:r for r in read('main-legacy-report-inspections.json')}
for r in papers:
    if r['id'] in ['2604.23018','2610.28465']:
        r['category']='simulation-evaluation';r['direction']='simulation-evaluation';r['category_review_reason']='完整摘要核对：资产库/仿真平台及评测为主要问题。'
    o=overrides.get(r['id'],{})
    for k in ['problem','experiments']:
        if o.get(k):r[k]=o[k]
    if o.get('takeaway_override'):r['takeaway']=o['takeaway_override']
    if r['id'] in legacy:
        r['legacy_report_inspection']=legacy[r['id']];r['original_report']=legacy[r['id']]['original_report']
deep_rows=[]; assets=[]
for d in deep:
    r=by[d['id']];r['disposition']='deep_read';r['evidence_level']='full_text';r['actual_reading']=d.get('actual_reading',d.get('actual_read_sections',d.get('read_sections')));r['deep_read_evidence_path']=str(P.relative_to(ROOT)/('core-deep.json' if d in deep[:3] else 'geometry-deep.json' if d in deep[3:7] else 'main-deep.json')).replace('\\','/')
    fig=d.get('overview_figure',d.get('system_figure',d.get('figure',{})));img=''
    path=fig.get('path',fig.get('local_path'))
    if path and (fig.get('visually_verified') or fig.get('visual_verified')):
        src=Path(path);src=src if src.is_absolute() else P/src
        dest=ROOT/'reports/assets'/f'{PREFIX}_{d["id"]}_overview{src.suffix}';shutil.copyfile(src,dest);assets.append(str(dest.relative_to(ROOT)))
        href=fig.get('url',fig.get('source_url'));img='<a href="'+e(href)+'"><img style="max-width:240px;width:100%;height:auto" src="assets/'+dest.name+'" alt="'+e(fig.get('caption','系统总览'))+'"></a><p>'+e(fig.get('figure_number',fig.get('figure_id','')))+' · 原图已视觉确认</p>'
    else:img='<a href="'+e(fig.get('body_figure_position_url',d.get('source_url','https://arxiv.org/html/'+d['id']+'v'+str(d['version']))))+'">方法正文位置</a><p>未发现经确认的总览图，不嵌结果图。</p>'
    citation='<a href="https://arxiv.org/abs/'+r['id']+'v'+str(r['version'])+'">'+e(r['title'])+'</a><p>'+e(r['window_class'])+' · '+r['id']+'v'+str(r['version'])+'</p><small>v1 '+str(r['v1_utc'])+'<br>updated '+str(r['updated_utc'])+'</small>'
    exp=d.get('experiments',d.get('table_findings'))
    cautions=d.get('protocol_cautions',d.get('experimental_protocol',[]))
    deep_rows.append(row([citation,img,render(d.get('problem')),render(d.get('method_structure',d.get('method'))),render(d.get('math_insight',d.get('insight_math'))),render(exp)+render(cautions)+render(d.get('ablation_analysis',d.get('ablation_controls',[]))),render(d.get('reproduction_insight',d.get('reproduction')))+render(d.get('limitations',d.get('coverage_limitations',[]))),render(r['actual_reading'])+'<p>全文及所列附录阅读；未运行、未下载权重/数据。期内旧文版本未逐段比较新旧正文，不能据此称重大修订。</p><a href="'+e(r['deep_read_evidence_path'].removeprefix('reports/'))+'">逐项证据与原文定位</a>'],r['report_anchor']))
tracking=[r for r in papers if r['disposition'] in ['supplemental','revision_tracking']]
names={'slam-vio':'SLAM / VIO','localization-registration':'定位、配准与 SfM','geometry-foundation':'几何基础模型与前馈 / 流式 3D','gaussian-reconstruction':'3DGS、神经重建与渲染','semantic-mapping':'语义与开放词汇地图','embodied-navigation':'具身与视觉语言导航','world-model':'世界预测模型','world-action':'世界动作模型','simulation-evaluation':'仿真与评测','sensor-applications':'传感器感知与机器人应用','spatial-understanding':'三维空间理解'}
presentation={'schema_version':1,'run_at':ledger['run_at'],'categories':[{'id':k,'label':v,'description':'以'+v+'为主要研究问题；跨方向关系见每篇详情，所有条目至少已读完整摘要。'} for k,v in names.items() if any(r['category']==k for r in tracking)],'papers':[{'id':r['id'],'category':r['category'],'takeaway':r['takeaway'],'priority':bool(r.get('priority')),'priority_reason':r.get('priority_reason','')} for r in tracking]}
save(ROOT/'reports'/f'{PREFIX}_presentation.json',presentation)
spec=importlib.util.spec_from_file_location('supp',ROOT/'reports/templates/render_supplemental.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);nav,groups,suppstats=mod.build(ledger,presentation)
manifest_sources=['main-search-manifest.json','main-advanced-manifest.json','main-category-manifest.json','extension-manifest.json','extension-advanced-manifest.json','extension-advanced-applications-manifest.json','review-query-manifest.json','main-cross-manifest.json','main-enrichment-manifest.json','review-enrichment-manifest.json','core-deep-cross-manifest.json','review-project-manifest.json','repo-manifest.json']
manifest={'schema_version':2,'run_at':ledger['run_at'],'coverage_start_exclusive':ledger['coverage_start_exclusive'],'coverage_end_inclusive':ledger['coverage_end_inclusive'],'query_sources':{n:read(n) for n in manifest_sources},'recovered_failures':{},'independent_review':read('review-summary.json'),'boundary':'查询族范围内分页耗尽；领域召回率不可证明。API lastUpdatedDate语义与submittedDate相同，修订覆盖采用Advanced latest替代。分类公告仅交叉发现，不用其日期代替Submission history。观察时间晚于run_at的元数据不改变版本截止时间。'}
for n in ['main-advanced-parser-failures.json','review-enrichment-initial-attempts.json','repo-connector-attempts.json','main-official-histories-initial.json']:
    if (P/n).exists():manifest['recovered_failures'][n]={'path':str((P/n).relative_to(ROOT)).replace('\\','/'),'data':read(n),'resolution':'见最终对应manifest/official histories；失败不作为零结果依据。'}
save(ROOT/'reports'/f'{PREFIX}_search-manifest.json',manifest)
counts=collections.Counter(r['disposition'] for r in papers);inc=[r for r in papers if r['disposition']!='excluded' and r['disposition']!='unresolved'];windows=collections.Counter(r['window_class'] for r in inc)
ledger['stats'].update(dispositions=dict(counts),included_history_verified=sum(r.get('history_verified',False) for r in inc),deep_read_count=len(deep),supplemental_tracking_count=len(tracking),legacy_mentions_need_inspection=[],legacy_inspection_closed_ids=list(legacy));ledger['coverage_status']='awaiting_final_validation';save(ROOT/'reports'/f'{PREFIX}_paper-ledger.json',ledger)
repos=read('repo-audits.json');repo_rows=[]
for r in repos['repos']:
    repo_rows.append(row(['<a href="'+r['url']+'">'+r['name']+'</a><p>'+e(r['sha'])+'</p><p>'+str(r['stars'])+' stars / '+str(r['forks'])+' forks；快照 '+repos['snapshot_at']+'</p>',render(r['goal'])+render(r['temporal_evidence']),render(r['structure'])+render(r['code_evidence'])+render(r['insight']),render(r['dependencies']),render(r['maturity']),render(r['relation'])]))
evidence=[row(['候选集合与版本','2,486 = 8 全文 + '+str(counts['supplemental'])+' 摘要补充 + '+str(counts['revision_tracking'])+' 修订跟踪 + 2,037 排除 + 0 未解决。449 个相关版本均核对官方Submission history。','新文252；旧文更新123；历史补漏64；历史版本补跟踪10。','历史已报道同版本以 excluded/already-covered 引用原报告；37个审计种子逐项核销。']),row(['A / B / C 检索覆盖','主检索9族×首次/更新；独立10条不同词查询；官方4分类；API与Advanced互补。全部有效查询分页耗尽。','主池1,290；独立发现1,404（其中1,193不在主池），最终并集2,486。','检索边界是关键词、渠道与时间谓词；不代表全领域零遗漏。']),row(['独立复核','写前独立重新发现并逐项对账，937个程序预筛标题后来均人工复看；69个独立完整摘要核查。','review-summary.json、review-all-dispositions.json；无未处置核心漏项。','写后检查另存validation附件；已知回溯条目不冒充本期新文。']),row(['实际阅读','8篇全文/所列附录；441篇相关摘要；全候选中719个ID有完整摘要阅读标记。','2个仓库选定源码静态审计；原始总览图7张已视觉确认。','其余明显范围外项以标题/元数据排除并留理由，不伪装成摘要或全文已读。']),row(['审计附件','<a href="'+PREFIX+'_paper-ledger.json">逐ID ledger</a> · <a href="'+PREFIX+'_search-manifest.json">查询、分页与失败恢复 manifest</a> · <a href="'+PREFIX+'_presentation.json">分类展示映射</a>','<a href="'+PREFIX+'_work/review-summary.json">独立复核</a> · <a href="'+PREFIX+'_validation.json">最终验证</a>','链接发现与作者声明不能替代源码运行验证。'])]
quant=[row(['SVIn+','水下回访 / 返航','平均标记回访误差 / 返航端点距离，m','0.21±0.08 vs 0.53±0.11；返航0.52 vs0.81','两组指标不同；没有全局轨迹GT，不称ATE。']),row(['OctWorld v2','Re10K，80条最长往返轨迹','LPIPS / 归一化点云L1 Chamfer','0.1633 / 0.0345；Gen3C 0.1933 / 0.0457','Chamfer非米；VGGT重建，65536点并归一化；生成模型1.0配置。']),row(['OctWorld v2','模型1.0 / 1.5，WorldScore','总分 / 3D consistency','50.31→56.02；71.67→64.93','骨干、数据、训练同时变化；总分上升不能解释为几何一致性提升。']),row(['RESPLE2 / Any3R / HorizonStream','各论文自有协议','不跨协议汇总排名','详见全文行内Table与消融证据','RESPLE2区分轨迹/端点、IMU与异步全局优化；Any3R需要标定ray map；Horizon常量内存仅核心状态，不含可选回环。'])]
v={k:'' for k in re.findall(r'\{\{(.*?)\}\}',(ROOT/'reports/templates/slam-3d-weekly-template.html').read_text(encoding='utf8'))}
v.update(TITLE='RESPLE2 · GPA-VGGT · OctWorld：时序状态、几何效率与可验证边界',TITLE_KEYWORDS='RESPLE2-GPA-VGGT-OctWorld',COVERAGE_START='2026-10-24 16:17:58',COVERAGE_END='2026-11-01 22:59:32',COVERAGE_START_DATE='2026-10-24',COVERAGE_END_DATE='2026-11-01',DEEP_READ_COUNT='8',DEEP_READ_NAMES='RESPLE2、LingGS、SVIn+、GPA-VGGT、VGGT失败探测、Any3R、HorizonStream、OctWorld',SUPPLEMENTAL_COUNT=str(len(tracking)),SUPPLEMENTAL_NAMES='按11个主要研究问题完整归类，含旧文更新与历史补跟踪',REPO_COUNT='2',REPO_NAMES='RESPLE2 / GPA-VGGT',ACCESS_LIMITATIONS='未编译、训练、推理或下载权重/数据。GitHub连接器超时后以公开REST和固定提交源码补齐；无登录来源作为必需证据。',TAKEAWAY_1='连续时间状态的设计决定传感器融合边界。',EVIDENCE_BACKED_SUMMARY_1='RESPLE2以端点clamping和状态/协方差重置连接样条与IMU传播；SVIn+把声呐、压力等约束放入水下局部里程计。返航距离与全轨迹误差须分别判断。',TAKEAWAY_2='前馈几何开始按层、时间与可信度分工。',EVIDENCE_BACKED_SUMMARY_2='GPA-VGGT保留Q、按层处理K/V；HorizonStream将局部匹配与循环几何状态分开；Any3R用已标定射线统一相机。失败探测与性能加速分别需要独立评测。',TAKEAWAY_3='世界生成的记忆结构可以量化，但不能直接当作SLAM。',EVIDENCE_BACKED_SUMMARY_3='OctWorld用自适应OctMap重投影维护静态空间记忆；模型1.5总分提高的同时部分几何指标下降，且相机路径作为输入。',ACCESS_AND_EVIDENCE_BOUNDARY='UTC精确覆盖：(2026-10-24T08:17:58Z, 2026-11-01T14:59:32Z]。处理持续至后续日期，但版本窗口冻结；252新文、123修订、64历史补漏、10历史版本补跟踪分开计数。期内修订未比较新旧正文者不称重大修订。',DEEP_READ_PAPER_ROWS='\n'.join(deep_rows),REPO_DEEP_DIVE_ROWS='\n'.join(repo_rows),REPO_ACCESS_GAPS='源码审计仅覆盖列出的文件/选段。SVIn+项目README尚有冲突标记和待办，数据未发布；不计源码深读。Stars仅检索快照，不作为成熟度或升温证明。',QUANTITATIVE_ROWS='\n'.join(quant),SUPPLEMENTAL_CATEGORY_NAV=nav,SUPPLEMENTAL_CATEGORY_GROUPS=groups,TREND_TITLE_1='几何状态与实时路径需要分开评估',TREND_BODY_1='RESPLE2的递归状态、可选全局修正和HorizonStream的核心循环状态有不同资源边界。报告保留端点误差、整轨迹误差、局部状态内存和回环开销的区别。',TREND_TITLE_2='统一相机与可用置信度是两种不同问题',TREND_BODY_2='Any3R以标定射线描述像素几何，不能据此推断不需标定；VGGT失败探测研究的是预测能否识别失效，不能把原始置信度默认视为校准后的可靠性。',TREND_TITLE_3='世界模型需要显式报告几何代价',TREND_BODY_3='OctWorld长期轨迹受静态场景和GPU地图增长限制；DA3深度仍在模型1.5管线中。模块速度、完整生成FPS和下游导航能力应各自给证据。',LOW_EVIDENCE_TRENDS='摘要级世界动作、导航和机器人应用已完整跟踪，但未据摘要作统一优劣排名。441条摘要跟踪的具体协议、统计显著性、权重可用性与复现均保留逐ID待办。',EVIDENCE_ROWS='\n'.join(evidence),FOLLOW_UP_ITEMS=''.join('<li>'+s+'</li>' for s in ['按ledger逐ID补读摘要条目的实验协议，不把优先关注提示当全文认证。','先验证RESPLE2依赖/标定和GPA-VGGT独立进程基准；本轮没有本机性能结论。','对期内修订建立新旧正文差异；检查SVIn+公式7、数据发布与文中距离不一致。','下一轮从冻结UTC截止时间继续，重试失败来源并保留本轮历史版本进度。']),RAW_LINK_ITEMS=''.join('<li><a href="https://arxiv.org/abs/'+r['id']+'v'+str(r['version'])+'">'+e(r['title'])+' · '+r['id']+'v'+str(r['version'])+'</a></li>' for r in inc))
template=(ROOT/'reports/templates/slam-3d-weekly-template.html').read_text(encoding='utf8')
template=template.replace('</style>','table { display:block; max-width:100%; overflow-x:auto; } td { overflow-wrap:anywhere; min-width:180px; } dt { font-weight:600; } dd { margin:0 0 10px; } @media(max-width:820px) { table { max-width:100%; } th, td { min-width:220px; } } </style>')
for k,x in v.items():template=template.replace('{{'+k+'}}',str(x))
report=ROOT/ledger['report_path'];report.write_text(template,encoding='utf8');save(P/'build-result.json',{'report_path':ledger['report_path'],'assets':assets,'counts':dict(counts),'window_counts':dict(windows),'tracking':len(tracking),'supplemental_render_stats':suppstats,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps({'report':str(report),'counts':dict(counts),'tracking':len(tracking),'assets':len(assets)},ensure_ascii=False))
