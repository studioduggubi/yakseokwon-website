"""Validate generated routes, assets, base paths, and search exclusion."""
import json,pathlib,re,urllib.parse,hashlib
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
BASE=BeautifulSoup((DIST/'index.html').read_text(),'html.parser').html.get('data-site-base','')
errors=[];remote_resources=set();refs=0;noindex_pages=0

def local_target(url,source):
 path=urllib.parse.urlsplit(url).path
 if BASE:
  if path!=BASE and not path.startswith(BASE+'/'):
   errors.append([source,'path outside deployment base',url]);return None
  path=path[len(BASE):]or'/'
 target=DIST/path.lstrip('/')
 return target/'index.html'if target.is_dir()else target

pages=list(DIST.rglob('*.html'))
for f in pages:
 text=f.read_text();s=BeautifulSoup(text,'html.parser');source=str(f.relative_to(DIST))
 if '[Truncated]'in text:errors.append([source,'truncated source'])
 robots=s.select_one('meta[name="robots"]')
 if robots and 'noindex'in robots.get('content','').split(', '):noindex_pages+=1
 else:errors.append([source,'missing noindex'])
 for e in s.find_all(True):
  for k in e.attrs:
   if k.startswith('on'):errors.append([source,'inline handler',k])
  for k in['src','poster','href','data-href','data-motion-src']:
   u=e.get(k)
   if not u or u.startswith(('mailto:','tel:','#','data:','javascript:')):continue
   if u.startswith(('https:','http:','//')):
    if e.name in['script','img','link','source','video']and(k!='href'or e.name=='link'):remote_resources.add(u)
    continue
   if u.startswith('/'):
    target=local_target(u,source);refs+=1
    if target is not None and not target.exists():errors.append([source,k,u])
  for candidate in e.get('srcset','').split(','):
   u=candidate.strip().split(' ')[0]
   if not u:continue
   if u.startswith(('https:','http:','//')):remote_resources.add(u)
   elif u.startswith('/'):
    target=local_target(u,source);refs+=1
    if target is not None and not target.exists():errors.append([source,'srcset',u])
 for script in s.select('script[src]'):
  if script['src']!=BASE+'/site.js?v='+hashlib.sha256((DIST/'site.js').read_bytes()).hexdigest()[:16]:errors.append([source,'unexpected script',script['src']])
for f in(DIST/'assets').glob('*.css'):
 for url in re.findall(r'url\([\"\']?([^\"\'\)]+)',f.read_text(errors='replace')):
  if url.startswith('/')and not url.startswith('//'):
   target=local_target(url,f.name)
   if target is not None and not target.exists():errors.append([f.name,'css asset',url])
index=json.loads((DIST/'data/boards.json').read_text())
for rows in index.values():
 for row in rows:
  target=local_target(row['url'],'board search')
  if target is not None and not target.exists():errors.append(['board search','missing post',row['url']])
report={'pages':len(pages),'base_path':BASE,'noindex_pages':noindex_pages,'checked_local_references':refs,'board_entries':{k:len(v)for k,v in index.items()},'remote_resource_dependencies':sorted(remote_resources),'errors':errors}
(ROOT/'reports/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if errors or remote_resources:raise SystemExit(1)
