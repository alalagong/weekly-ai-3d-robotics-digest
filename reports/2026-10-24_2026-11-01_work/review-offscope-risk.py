import pathlib,json,datetime
P=pathlib.Path(__file__).resolve().parent
reasons={
'2610.31567':'水凝胶微结构和电场用于药物输运，几何是材料形状，不是观测几何。',
'2610.40473':'可达集的抽样复杂度理论，机器人机械臂只是高维例子，不估计环境或相机位姿。',
'2610.39560':'软夹爪形态拓扑优化，几何是已知物体和抓姿条件，不恢复感知几何。',
'2610.36844':'网络层深度相关量化用于伪装目标检测；depth为网络层级。',
'2610.38482':'2.5D轨迹与深度是动作识别特征，主要输出动作类别，不是环境三维或轨迹估计。',
'2610.34897':'工业逻辑异常检测使用二维mask长度和身份绑定，不构建三维地图。',
'2610.35374':'预训练表征空间的几何保持服务域泛化目标检测，不是物理三维。',
'2610.39868':'相机噪声与胶片颗粒合成，不估计相机、深度或世界状态。',
'2610.30824':'通用VLM反复编码与网络动态深度，不是场景深度或地图。',
'2610.33202':'地下无线网络探针与通信深度解耦，不是三维地下感知/定位或导航。',
'2610.32792':'已重建固定物体的投影外观编辑及光照补偿；不提出场景重建、配准或位姿估计方法。是最接近3D应用边界的排除项，保留摘要供主审。',
'2610.31140':'面部表情识别的时空网络及分类几何anchors，不恢复三维人脸或相机位姿。',
'2610.32039':'监督对比学习的特征单纯形理论，不是物理多视图几何。',
'2610.31801':'机器人已知运动学轨迹的语义时间切分，不估计机器人位姿或环境地图。',
'2610.34367':'嵌入曲面直径与平均曲率的纯数学定理。',
'2610.38752':'FPGA并行Canny/Harris和线跟踪预处理，验证闭环循线车辆；未评估SLAM、位姿、三维建图或空间导航，是传感硬件邻接边界项。',
'2610.38377':'三极化天线通信空间流，不是空间环境估计或地图。',
'2610.36956':'历史手写文献识别与文本对齐，register是档案册，不是几何配准。',
'2610.36628':'分类器特征空间的测试时适应，未涉及物理三维任务。',
'2610.36574':'LLM流式输出安全检测，深度是网络层，流式不是几何流。',
'2610.35171':'天文望远镜相机数据RDMA传输和拥塞管理，不估计观测几何。',
'2610.33324':'恒星吸积流的天体物理多时相观测及多普勒层析，不是计算机视觉SLAM范围。',
'2610.32749':'流式音视频目标说话人提取，未估计三维声源地图或机器人导航。',
'2610.38042':'网球广播/手机视角下反弹击球事件定位，event是语义动作事件，不是事件相机几何。',
'2605.16600':'Transformer训练权重变化在残差特征空间中的几何，不是物理场景。',
'2605.04971':'神经网络权重奇异向量跨层对齐，不是跨视图几何。',
'2606.18778':'分布漂移下潜在聚类概率预测的理论界，不涉及定位建图。',
'2610.05891':'二维分类CAM热图监督，spatial是图像区域，不是物理三维或导航。',
'2610.33715':'已知串联机械臂运动学的量子表示与逆运动学，非观测式相机/环境状态估计。'
}
rows=json.loads((P/'review-main-offscope-risk-selection.json').read_text(encoding='utf8'));out=[]
for r in rows:
 i=r['id'];out.append({'id':i,'title':r['title'],'version':r['version'],'abstract_read':True,'evidence_level':'abstract','read_sections':['Abstract (complete; independent risk audit)'],'decision':'agree_exclude','reason':reasons[i],'borderline':i in ('2610.32792','2610.38752'),'original_reference':'main-offscope-decisions.json#'+i,'source_urls':r['source_urls']})
assert len(out)==len(reasons)==29
(P/'review-main-offscope-risk-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
s=json.loads((P/'review-summary.json').read_text(encoding='utf8'));s['offscope_risk_abstracts_read']=29;s['offscope_risk_reversed']=0;s['offscope_risk_borderline_ids']=['2610.32792','2610.38752'];s['reviewed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/'review-summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8')
print('29 complete abstracts risk-checked; 0 reversals; 2 explicit scope-borderline records retained.')
