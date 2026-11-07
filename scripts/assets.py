"""Copy observed public page assets and localize their referenced CSS/font files."""
import concurrent.futures,hashlib,json,mimetypes,pathlib,re,shutil,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'public/assets'; OUT.mkdir(parents=True,exist_ok=True)
CSS=ROOT/'content/css';CSS.mkdir(parents=True,exist_ok=True)
MAP=ROOT/'content/asset-map.json'
asset_map=json.loads(MAP.read_text()) if MAP.exists() else {}
errors={}
FONTFACE=re.compile(r'@font-face\s*\{[^{}]*\}',re.I|re.S)
URL=re.compile(r'url\(\s*[\"\']?([^\"\'\)]+)[\"\']?\s*\)',re.I)
IMPORT=re.compile(r'@import\s+[\"\']([^\"\']+)[\"\']',re.I)
def canonical(url,base):
 url=url.strip().replace('&amp;','&')
 if not url or url.startswith(('data:','#','blob:','javascript:')): return None
 u=urllib.parse.urljoin(base,url);return urllib.parse.urldefrag(u)[0] if u.startswith(('https://','http://')) else None
def filename(url,kind=None,ctype=''):
 ext=pathlib.Path(urllib.parse.urlsplit(url).path).suffix.lower()
 if kind=='stylesheet' or 'text/css' in ctype:ext='.css'
 if not ext or len(ext)>7:ext=mimetypes.guess_extension(ctype.split(';')[0]) or '.bin'
 return hashlib.sha256(url.encode()).hexdigest()[:18]+ext
def copy_bundles():
 for x in json.loads((ROOT/'capture/bundle-manifest.json').read_text()):
  u=x['url'];name=filename(u,x['kind'],x.get('contentType')or'');dest=OUT/name
  if not dest.exists():shutil.copy2(x['path'],dest)
  asset_map[u]='/assets/'+name
  if name.endswith('.css') and not (CSS/name).exists():shutil.copy2(x['path'],CSS/name)
def preferred_fonts(t):
 def face(m):
  block=m.group();u=URL.findall(block)
  if not u:return block
  choices=[x for x in u if '.woff2' in x] or [x for x in u if '.woff' in x] or [x for x in u if '.ttf' in x] or u
  choice=choices[0];fmt='woff2' if '.woff2' in choice else 'woff' if '.woff' in choice else 'truetype' if '.ttf' in choice else ''
  block=re.sub(r'\bsrc\s*:[^;]+;', '',block,flags=re.I|re.S)
  return block[:-1]+('font-display:swap;'if'font-display'not in block else'')+'src: url("'+choice+'")'+(' format("'+fmt+'")'if fmt else'')+';}'
 return FONTFACE.sub(face,t)
def fetch(item):
 u,kind=item
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; StudioDuggubiSiteMigration/1.0)'})
  with urllib.request.urlopen(req,timeout=25) as f:content=f.read();ctype=f.headers.get('Content-Type','')
  name=filename(u,kind,ctype);(OUT/name).write_bytes(content)
  if name.endswith('.css'):(CSS/name).write_bytes(content)
  return u,'/assets/'+name,None
 except Exception as e:return u,None,str(e)
def refs(t,base):
 t=preferred_fonts(t)
 return {u:('stylesheet' if '.css' in urllib.parse.urlsplit(u).path or 'fonts.googleapis.com' in u else None)for v in URL.findall(t)+IMPORT.findall(t) if(u:=canonical(v,base))}
def run():
 copy_bundles();pending={}
 for f in (ROOT/'capture').glob('*.json'):
  if f.name=='bundle-manifest.json':continue
  p=json.loads(f.read_text())
  if not isinstance(p,dict) or 'html'not in p:continue
  for u in p['stylesheets']:
   if u not in asset_map:pending[u]='stylesheet'
  for t in p['styles']:
   for u,k in refs(t,p['url']).items():
    if u not in asset_map:pending[u]=k
  from bs4 import BeautifulSoup
  soup=BeautifulSoup(p['html'],'html.parser')
  for el in soup.select('img,source,video'):
   for attr in ['src','poster','data-original']:
    if el.get(attr) and (u:=canonical(el[attr],p['url'])) and u not in asset_map:pending[u]=None
  for el in soup.select('[style]'):
   for u,k in refs(el['style'],p['url']).items():
    if u not in asset_map:pending[u]=k
 for iteration in range(6):
  for original,local in list(asset_map.items()):
   if not local.endswith('.css'):continue
   sf=CSS/pathlib.Path(local).name
   if not sf.exists():continue
   for u,k in refs(sf.read_text(errors='replace'),original).items():
    if u not in asset_map and u not in errors:pending[u]=k
  pending={u:k for u,k in pending.items()if u not in asset_map and u not in errors}
  if not pending:break
  batch=list(pending.items());pending={};print('Asset round',iteration+1,'requests',len(batch),flush=True)
  with concurrent.futures.ThreadPoolExecutor(max_workers=12)as pool:
   for u,local,error in pool.map(fetch,batch):
    if error:errors[u]=error
    else:asset_map[u]=local
  MAP.write_text(json.dumps(asset_map,ensure_ascii=False,indent=2))
 for original,local in asset_map.items():
  if not local.endswith('.css'):continue
  sf=CSS/pathlib.Path(local).name
  if not sf.exists():continue
  t=preferred_fonts(sf.read_text(errors='replace'))
  t=URL.sub(lambda m:'url("'+asset_map.get(canonical(m.group(1),original),m.group(1))+'")',t)
  t=IMPORT.sub(lambda m:'@import "'+asset_map.get(canonical(m.group(1),original),m.group(1))+'"',t)
  (OUT/pathlib.Path(local).name).write_text(t)
 MAP.write_text(json.dumps(asset_map,ensure_ascii=False,indent=2))
 (ROOT/'reports/asset-download.json').write_text(json.dumps({'assets':len(asset_map),'errors':errors},ensure_ascii=False,indent=2))
 print('Assets',len(asset_map),'failures',len(errors),'bytes',sum(f.stat().st_size for f in OUT.iterdir()),flush=True)
if __name__=='__main__':run()
