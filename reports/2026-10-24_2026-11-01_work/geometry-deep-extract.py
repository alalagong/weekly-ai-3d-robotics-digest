import pathlib,json,re
from lxml import html
P=pathlib.Path(__file__).parent
def txt(e):return ' '.join(e.text_content().split())
for path in P.glob('geometry-deep-*v*.html'):
 doc=html.fromstring(path.read_bytes());lines=[]
 for e in doc.xpath('//h1|//h2|//h3|//h4|//h5|//p|//table|//figcaption'):
  if e.xpath('ancestor::nav|ancestor::footer|ancestor::table|ancestor::figcaption'):continue
  ident=e.get('id') or next((a.get('id') for a in e.iterancestors() if a.get('id')),'')
  if e.tag=='table':
   rows=[' | '.join(txt(c) for c in row.xpath('./th|./td')) for row in e.xpath('.//tr')]
   value='\n'.join(rows)
  else:value=txt(e)
  if value:lines.append(f'[{ident}] {value}')
 dest=path.with_name(path.stem+'-read.txt');dest.write_text('\n\n'.join(lines),encoding='utf-8')
 print(path.name,'lines',len(lines))
