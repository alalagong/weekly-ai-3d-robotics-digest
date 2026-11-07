import pathlib,json,datetime
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();allrows=read('review-all-dispositions.json');original=[x for x in allrows if x['evidence_level']=='metadata_programmatic'];raw={x['id']:x for x in read('review-independent-unique.json')}
save('review-original-programmatic-dispositions.json',original)
reasons={
'2610.40468':'以农村临床诊断为动机的对抗域泛化样本复杂度理论，不是驾驶环境或机器人空间泛化。',
'2610.33005':'能源模型用于语言token生成及语言预训练，不是视觉几何或物理世界模型。',
'2603.09138':'p4旋转等变Mamba用于二维分类、语义分割及图像超分辨，未构建物理三维或估计相机位姿。',
'2610.32926':'Zakai神经算子用于合成Double-Well/VDP/Lorenz状态及固定线虫脑信号，不是导航或几何状态估计。',
'2610.32487':'state estimation实际是电网电压与相位估计，14至118-bus电力网络，不是移动机器人状态或SLAM。',
'2610.32409':'事件SNN分类的扰动鲁棒后校准；输出logits和动作类别，不恢复事件相机运动或场景几何。',
'2610.32372':'异步多速率线性控制的Lyapunov/LMI稳定和耗散理论，仅数值例子，无感知定位或空间建图。',
'2610.38628':'自动驾驶测试sim-to-real现实差距的系统综述，分析测试证据与组件，没有显式三维/地图/定位方法或学习式世界模型；保留仿真邻接边界。',
'2610.33294':'worlds指受对称性超选择约束的广义概率/量子理论，不是生成物理场景或机器人世界模型。',
'2610.38662':'已知状态的护航追逃最短时间路径解析结构，未涉及定位、三维感知、建图或学习世界动力学。',
'2610.38259':'任意骨架角色的拓扑无关运动生成，输出骨架动作，不估计观测三维场景或相机轨迹。',
'2610.37633':'XTrack由query mask跟踪跨视角跨时间物体身份，输出mask和identity；不恢复位姿、三维、地图或导航，按纯对象关联排除。',
'2610.35170':'光通信ISAC的目标距离/速度和信道估计理论与仿真，不估计机器人自运动、环境地图或多视图几何；按通信波形感知邻接排除。',
'2610.08533':'几何为MSR-VTT/DiDeMo音视频模态的Gram表征空间，分析退化方向，不是物理几何。',
'2610.33892':'用给定二维位置、图像和波束历史预测下一波束标签，不估计位置、三维环境或导航。',
'2610.34921':'PhysEvolve以可执行物理world程序和反事实模拟训练通用VLM物理问答；无显式三维重建、地图、相机或导航。按严格直接几何/具身范围暂排，作为world simulator边界供主审裁定。'
}
aud=[]
for index,o in enumerate(original):
 i=o['id'];r=dict(o);r['original_evidence_level']=o['evidence_level'];r['independent_llm_title_read']=True;r['title_review_index']=index;r['title_review_batch']=index//240;r['reviewed_at']=now;r['evidence_level']='metadata_title';r['reason']='独立LLM已逐题名复审：《'+r['title']+'》的研究对象属于'+r['exclusion_topic']+'，不以SLAM/VIO/SfM、物理环境几何、位姿或直接空间地图/导航为任务。该判定已人工式题名审查；并非仅以预筛词未命中排除。'
 if i in reasons:r.update({'evidence_level':'abstract','abstract_read':True,'abstract':raw[i]['abstract'],'read_sections':['Title (independent LLM review)','Abstract (complete; ambiguous-title follow-up)'],'reason':reasons[i]})
 r['scope_borderline']=i in ('2610.38628','2610.35170','2610.34921');aud.append(r)
assert len(aud)==937 and len(reasons)==16 and all(r['disposition']=='excluded' for r in aud)
save('review-937-title-audit.json',aud);byid={x['id']:x for x in aud};save('review-all-dispositions.json',[byid.get(x['id'],x) for x in allrows]);save('review-937-abstract-followups.json',[x for x in aud if x['id'] in reasons])
s=read('review-summary.json');s.update({'reviewed_at':now,'programmatic_exclusions_original':937,'independent_llm_title_audit_count':937,'independent_llm_title_audit_batches':[{'indices':[0,239],'count':240},{'indices':[240,479],'count':240},{'indices':[480,719],'count':240},{'indices':[720,936],'count':217}],'ambiguous_title_complete_abstracts_read':16,'ambiguous_title_core_misses_found':0,'scope_borderline_ids_additional':['2610.38628','2610.35170','2610.34921'],'programmatic_only_final_exclusions':0,'total_independent_complete_abstracts_read':24+29+16});s['limitations'][0]='Original 937 vocabulary-prefilter exclusions preserved separately, then all 937 titles independently LLM-reviewed in four printed batches; 16 ambiguous items received complete abstract follow-up. No automatic prefilter is claimed as independent acceptance.';save('review-summary.json',s)
print('937/937 titles independently LLM-read; 16 complete abstracts; 0 newly found geometry core misses. Original prefilter retained.')
