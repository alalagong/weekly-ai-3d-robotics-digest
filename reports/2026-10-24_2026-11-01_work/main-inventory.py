import json,re,html,pathlib,urllib.request,time,concurrent.futures
P=pathlib.Path(__file__).resolve().parent
ROOT=P.parent.parent
def save(name,x): (P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()
def fetch(cat):
    rows=[]; pages=[];skip=0;total=None
    while True:
        url=f'https://arxiv.org/list/{cat}/recent?skip={skip}&show=2000'
        q={'family':'official-category-inventory','category':cat,'url':url,'field':'official announcement title inventory','date_predicate':'recent announcement dates; exact submission times verified separately','retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exhausted':False}
        try:
            dest=P/f'main-{cat}-{skip}.html'
            s=dest.read_text(encoding='utf-8') if dest.exists() else urllib.request.urlopen(url,timeout=35).read().decode()
            dest.write_text(s,encoding='utf-8')
            m=re.search(r'Total of\s+([\d,]+)\s+entries',s);total=int(m[1].replace(',','')) if m else None
            blocks=re.findall(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>',s,re.S);found=[]
            for dt,dd in blocks:
                mid=re.search(r'arXiv:(\d{4}\.\d{4,5})',dt)
                title=re.search(r'<div class=[\'\"]list-title mathjax[\'\"]>(.*?)</div>',dd,re.S)
                if mid:found.append({'id':mid[1],'title':clean(title[1]).removeprefix('Title:').strip() if title else '', 'source_urls':[url],'categories':[cat]})
            rows+=found;q.update(total=total,returned=len(found),skip=skip,pages_fetched=1,raw_path=str(dest.relative_to(ROOT)),exhausted=total is not None and skip+len(found)>=total)
        except Exception as ex:q['failure']=str(ex);pages.append(q);break
        pages.append(q)
        if q['exhausted'] or not found:break
        skip+=len(found);time.sleep(3)
    print(cat,total,len(rows),pages[-1]['exhausted'],flush=True)
    return rows,pages
out=list(concurrent.futures.ThreadPoolExecutor(max_workers=2).map(fetch,['cs.RO','cs.CV','eess.IV','eess.SY']))
inventory={};manifest=[]
for rows,pages in out:
    manifest+=pages
    for r in rows:
        if r['id'] in inventory:
            inventory[r['id']]['source_urls']+=r['source_urls'];inventory[r['id']]['categories']+=r['categories']
        else:inventory[r['id']]=r
save('main-category-manifest.json',manifest);save('main-category-inventory.json',list(inventory.values()))
pattern=re.compile(r'slam|odometr|locali[sz]|structure.from.motion|\bsfm\b|\bvio\b|visual.inertial|bundle.adjust|loop.clos|pose.graph|registrat|reconstruct|mapping|\bmap\b|gaussian|splat|vggt|dust3r|mast3r|\bpi3\b|geometry|geometric|point.?cloud|pointmap|3d.scene|3d.vision|depth|navigat|world.model|world.action|lidar|radar|thermal|endoscop',re.I)
cross=[x for x in inventory.values() if pattern.search(x['title'])]
save('main-category-candidates.json',cross)
history=json.loads((ROOT/'reports/paper-history.json').read_text(encoding='utf-8-sig'))
audit=(ROOT/'reports/2026-10-18_SLAM-VGGT_论文完整性审计.md').read_text(encoding='utf-8-sig')
ids=list(dict.fromkeys(re.findall(r'arxiv.org/abs/(\d{4}\.\d{4,5})',audit)))
seeds=[]
for ident in ids:
    versions=history['papers'].get(ident,{}).get('versions',{})
    processed=[{'version':v,**r} for v,r in versions.items()]
    seeds.append({'id':ident,'source':'reports/2026-10-18_SLAM-VGGT_论文完整性审计.md','processed_versions':processed,'status':'already-covered-regression-seed' if processed else 'unresolved-seed','note':'Do not count same processed version as historical backfill. Fresh current-version searches handled separately.'})
save('main-audit-seeds.json',seeds)
save('run-context.json',{'run_at':'2026-11-01T14:59:32Z','coverage_start_exclusive':'2026-10-24T08:17:58Z','coverage_end_inclusive':'2026-11-01T14:59:32Z','display_timezone':'Asia/Shanghai','initial_network_failure':'Sandbox urllib DNS getaddrinfo11001; approved read-only external fetch works','category_inventory_count':len(inventory),'category_candidates':len(cross),'audit_seed_count':len(seeds)})
print('unique',len(inventory),'potential',len(cross),'seeds',len(seeds),flush=True)
