import pathlib,json,re
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
pool={}
for name in ['main-cross-metadata.json','main-search-candidates.json','main-advanced-candidates.json','extension-advanced-candidates.json']:
    if not (P/name).exists():continue
    x=read(name)
    if isinstance(x,dict):x=x.get('papers',x.get('candidates',[]))
    for r in x:
        if not r.get('id'):continue
        if r['id'] not in pool:pool[r['id']]=r.copy()
        else:
            a=pool[r['id']]
            for k in ['title','abstract','version','v1_utc','updated_utc']:
                if not a.get(k) and r.get(k):a[k]=r[k]
            for k in ['query_hits','source_urls']:a[k]=list(dict.fromkeys(a.get(k,[])+r.get(k,[])))
        pool[r['id']].setdefault('input_files',[]).append(name)
save('main-pool.json',list(pool.values()))
core=re.compile(r'slam|odometr|locali[sz]|\bvio\b|inertial|structure.from.motion|\bsfm\b|bundle.adjust|pose.graph|loop.clos|registrat|calibrat|place.recog',re.I)
geometry=re.compile(r'vggt|dust3r|mast3r|\bpi3\b|\b3d\b|\b4d\b|reconstruct|splat|point.?map|point.?cloud|multi.view.stereo|depth.estim|scene.coordinate|camera.recover|geometry.foundation',re.I)
extension=re.compile(r'world.model|world.action|world.?modeling|\bwam\b|navigat|\bvln\b|scene.graph|semantic.map|spatial.memory|embodied|occupancy',re.I)
groups={k:[] for k in ['core','geometry','extension','screen']}
for r in pool.values():
    t=r['title'];a=r.get('abstract','')
    if core.search(t):key='core'
    elif geometry.search(t):key='geometry'
    elif extension.search(t):key='extension'
    elif core.search(a) or geometry.search(a) or extension.search(a):key='screen'
    else:key='screen'
    groups[key].append(r)
for k,rows in groups.items():save('main-route-'+k+'.json',rows)
print('pool',len(pool),'routes',{k:len(v) for k,v in groups.items()})
print('LIO-SMF',[(r['id'],r['title']) for r in pool.values() if '2605.09383'==r['id']])
