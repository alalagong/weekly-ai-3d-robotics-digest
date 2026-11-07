import pathlib,json,re,datetime,collections
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat();START='2026-10-24T08:17:58Z';END='2026-11-01T14:59:32Z'
allrows=read('review-independent-unique.json');main={x['id']:x for x in read('main-pool-enriched.json')};off={x['id']:x for x in read('main-offscope-decisions.json')};potential={x['id'] for x in read('review-independent-potential.json')};hist=read('review-official-histories.json');notes=read('review-notes.json');history=json.loads((P.parent/'paper-history.json').read_text(encoding='utf8'))['papers'];rows={x['id']:x for x in allrows}
reject={
'2610.40530':'PhysCount研究单张图像的外观与物理实体计数，未建立三维重建、地图、位姿或具身导航任务；排除通用二维视觉推理。',
'2610.39609':'DiFuse融合扩散特征改善通用空间推理，摘要未建立三维几何表示、建图、导航或相关世界动力学；排除通用多模态VQA。',
'2610.32220':'Angular Supervision研究二维目标grounding和分割热图，摘要不涉及三维几何、地图或导航。',
'2610.31490':'多波束声呐去斑去模糊恢复强度图像；虽利用已配准序列，摘要未求解配准、位姿、三维几何或闭环导航，排除传感器图像增强邻接任务。',
'2610.36785':'OmniGlimpse维护多视图目标身份，明确无需相机标定；摘要不恢复三维位置、几何、相机轨迹或地图，排除纯身份关联。',
'2610.35417':'Homogeneity Pursuit对三维点云做统计组结构估计并应用阿尔茨海默医学影像；不涉及定位重建、空间建图或具身任务。',
'2610.37309':'MvT的多视图为事件时空投影，统一坐标包含时间轴；摘要目标是二维多目标轨迹关联，不是物理三维重建或多相机几何。',
'2610.33764':'视觉子集选择与网格寻路的多证据整合诊断，摘要未涉及真实三维、相机几何、导航感知或地图构建。'
}
def topic(t):
 rules=[(r'quantum|quark|fermion|boson|black.hole|schr[oö]dinger|gravity|gravitational|cosmic|cosmolog|galaxy|stellar|nebula|solar|coronal|magnet|superconduct|higgs|nucleon|kitaev|spin.chain|qcd|scattering','物理天体与量子系统'),(r'theorem|algebra|cohomolog|liouville|sobolev|navier|hilbert|riemann|yangian|gabor|quiver|semidual|bernstein|gibbs|l[eé]vy|poincar|cft|hjb|porous|superprocess|eigenvalue|manifold|calder|oscillatory|equation|tensor.triangular|rational|semigroup|isomorphism|calculus','数学与连续系统'),(r'medical|mri|pet/ct|fmri|prostate|pulmonary|stroke|omics|chromatin|drug|bacteria|biom|proteomic|holography|lumpectomy|connectome|brain|neuro|neuronal','医学生命与非几何成像'),(r'speaker|speech|audio|acoustic|music|sentiment|lip.focus|video.ground|action.recognition|motion.transfer|object.tracking|count|vqa|visual.understanding|grounding','二维视听感知与通用视觉理解'),(r'grasp|manipulat|dexter|hand|retarget|robot|swarm|motion.primitive|policy|vla','机器人控制或操作邻接任务'),(r'3d.asset|cad|3d.generation|articulated.3d|rigging|3d.macromolecule','物体资产生成或非场景三维任务'),(r'weather|precip|thermal.dust|ionosph|fire.segment|remote.sensing','气象遥感与地球系统')]
 return next((v for pat,v in rules if re.search(pat,t,re.I)),'其他非目标研究对象')
screened=[]
for i,h in hist.items():
 r=dict(rows[i]);r.update({'history_evidence':h,'version_history':h['version_history'],'history_verified':h['history_verified'],'evidence_level':'abstract','reading_level':'complete abstract + official submission history','abstract_read':True,'read_sections':['Abstract (complete; independent review)','Official submission history'],'reviewed_at':NOW})
 eligible=[v for v in h['version_history'] if v['utc']<=END];v=max(eligible,key=lambda v:v['version']);v1=min(h['version_history'],key=lambda v:v['version']);r.update({'version':v['version'],'v1_utc':v1['utc'],'updated_utc':v['utc'],'source_urls':list(dict.fromkeys(r['source_urls']+['https://arxiv.org/abs/'+i+'v'+str(v['version'])]))})
 prior=history.get(i,{});processed=prior.get('versions',{}).get('v'+str(v['version']));r['original_report']=processed or None;r['previously_processed_versions']=prior.get('versions',{})
 r['window_class']='new' if START<v1['utc']<=END else ('revised' if START<v['utc']<=END else 'historical_backfill')
 if processed:r.update({'disposition':'excluded','reason':'already-covered: 当前精确版本已处理；引用原报告，不重复计本期跟踪。','exclusion_topic':'already-covered','status':'already_covered'})
 elif i in notes:
  r.update(notes[i]);r.update({'disposition':'included','reason':'独立发现的新ID；研究问题直接涉及'+r['category']+'，纳入摘要跟踪。','status':'revision_tracking' if r['window_class']=='revised' else 'supplemental','follow_up':'未读论文全文、未运行；核对原表、数据划分、输入、硬件及公开资产。修订项未逐版全文比较。'})
 else:r.update({'disposition':'excluded','reason':reject[i],'exclusion_topic':'adjacent_out_of_scope','status':'excluded'})
 if i in ('2610.40525','2609.03919','2610.30799'):
  r['read_sections'].append('Official project page' if i!='2610.30799' else 'Official repository README');r['reading_level']+=' + official project page / README';r['project_evidence_file']='review-project-'+i+'.txt'
 screened.append(r)
