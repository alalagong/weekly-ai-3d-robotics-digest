import pathlib,json,re,time,datetime,collections,html
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parent.parent
def read(n,default=None):
 try:return json.loads((P/n).read_text(encoding='utf-8-sig'))
 except FileNotFoundError:return default
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
notes={}
for line in (P/'extension-notes.txt').read_text(encoding='utf8').splitlines():
 if line.strip():ident,cat,txt=line.split('|',2);notes[ident]=(cat,txt)
exclusions={
'2610.30657':'社会协商、合作与调解的回应分布预测，无机器人、空间仿真或定位建图任务。',
'2610.30932':'电商购物和用户行为推荐模拟，无具身空间、机器人或三维建图关系。',
'2610.33263':'篮球投篮视频分类及Grad-CAM捷径审计；非导航、三维或机器人世界模型。',
'2610.33616':'二维图像压缩中的语义频率调制，semantic map仅作编码先验，无空间建图任务。',
'2610.34523':'ARC-AGI-3符号游戏的认知口述研究，无三维空间仿真或机器人导航建图方法。',
'2610.34797':'零售和网络等通用时序预测，文本干预不对应具身空间或机器人动作。',
'2610.34943':'AI编程推理模式；semantic mapping指代码翻译而不是空间语义建图。',
'2610.35813':'动态超表面天线波束与能效优化，世界状态为无线信道而非机器人空间导航。',
'2610.37175':'预测机器学习程序的训练日志和验证分数，world model是ML实验执行代理。',
'2610.37391':'无线MIMO信道重建，潜在传播场不是三维场景重建或机器人定位。',
'2610.37937':'图像分类知识蒸馏的随机原型空间，未涉及空间几何、定位或机器人世界模型。',
'2610.37963':'天气、网络流量及语音等时序表示学习，不是具身交互世界模型。',
'2610.38289':'肺炎临床病程状态与医疗决策预测，无机器人、空间仿真或三维感知方法。',
'2610.38439':'机器学习代码候选的直接排序奖励模型，非机器人世界状态或导航规划。',
'2610.39014':'二维真假图像统计可分性，semantic map为图像抽象而非空间地图。',
'2610.40503':'ARC-AGI-3符号规则和Lean形式证明，无三维/机器人/导航建图贡献。',
'2610.33669':'条件密度回归的贝叶斯混合模型；空间关键词为统计描述而非机器人几何。',
'2610.33715':'量子机械臂逆运动学数学表示，无感知建图、定位、导航或世界模型环节。',
'2610.33965':'内窥镜胃肠疾病二维分类与效率评测，无相机定位、三维重建或路径导航。',
'2610.36146':'二维文生图提示编辑及关系忠实性，场景图未形成三维空间或机器人任务表示。',
'2610.36881':'无线CSI检索预测，无机器人定位、空间地图或具身世界模型任务。',
'2610.38879':'回归方差分配的统计先验，非三维感知或导航。',
'2610.39183':'水下二维颜色及细节增强，未评价定位、建图、导航或三维重建。',
'2610.40066':'经典平带量子度量物理，localization指波动局域化而非机器人定位。',
'2610.40648':'超导Friedel振荡和电子结构物理，point map检索同词歧义，无空间重建导航。',
'2505.07687':'医学多模态影像合成，三维结构一致性是器官影像质量，未含相机定位、导航或场景重建。',
'2512.24036':'量子修正黑洞的引力波与轨道物理，metric scaling是时空度规而非视觉尺度恢复。',
'2602.00414':'实验室危险识别的二维图像与场景图推理，未建立三维环境图或机器人导航系统。',
'2606.04689':'Visual Genome二维关系图的量子谓词分类，非三维语义地图或具身导航。',
'2607.21620':'个性化文本生成的全局局部激活引导，非机器人空间定位。',
'2608.12290':'通用图生视频提示与随机参数搜索，二维语义遵循不涉及动作条件空间仿真。',
'2610.31149':'老年照护HRI设计综述，讨论界面、隐私与部署，摘要未提供定位建图或导航/world模型方法。',
'2610.33054':'癌症患者临床事件及影像的病程世界模型，无机器人、空间仿真或三维场景方法。',
'2610.37926':'Overcooked和SMAX的通用多代理奖励程序设计，无机器人、三维空间或定位建图贡献。',
'2609.17419':'LLM工具与谜题错误动力学的统计研究；虽混合具身样例，摘要无独立空间/导航/world仿真方法。',
'2610.30448':'计算机DRAM空间访存预取器，spatial memory与机器人空间记忆同名但无领域关系。',
'2606.31689':'Scratch二维程序执行后果评测，不涉及三维场景或机器人导航建图。',
'2609.40003':'Geometry Dash二维跳跃游戏控制，无三维空间、机器人或地图定位关系。',
'2610.00012':'模块化LLM工具系统的因果预测理论，未提供机器人、导航或三维空间实验。',
'2506.07450':'通用零样本多代理协调的种群训练，摘要未给三维/机器人/导航相关实验或任务。',
'2606.03371':'零售销售辅助的客户意图和干预决策，world model为社会回应预测，无机器人空间方法。'
}
exclusions.update(read('extension-extra-exclusions.json',{}))
exclusions['2509.01107']='低光水下等退化条件的二维布局到图像生成，mapping指生成分布；无三维、机器人定位建图或导航任务。'
sources=[]
main=read('main-search-candidates.json',[])
sources += [('main-C-api',x) for x in main if any('C-' in q for q in x.get('query_hits',[]))]
sources += [('main-C-route',x) for x in read('main-route-extension-enriched.json',read('main-route-extension.json',[]))]
pool_extra={x['id']:x for x in read('main-pool-enriched.json',[])}
sources += [('main-C-extra',pool_extra.get(x['id'],x)) for x in read('main-extra-extension.json',[])]
independent=read('extension-search.json',{}).get('papers',[])
initial_api_ids=set()
for raw in P.glob('extension-api-*-submittedDate-*.xml'):
 initial_api_ids.update(re.findall(r'arxiv\.org/abs/(\d{4}\.\d{4,5})',raw.read_text(encoding='utf8')))
