import pathlib,json,re,collections
P=pathlib.Path(__file__).resolve().parent
rd=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
pool={x['id']:x for x in rd('main-pool-enriched.json')};rows=rd('main-title-screened-offscope.json')
groups=[
('天体与空间物理',r'galax|milky|solar|sun\b|cepheid|lyrae|telescope|observatory|reionization|reionisation|comet|asteroid|gravitational|tidal|parker|reion|star\b|stars|astro|atmospher|C/2025|Telescopii|Gaia|cauchy.horizon|mass.inflation|auroral'),
('量子、凝聚态与粒子物理',r'quantum|qubit|superconduct|photon|fermion|boson|magnetic|ising|nuclear|atomic|plasma|spin\b|qcd|hadron|meson|baryon|lepton|lattice|topolog|field theory|casimir|electrochemical|axion|chiral|kagome|PNJL|CP.Violation|Reggeized|pion|neutr|Higgs|Hofstadter|Wannier|Friedel|Coherent.Microwave|Rydberg|Kelvin.Wave|STCF|B_s|B_Λ|\\to|decays|[πψφΛΥΣ].*[+_(){}]|anyon|Hall.crystal|Schrödinger|Schrodinger|Bell.Greenberger|MAMI|Fargues|Dark.Matter'),
('纯数学与通用算法理论',r'theorem|conjecture|polynomial|ergodic|ramsey|turan|turán|hypergraph|inequal|asymptotic|convex|markov|algebra|probab|eigen|schubert|modular|subgroup|combinat|langevin|fourier|log.concave|percolat|recursion|symmetr|brion|nilpot|decid|prime|noncommut|curve|profinite|riesz|painlev|harmonic|Euclidean.4|Euclidean.space|choice|Skew.brace|schur|polyhedr|random.walk|multiband.prolate|dirichlet|Lebesgue|fields.and.bases|L.functions|Drinfeld|Calabi|Cayley|paintbox|move.structure|entropy.rate|parking.function|graph.connectivity|semistream|streaming.lower|space.approximation'),
('语音、音频与通信信号',r'speech|speaker|audio|music|acoustic|conversat|translation|spoken|hearing|respirat|MIMO|wireless|radio|RIS\b|transceiver|beamforming|RF.Finger|CSI\b|channel|phonetic|I2S|voice|codec|DAQ|readout.chain|TPC|sPHENIX'),
('二维医学与生理分析',r'medical|mri|brain|cancer|tumor|tumour|chest|x.ray|clinical|patient|ecg|heart|ppg|cardiovascular|skin|cholangio|biobank|health|physiolog|blood|retina|cell.type|spinal.images|hydrogel|Iontophoretic|Pneumonia'),
('语言模型、软件与非具身代理',r'agent|language|llm|coding|context|instruction|memory|reasoning|token|transformer|recommend|gui|tool|prompt|embedding|code|software|benchmark.radar|OCR|entailment|office.scale|Lexing|disclosure|website|cache|KV\b|unlearning|post.training|RPKD|fact.check|prefetch|GTV|Cognitive|Narrative|Masked.Diffusion|Vision.Language|Text.to.Image'),
('一般视觉、时序统计与系统工程',r'forecast|series|financial|economic|trading|classification|anomaly|regression|gradient|learning|sample|distribution|stochastic|clustering|statistic|vector|sampling|graph|data|stream|video|image|vision|detector|detection|recognition|segmentation|sensor|compression|gpu|fpga|network|signal|system|control|fluid|flow|thermal|power|temperature|hydrogen|chemical|elastic|noise|bayes|causal|parameter|optimization|simulation|computation|HPC|ReLU|test.time|logit|feature|prototype|discriminant|CLIP|Category.Discovery|loss.spike|unsteady|morpholog|water.wave|reranking|Selective.Auditing|water.mapping|price|welfare|agreements|causal|Q.MMR|entropy|OOD|physical.non|numerical.frame')]
manual={
'2608.04527':'已读完整摘要：RTCF通过单调轨迹记忆对齐和低频动作残差纠正冻结VLA；其对象为LIBERO操作策略执行，无SLAM、几何重建、导航或预测世界模型。作为机器人控制边界排除，若独立复核给出直接空间关系则重新纳入。',
'2610.39560':'已读完整摘要：研究软夹爪机械拓扑优化和抓取鲁棒性，明确依靠机械设计而非感知控制；未提出SLAM、三维视觉重建、导航或机器人世界模型。',
'2610.34184':'已读完整摘要：只评测胶囊内窥镜Wi-Fi HaLow图像通信链路的吞吐、功耗与时延；未研究内窥镜定位、几何重建或建图。',
'2610.34904':'已读完整摘要：研究Sentinel-2洪水水体二维分割与预训练模型速度/IoU；mapping指遥感分类图，不是定位建图或三维几何。',
'2610.39356':'已读完整摘要：Generalized Category Discovery的类别指派/Hungarian评测偏差与分类损失；mismapping不是空间建图。',
'2610.39444':'已读完整摘要：离散masked diffusion采样、条件混合与样本复杂度理论，无三维重建或机器人world应用。',
'2610.39499':'已读完整摘要：Group-Lasso Siamese特征选择，实验为通用分类数据；feed-forward为一般神经网络，不是前馈3D。',
'2610.37658':'已读完整摘要：分类模型test-time干预和标注预算控制，无定位、几何、导航或机器人world建模任务。',
'2610.37645':'已读完整摘要：MERLIN线性注意力用于Gated DeltaNet/Mamba语言模型的长上下文QA，未展示VGGT/3D/机器人应用。',
'2610.37466':'已读完整摘要：H100 DSMEM、GEMM和FlashAttention通用硬件kernel优化，未涉及几何基础模型或3D任务。',
'2610.36794':'已读完整摘要：Select-TTT针对语言模型长上下文QA的fast-weight写入；无流式几何状态或机器人任务。',
'2610.37937':'已读完整摘要：随机原型知识蒸馏在CIFAR/ImageNet分类评测，无定位建图/3D任务。',
'2610.38879':'已读完整摘要：Proximal R2回归先验、结构方差分配与统计后验；global-local不是全局/局部定位。',
'2610.36881':'已读完整摘要：RAG-CSI预测通信channel state和相位/幅度序列；未提出无线定位或RF里程计。',
}
manual_topics={}
for label,ids in {
'纯数学与通用算法理论':'2610.39211 2610.35577 2610.35306 2610.34877 2610.34367 2610.32522 2610.30720 2610.39893 2507.21575 2608.09770 2410.09574 2610.20792 2609.04285',
'量子、凝聚态与粒子物理':'2610.36034 2610.36262 2606.14305 2610.21462 2610.01024 2605.12126 2610.03230',
'化学、材料与非视觉物理仿真':'2610.32567 2608.16472',
'语言模型、软件与非具身代理':'2610.36169 2610.38160 2610.36956 2606.03163 2610.29304 2605.02960',
'一般二维识别与遥感图像理解':'2610.40643 2610.39539 2610.39323 2610.32200',
'通用计算、时序与信号系统':'2610.38377 2610.35171 2610.33665 2610.31935 2602.20317 2609.19899 2407.05302 2602.18801 2610.22008 2602.17700',
'语音与人类行为安全研究':'2608.24127',
}.items():
    manual_topics.update({ident:label for ident in ids.split()})