save('review-candidates-screened.json',screened);smap={x['id']:x for x in screened}
dispositions=[]
for r in allrows:
 i=r['id'];d={k:r[k] for k in ('id','title','query_hits','source_urls')};d['reviewed_at']=NOW
 if i in smap:
  s=smap[i];d.update({k:s.get(k) for k in ('disposition','reason','evidence_level','version','v1_utc','updated_utc','window_class','original_report')});d['resolution_reference']='review-candidates-screened.json#'+i
 elif i in main:
  m=main[i];d.update({'version':m['version'],'v1_utc':m['v1_utc'],'updated_utc':m['updated_utc'],'disposition':'existing_main_pool','reason':'独立检索命中已在主候选池，引用原集合后续纳排，不重复创建记录。','evidence_level':'metadata_title','resolution_reference':'main-pool-enriched.json#'+i})
  if i in off:d.update({'disposition':'excluded','reason':off[i]['reason'],'resolution_reference':'main-offscope-decisions.json#'+i})
  prior=history.get(i,{}).get('versions',{}).get('v'+str(m['version']))
  if prior:d.update({'disposition':'excluded','reason':'already-covered: 主池当前精确版本已在原报告处理。','original_report':prior,'resolution_reference':'reports/paper-history.json#'+i+'/v'+str(m['version'])})
 elif i in potential:
  tp=topic(r['title']);d.update({'disposition':'excluded','reason':'题名实质为'+tp+'；《'+r['title']+'》未以相机/机器人定位、环境几何重建、SLAM或直接相关空间地图/世界模型为研究对象。仅题名与元数据排除，不声称全文或完整摘要阅读。','evidence_level':'metadata_title','exclusion_topic':tp,'resolution_reference':'review-independent-unique.json#'+i})
 else:
  d.update({'disposition':'excluded','reason':'独立all字段宽检索的非目标命中；自动预筛题名及摘要文本均无SLAM/重建/定位/相机/深度/物理3D/机器人导航/世界模型等研究对象词，题名为《'+r['title']+'》。保留原始文本以便追溯，不声称人工完整摘要阅读。','evidence_level':'metadata_programmatic','exclusion_topic':topic(r['title']),'resolution_reference':'review-independent-unique.json#'+i})
 dispositions.append(d)
save('review-all-dispositions.json',dispositions)
newpot=[x for x in dispositions if x['id'] in potential and x['id'] not in main];save('review-256-dispositions.json',newpot)
seeds=[]
for s in read('main-audit-seeds.json'):
 i=s['id'];m=main[i];prior=history.get(i,{}).get('versions',{}).get('v'+str(m['version']));seeds.append({'id':i,'version':m['version'],'updated_utc':m['updated_utc'],'official_metadata_reference':'main-pool-enriched.json#'+i,'disposition':'excluded' if prior else 'needs_review','reason':'already-covered: 当前精确版本已在原报告处理，原审计seed不能重复视作本期新文。' if prior else '未找到当前精确版本原报告记录','original_report':prior,'source':'main-audit-seeds.json','evidence_level':'official_metadata + version_history_record; no new full-text claim'})
save('review-37-seed-reconciliation.json',seeds)
summary={'reviewed_at':NOW,'coverage_start_exclusive':START,'coverage_end_inclusive':END,'independent_discovery_completed_before_main_pool_read':True,'query_count':len(read('review-query-manifest.json')),'query_rows':sum(q['fetched'] for q in read('review-query-manifest.json')),'queries_exhausted':all(q['exhausted'] for q in read('review-query-manifest.json')),'unique_ids':len(dispositions),'overlap_main':sum(x['id'] in main for x in dispositions),'outside_main':sum(x['id'] not in main for x in dispositions),'potential_ids':len(potential),'potential_outside_main':len(newpot),'complete_abstracts_read':len(screened),'included_new_candidates':sum(x['disposition']=='included' for x in screened),'all_disposition_counts':dict(collections.Counter(x['disposition'] for x in dispositions)),'seed_count':len(seeds),'seeds_exact_version_already_covered':sum(x['disposition']=='excluded' for x in seeds),'limitations':['937 non-target all-field hits resolved by transparent programmatic title/abstract vocabulary prefilter, not manual complete abstract reading.','Metadata title exclusions do not claim abstract or full-text reading.','Official updated histories govern time attribution; search result display date may differ by one day.','No paper full texts or executable source internals read in this independent review; 3 project/README pages read.']}
assert len(dispositions)==len({x['id'] for x in dispositions})==1404
assert len(newpot)==256 and len(screened)==24
assert all(x['disposition'] in ('included','excluded','existing_main_pool') for x in dispositions)
assert all(40<=len(x['takeaway'])<=100 for x in screened if x['disposition']=='included')
save('review-summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