sources += [('independent-api',x) for x in independent if x['id'] in initial_api_ids]
sources += [('independent-advanced',x) for x in read('extension-advanced-candidates.json',[])]
sources += [('independent-advanced-applications',x) for x in read('extension-advanced-applications-candidates.json',[])]
pool={x['id']:x for x in read('main-pool-enriched.json',[])}
histories=read('extension-official-histories.json',{})
prior=json.loads((ROOT/'reports/paper-history.json').read_text(encoding='utf-8-sig'))['papers']
U={}
for origin,x in sources:
 ident=x['id']
 if ident not in U:U[ident]={**pool.get(ident,{}),**x,'input_origins':[origin]}
 else:
  U[ident]['input_origins'].append(origin)
  U[ident]['source_urls']=list(dict.fromkeys(U[ident].get('source_urls',[])+x.get('source_urls',[])))
  if len(x.get('abstract',''))>len(U[ident].get('abstract','')):U[ident]['abstract']=x['abstract']
 for k in ('version','v1_utc','updated_utc'):
  if not U[ident].get(k) and pool.get(ident,{}).get(k):U[ident][k]=pool[ident][k]
priority_ids={'2610.31476':'点级更新直接改善动态语义地图。','2610.31762':'导航目标驱动的几何可读出未来表示。','2610.33794':'扫描重建直接支持真实环境导航适配。','2610.34041':'激光几何增量转成时序事件场景图。','2610.36011':'以三维基础模型为原生世界动作骨干。','2610.36454':'水下多传感紧耦合定位直接相关。','2610.39232':'统一深度、运动与视频生成的四维感知。','2610.40614':'可直接渲染潜在的三维高斯世界记忆。','2610.35312':'开放词汇单目占据和几何语义联合。','2610.31432':'跨会话三维拓扑定位与导航。','2610.30589':'动态环境开放词汇在线建图。'}
rows=[];unresolved=[]
for ident,x in sorted(U.items()):
 if ident not in notes and ident not in exclusions:unresolved.append({'id':ident,'title':x.get('title'),'origins':x['input_origins']});continue
 abstract=x.get('abstract','');ss=re.split(r'(?<=[.!?])\s+(?=[A-Z])',abstract)
 if ident=='2610.37330':
  s=(P/'extension-37330-official.html').read_text(encoding='utf8');seg=re.search(r'<div[^>]*class="ltx_abstract"[^>]*>(.*?)</div>',s,re.S)
  if not seg:raise ValueError('Canonical 37330 HTML abstract missing')
  x['conflicting_abs_atom_abstract']=abstract;x['abstract']=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',seg[1]))).strip().removeprefix('Abstract').strip();abstract=x['abstract'];ss=re.split(r'(?<=[.!?])\s+(?=[A-Z])',abstract)
  x.update(canonical_abstract_source='https://arxiv.org/html/2610.37330v1#abstract1',metadata_conflict='Official abs/Atom title is Tokens of Motion but abstract describes unrelated AFIL; canonical official HTML abstract matches title and M-PACT. Keep conflict warning; abstract-level HTML reading only.')
 x['abstract_read']=True;x['evidence']={'level':'abstract','read_sections':['Abstract (complete)'],'boundary':'未读全文，未核验表格、消融细项或复现；引用数字仅为作者摘要报告。'}
 if ident in histories:
  h=histories[ident];x.update(h)
  if h.get('version_history'):
   v1=next((v for v in h['version_history'] if v['version']==1),None);cur=max(h['version_history'],key=lambda v:v['version']);x.update(version=cur['version'],v1_utc=v1['utc'] if v1 else x.get('v1_utc'),updated_utc=cur['utc'])
 v=x.get('version');pv=prior.get(ident,{}).get('versions',{}).get('v'+str(v));x['prior_same_version']=pv
 pub=x.get('v1_utc','');upd=x.get('updated_utc','');start='2026-10-24T08:17:58Z';end='2026-11-01T14:59:32Z'
 x['window_class']='new' if start<pub<=end else ('revised' if start<upd<=end else ('historical_revision_backfill' if v and v>1 else 'historical_backfill'))
 for source_key,target_key in [('v1_utc','v1_asia_shanghai'),('updated_utc','updated_asia_shanghai')]:
  if x.get(source_key):x[target_key]=datetime.datetime.fromisoformat(x[source_key].replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
 x['date_evidence']='Official arXiv submission history' if x.get('history_verified') else 'Official arXiv Atom metadata; exact abs history cross-check pending in parent'
 if ident in exclusions:x.update(disposition='excluded',reason=exclusions[ident],direction='out-of-scope',category='out-of-scope')
 else:
  cat,txt=notes[ident];experiment_sentences=[s for s in ss if re.search(r'experiment|evaluat|benchmark|achiev|success|%|\\%|speedup|results|outperform',s,re.I)]
  x.update(disposition='supplemental',reason='摘要确认与机器人世界模型/动作、三维感知/空间仿真、定位建图或具身导航直接相关。',category=cat,direction=cat,problem=ss[0] if ss else '',method=txt,takeaway=txt,insight_math='摘要级设计洞见：'+txt+' 数学推导与成立条件未作全文核验。',experiments=' '.join(experiment_sentences[-4:]) if experiment_sentences else '摘要未提供可核验的实验数值；不推断性能。',priority=ident in priority_ids,priority_reason=priority_ids.get(ident,'保留相关方向的完整摘要跟踪；未据全文或本地复现提升优先级。'),follow_up='若后续深读，核验Method、Experiments、消融与官方实现；本轮未本地运行。')
  if pv:x.update(disposition='already_reported_same_version',reason='paper-history已记录相同ID+版本，本轮核销引用原报告，不计新增或历史补漏。')
 rows.append(x)
save('extension-screened.json',{'schema_version':1,'run_at':'2026-11-01T14:59:32Z','generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'C-family model-read screening plus independent rediscovery; copied English sentences are abstract experiment evidence, not full-text validation','papers':rows,'unresolved':unresolved,'counts':dict(collections.Counter(x['disposition'] for x in rows)),'abstract_read_unique':len(rows),'boundary':'C main API + route + extra dispatched sets abstract-read; only 37330 HTML Abstract read to resolve source conflict, not full text.'})
save('extension-unresolved.json',unresolved)
print('rows',len(rows),'counts',dict(collections.Counter(x['disposition'] for x in rows)),'unresolved',len(unresolved));print(json.dumps(unresolved,ensure_ascii=False))
