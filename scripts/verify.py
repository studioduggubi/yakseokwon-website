"""Validate generated routes, local assets, and independent runtime boundaries."""
import json,pathlib,re,urllib.parse
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
errors=[];remote_resources=set();refs=0
pages=list(DIST.rglob('*.html'))
for f in pages:
 text=f.read_text();s=BeautifulSoup(text,'html.parser')
 if '[Truncated]'in text:errors.append([str(f.relative_to(DIST)),'truncated source'])
 for e in s.find_all(True):
  for k,v in e.attrs.items():
   if k.startswith('on'):errors.append([str(f.relative_to(DIST)),'inline handler',k])
  for k in ['src','poster','href','data-href']:
   u=e.get(k)
   if not u or u.startswith(('mailto:','tel:','#','data:','javascript:')):continue
   if u.startswith(('https:','http:','//')):
    if e.name in ['script','img','link','source','video']and(k!='href'or e.name=='link'):remote_resources.add(u)
    continue
   dest=urllib.parse.urlsplit(u).path
   if dest.startswith('/'):
    target=DIST/dest.lstrip('/');target=target/'index.html'if target.is_dir()else target;refs+=1
    if not target.exists():errors.append([str(f.relative_to(DIST)),k,u])
 for script in s.select('script[src]'):
  if script['src']!='/site.js':errors.append([str(f.relative_to(DIST)),'unexpected script',script['src']])
for f in (DIST/'assets').glob('*.css'):
 for url in re.findall(r'url\([\"\']?([^\"\'\)]+)',f.read_text(errors='replace')):
  if url.startswith('/assets/')and not(DIST/urllib.parse.urlsplit(url).path.lstrip('/')).exists():errors.append([f.name,'css asset',url])
index=json.loads((DIST/'data/boards.json').read_text())
report={'pages':len(pages),'checked_local_references':refs,'board_entries':{k:len(v)for k,v in index.items()},'remote_resource_dependencies':sorted(remote_resources),'errors':errors}
(ROOT/'reports/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if errors or remote_resources:raise SystemExit(1)
