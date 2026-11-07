import pathlib,urllib.request,json,time
from lxml import html
P=pathlib.Path(__file__).resolve().parent
jobs=[('2610.40525','https://crossweave3d.github.io/'),('2609.03919','https://microsoft.github.io/OctWorld/'),('2610.30799','https://github.com/mmaiLab/WovenAnchorMatcher')]
out=[]
for i,url in jobs:
 m={'id':i,'url':url,'channel':'official project / author repository','retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'fields':'project main page / repository landing README','predicate':'new independent candidate verification; no date inference from project page','total':1,'pages':[],'fetched':0,'exhausted':False}
 try:
  b=urllib.request.urlopen(url,timeout=35).read();raw=P/('review-project-'+i+'.html');raw.write_bytes(b);tree=html.fromstring(b)
  for el in tree.xpath('//script|//style|//nav|//header|//footer'):el.drop_tree()
  s=' '.join(tree.text_content().split());(P/('review-project-'+i+'.txt')).write_text(s,encoding='utf8');m.update({'pages':[{'url':url,'raw_path':raw.name}],'fetched':1,'exhausted':True,'text_excerpt':s[:12000]})
 except Exception as ex:m['failure']=str(ex)
 out.append(m);(P/'review-project-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(i,m['exhausted'],m.get('failure'),flush=True)
