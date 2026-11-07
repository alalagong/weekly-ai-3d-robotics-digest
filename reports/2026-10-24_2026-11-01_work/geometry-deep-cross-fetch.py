import pathlib,json,re,datetime,urllib.request,concurrent.futures,sys
from lxml import html
P=pathlib.Path(__file__).parent;sys.stdout.reconfigure(encoding='utf-8')
urls=['https://arxiv.org/abs/'+i for i in ['2607.02711','2609.09394','2609.15018','2603.03269','2607.09503']]+['https://jingong-chen.github.io/Any3R/','https://3dagentworld.github.io/horizonstream/','https://noheat61.github.io/GPA-VGGT/']
def fetch(u):
 stem=u.rstrip('/').rsplit('/',1)[-1];row={'url':u,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  raw=urllib.request.urlopen(u,timeout=25).read();path=P/f'geometry-deep-cross-{stem}.html';path.write_bytes(raw);d=html.fromstring(raw)
  row['path']=str(path);row['title']=' '.join(d.xpath('//title/text()'))
  row['external_urls']=list(dict.fromkeys(d.xpath('//a/@href')))
  for sel,key in [('//*[contains(@class,"submission-history")]','history'),('//blockquote[contains(@class,"abstract")]','abstract')]:
   a=d.xpath(sel);row[key]=' '.join(a[0].text_content().split()) if a else None
  row['text_path']=str(path.with_suffix('.txt'));path.with_suffix('.txt').write_text(' '.join(d.text_content().split()),encoding='utf-8')
 except Exception as e:row['error']=str(e)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,urls))
(P/'geometry-deep-cross-fetch.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:print(json.dumps(r,ensure_ascii=False))