counts=collections.Counter();unmapped=[]
for r in rows:
    n=pool[r['id']];r.update({k:n.get(k) for k in ['version','v1_utc','updated_utc','abstract','source_urls']});r.pop('provisional_title_exclusion',None)
    if r['id'] in manual:r.update(reason=manual[r['id']],abstract_read=True,evidence_level='abstract');topic='完整摘要确认范围外'
    else:
        topic=manual_topics.get(r['id']) or next((name for name,pat in groups if re.search(pat,r['title'],re.I)),None)
        if topic is None:unmapped.append({'id':r['id'],'title':r['title']});topic='待补具体主题'
        r.update(reason='题名明确属于'+topic+'；题名《'+r['title']+'》所述研究对象与SLAM/VIO/SfM、几何基础模型/前馈3D及直接相关机器人建图导航/世界模型无直接关系。仅题名/官方元数据判定，不声称已读摘要。',evidence_level='metadata_title')
    r.update(exclusion_topic=topic,window_class=None,report_anchor=None,follow_up=None);counts[topic]+=1
(P/'main-offscope-decisions.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');(P/'main-offscope-unmapped.json').write_text(json.dumps(unmapped,ensure_ascii=False,indent=2),encoding='utf-8')
print(dict(counts));print('needs-topic',unmapped)
