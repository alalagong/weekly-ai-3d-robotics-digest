import pathlib,json,re
from lxml import html,etree
P=pathlib.Path(__file__).resolve().parent
out={}
for i in ['2610.37602','2610.36853','2610.36454']:
 path=P/('core-deep-'+i+'v1.html');root=html.fromstring(path.read_bytes())
 for m in root.xpath('//*[local-name()="math"]'):
  m.text=' '+(m.get('alttext') or ''.join(m.itertext()))+' '
  for c in list(m):m.remove(c)
 lines=[];figures=[];tables=[];sections=[]
 for x in root.xpath('//article//*[self::h1 or self::h2 or self::h3 or self::h4 or self::p or self::figcaption or self::table]'):
  if any(a.tag in ('p','table') for a in x.iterancestors()):continue
  txt=re.sub(r'\s+',' ',' '.join(x.itertext())).strip()
  if not txt:continue
  ident=x.get('id') or next((a.get('id') for a in x.iterancestors() if a.get('id')),None)
  line='['+str(ident)+'] '+txt;lines.append(line)
  if x.tag.startswith('h'):sections.append({'id':ident,'text':txt})
  if x.tag=='table':tables.append({'id':ident,'text':txt,'rows':[[re.sub(r'\s+',' ',' '.join(c.itertext())).strip() for c in row.xpath('./th|./td')] for row in x.xpath('.//tr')]})
 for fig in root.xpath('//figure'):
  cap=fig.xpath('./figcaption');txt=re.sub(r'\s+',' ',' '.join(cap[0].itertext())).strip() if cap else ''
  figures.append({'id':fig.get('id'),'caption':txt,'images':[dict(im.attrib) for im in fig.xpath('.//img')]})
 (P/('core-deep-'+i+'v1.txt')).write_text('\n\n'.join(lines),encoding='utf8')
 out[i]={'sections':sections,'figures':figures,'tables':tables,'paragraphs':len(lines),'chars':sum(len(x) for x in lines)}
(P/'core-deep-extracted.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for i,d in out.items():
 print(i,d['chars'],'chars',len(d['tables']),'tables');print('SECTIONS',d['sections']);print('FIGURES',[(x['id'],x['caption']) for x in d['figures']])
