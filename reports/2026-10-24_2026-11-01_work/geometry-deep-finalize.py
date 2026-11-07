import json,pathlib,datetime,re,struct
P=pathlib.Path(__file__).parent
papers=[]
for name in ['geometry-deep-notes.json','geometry-deep-notes-2.json']:papers+=json.loads((P/name).read_text(encoding='utf-8'))
images=json.loads((P/'geometry-deep-images.json').read_text(encoding='utf-8'))
visual_notes={
 '2610.37000':'原图1680×889，视觉确认：上部DINOv2输入→0–8共享跨帧KV→9–23仅KV合并，13–16弱合并；下部(a)stride8内容聚类与log s，(b)128D投影与保留Q。与Fig4 Overview caption一致。',
 '2610.36150':'原图823×281，视觉确认：三类相机与ray sphere→角坐标→intra/inter-frame attention；camera/dense heads输出pose及X=dR；下支路solid-angle训练损失。与Fig3 Overview caption一致。',
 '2605.23889':'原图2035×872，视觉确认：RGB stream/local causal window、pose/MRT/image tokens，GWA与GLA交替，右侧pose/depth/optional LC，下面head/channel gates及persistent state。与Fig3 Overview caption一致。'
}
for im in images:
 im['visually_verified']=True;im['verification_tool']='functions.view_image';im['visual_description']=visual_notes[im['id']]
 data=pathlib.Path(im['path']).read_bytes();im['width'],im['height']=struct.unpack('>II',data[16:24]);im['embed_allowed']=True
(P/'geometry-deep-images.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
initial=json.loads((P/'geometry-deep.json').read_text(encoding='utf-8'));initmap={r['id']:r for r in initial['papers']}
for p in papers:
 stem=f"geometry-deep-{p['id']}v{p['version']}";structure=json.loads((P/(stem+'-structure.json')).read_text(encoding='utf-8'))
 p['evidence_level']='full_text';p['abstract_read']=True;p['full_main_text_read']=True
 prior=initmap[p['id']]
 hp=prior.get('history_path') or prior.get('source',{}).get('official_history_path')
 ht=prior.get('history') or prior.get('source',{}).get('official_history')
 p['source']={'html_url':structure['url'],'html_path':structure['path'],'extracted_text_path':str(P/(stem+'-read.txt')),'structure_path':str(P/(stem+'-structure.json')),'retrieved_at':structure['retrieved_at'],'char_count':structure['char_count'],'pdf_used':False,'official_history_path':hp,'official_history':ht}
 p['system_figure']=next((r for r in images if r['id']==p['id']),{'embed_allowed':False,'visually_verified':False,'reason':'全文所有figure caption无明确overview/pipeline/framework系统图；不将ROC或结果图冒充系统图。','body_figure_position_url':structure['url']+'#S3','label':'方法Section3正文位置（不嵌图）'})
 p['revision_comparison']='v1全文未读取比较；不评价重大修订' if p['version']>1 else 'v1新文，无旧版差异比较'
 p['ran_experiments']=False;p['downloaded_weights_or_datasets']=False
 for exp in p['experiments']:
  tablemap={
   '2610.37000':{'1':'S4.T1','2':'S5.T2','3':'S5.T3','4':'S5.T4','5':'S5.T5','S1':'A2.T1','S2':'A3.T2','S3':'A3.T3','S4':'A6.T4','S5':'A7.T5','S6':'A7.T6'},
   '2610.35806':{str(i):'S4.T'+str(i) for i in range(1,8)},
   '2610.36150':{'1':'S3.T1','2':'S4.T2','3':'S4.T3','4':'S4.T4','19':'A5.T19','20':'A5.T20','21':'A10.T21','22':'A12.T22'},
   '2605.23889':{'1':'S3.T1','2':'S4.T2','3':'S4.T3.fig1','4':'S4.T5.fig1','5':'S4.T5.fig2','6':'S4.T6','7':'A3.T7','8':'A5.T8'}
  }
  tm=re.search(r'Tables?\s*(S?\d+)',exp['source'])
  anchor=tablemap[p['id']].get(tm.group(1)) if tm else None
  match=re.search(r'(?:S\d+(?:\.[\w]+)*)',exp['source'])
  if anchor:exp['source_url']=structure['url']+'#'+anchor
  elif match:exp['source_url']=structure['url']+'#'+match.group(0)
  else:exp['source_url']=structure['url']
 p['claim_boundary']='作者实验及本文阅读结论，非本地复现实测。'
crossfetch=json.loads((P/'geometry-deep-cross-fetch.json').read_text(encoding='utf-8'))
history=json.loads((P/'../paper-history.json').read_text(encoding='utf-8'))
cross=[]
for r in crossfetch:
 if not r.get('history'):continue
 aid=r['url'].rsplit('/',1)[-1];v=max(map(int,re.findall(r'\[v(\d+)\]',r['history'])))
 known=history.get('papers',{}).get(aid,{})
 cross.append({'id':aid,'version':v,'title':r['title'],'source_url':r['url'],'history':r['history'],'official_abs_path':r['path'],'abstract_read':True,'reading_level':'abstract','abstract':r['abstract'],'disposition':'context_outside_window_not_new_backfill','reason':'官方submission history显示最新版本仍早于2026-10-24T08:17:58Z，仅用于方法关系定位，不冒作期内新发现或新补漏。','history_match':known.get('versions',{}).get('v'+str(v)),'legacy_mentions':known.get('legacy_mentions',[])})
rev=history['papers']['2610.07883']['versions']['v1']
cross.append({'id':'2610.07883','version':1,'title':'ReVar3R: gauge-aware perturbation uncertainty for feed-forward 3D reconstruction','reading_level':'reference_metadata_this_subtask','disposition':'already_covered_exact_version','reason':'failure-probe Related Work引用的点级不确定性对照；不重复升级本次阅读。','previous_report':rev['report_path'],'previous_evidence_level':rev['evidence_level']})
out={'schema_version':1,'run_at':'2026-11-01T14:59:32Z','coverage_start_utc':'2026-10-24T08:17:58Z','coverage_end_utc':'2026-11-01T14:59:32Z','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'complete','freeze_note':'论文版本按官方提交历史锁定；11月2日访问项目页仅确认当前可见入口，不据此追认窗口内代码发布时间。','counts':{'full_main_text_read':4,'system_figures_visually_verified':3,'no_qualifying_system_figure':1,'local_experiment_runs':0,'cross_context_abstracts_read':5,'new_in_window_cross_discoveries':0},'papers':papers,'cross_discovery':cross,'cross_reference_evidence_path':str(P/'geometry-deep-cross-references.json'),'project_crosscheck_evidence_path':str(P/'geometry-deep-cross-fetch.json'),'known_limits':['全文获取采用arXiv HTML；所有数学/表格数字以原HTML对应段落为源；没有下载PDF或权重数据。','read.txt含MathML与TeX双文本，出现重复数字是抽取表示；本JSON手工核对记录单一数值。','不把主文全文深读扩张成每张定性图视觉全审计；actual_read_sections与coverage_limitations逐篇写明。','五个相关工作均核对官方abs/完整摘要且最新版本在窗口前；其余仅提名引用没有时间归属证据，不进入新候选。']}
assert len(papers)==4 and len({(p['id'],p['version']) for p in papers})==4
assert all(pathlib.Path(p['source']['html_path']).exists() for p in papers)
assert all(pathlib.Path(x['path']).exists() for x in images)
assert all(p['source']['official_history'] for p in papers)
(P/'geometry-deep.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out['counts'],ensure_ascii=False))
