import pathlib,re,json
from lxml import html
P=pathlib.Path(__file__).resolve().parent
def clean(s):return re.sub(r'\s+',' ',s).strip()
rows={}
for f in P.glob('review-*-submitted_date*.html'):
 tree=html.fromstring(f.read_bytes())
 for e in tree.xpath('//li[@class="arxiv-result"]'):
  a=e.xpath('.//p[contains(@class,"list-title")]//a');m=re.search(r'(\d{4}\.\d{4,5})',a[0].text_content() if a else '')
  if not m:continue
  i=m[1]
  if i in rows:rows[i]['query_hits'].append(f.name);continue
  t=e.xpath('.//p[contains(@class,"title is-5")]');ab=e.xpath('.//span[contains(@class,"abstract-full")]');da=e.xpath('.//p[contains(@class,"is-size-7")]')
  rows[i]={'id':i,'title':clean(t[0].text_content()) if t else '', 'abstract':clean(ab[0].text_content()).removesuffix('△ Less').strip() if ab else '', 'search_date_text':[clean(x.text_content()) for x in da],'query_hits':[f.name], 'source_urls':['https://arxiv.org/abs/'+i],'reading_level':'metadata only; abstract available'}
relevant=re.compile(r'\bSLAM\b|reconstruct|localiz|odometr|registr|camera|\bdepth\b|\b3[Dd]\b|3-[Dd]|point.cloud|gaussian.splat|world.model|world.simulat|spatial|scene|robot|navigat|\bVIO\b|\bSfM\b|\bVGGT\b|\bDUSt3R\b|\bpointmap\b|feature.match|image.match|epipolar|egomotion',re.I)
candidates=[r for r in rows.values() if relevant.search(r['title']) or relevant.search(r['abstract'])]
(P/'review-independent-unique.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf8')
(P/'review-independent-potential.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf8')
print('unique',len(rows),'potential',len(candidates))
print('\n'.join(r['id']+' | '+r['title'] for r in candidates))
