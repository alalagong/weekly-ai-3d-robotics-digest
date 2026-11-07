import json,pathlib,urllib.request,urllib.parse,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf-8')
P=pathlib.Path(__file__).parent
tasks=[]
for f in P.glob('geometry-deep-*-structure.json'):
 m=json.loads(f.read_text(encoding='utf-8'))
 for fig in m['figures']:
  if fig['caption'].startswith('Figure') and any(k in fig['caption'].lower() for k in ['overview','pipeline','framework','architecture']):
   for im in fig['imgs']:
    url=urllib.parse.urljoin('https://arxiv.org/html/',im['src'])
    dest=P/f"geometry-deep-{m['id']}v{m['version']}-overview{pathlib.Path(im['src']).suffix}"
    tasks.append({'id':m['id'],'version':m['version'],'figure_id':fig['id'],'caption':fig['caption'],'url':url,'path':str(dest),'visually_verified':False})
def fetch(t):
 try:pathlib.Path(t['path']).write_bytes(urllib.request.urlopen(t['url'],timeout=25).read());t['status']='downloaded'
 except Exception as e:t['error']=str(e);t['status']='failed'
 return t
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:res=list(ex.map(fetch,tasks))
(P/'geometry-deep-images.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
for t in res:print(t['id'],t['status'],t['path'])
