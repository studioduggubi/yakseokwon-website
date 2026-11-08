"""Validate generated routes, assets, base paths, and search exclusion."""
import json,pathlib,re,urllib.parse,hashlib,struct
from metadata import ORIGIN,OG_LOCALES
from collections import Counter
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
parsed={f:BeautifulSoup(f.read_text(),'html.parser')for f in pages}
for f in pages:
 text=f.read_text();s=parsed[f];source=str(f.relative_to(DIST))
 if len(s.select('h1'))!=1:errors.append([source,'expected one page heading'])
 if any('&rarr'in e.get_text()or e.get_text().rstrip().endswith(' &')for e in s.select('.show_body')):errors.append([source,'malformed preview arrow entity'])
 if s.select('.ys-kicker,.ys-bi-eyebrow,.ysw-eyebrow'):errors.append([source,'decorative title eyebrow remains'])
 if s.html.get('data-page-key')=='food'and s.select('#s20251019888fa302fab4d,.ys-rice-instructions,.ys-page-nav a[href="#s20251019888fa302fab4d"]'):errors.append([source,'retired rice-mix section remains'])
 if s.html.get('data-page-key')=='food'and s.select('a[href*="/products/3995890742"]'):errors.append([source,'food page links to reservation ticket'])
 if s.select('[data-youtube],.ys-video iframe'):errors.append([source,'embedded video playback remains'])
 if s.html.get('data-page-key')in['food','experience']and len(s.select('a.ys-video-link'))!=1:errors.append([source,'expected one native video link'])
 for video in s.select('a.ys-video-link'):
  url=urllib.parse.urlsplit(video.get('href',''));query=urllib.parse.parse_qs(url.query)
  if url.scheme!='https'or url.hostname!='www.youtube.com'or url.path!='/watch'or not re.fullmatch('[A-Za-z0-9_-]{11}',query.get('v',[''])[0]):errors.append([source,'invalid YouTube video URL'])
  if video.get('target')!='_blank'or'noopener'not in video.get('rel',[]):errors.append([source,'unsafe external video link'])
 duplicates=[key for key,count in Counter(e['id']for e in s.select('[id]')).items()if count>1]
 if duplicates:errors.append([source,'duplicate IDs',duplicates])
 # Sharing metadata must exist in the initial HTML, including every language route.
 canonical=ORIGIN+BASE+'/'+str(f.parent.relative_to(DIST)).replace('\\','/').strip('./')
 canonical=canonical.rstrip('/')+'/'
 if len(s.select('head link[rel=canonical]'))!=1 or s.select_one('head link[rel=canonical]').get('href')!=canonical:errors.append([source,'invalid canonical'])
 def metadata(name):
  nodes=s.select('head meta[property="'+name+'"],head meta[name="'+name+'"]')
  if len(nodes)!=1 or not nodes[0].get('content','').strip():errors.append([source,'missing or duplicate metadata',name]);return ''
  return nodes[0]['content']
 for name in ['og:title','og:description','og:type','og:url','og:site_name','og:locale','og:image','og:image:alt','og:image:width','og:image:height','og:image:type','twitter:card','twitter:title','twitter:description','twitter:image','twitter:image:alt','theme-color','description']:metadata(name)
 if metadata('og:url')!=canonical or metadata('og:title')!=s.title.get_text():errors.append([source,'inconsistent sharing title or URL'])
 if metadata('description')!=metadata('og:description') or metadata('twitter:description')!=metadata('description'):errors.append([source,'inconsistent descriptions'])
 if metadata('twitter:card')!='summary_large_image' or metadata('og:image:type')!='image/jpeg':errors.append([source,'invalid sharing card format'])
 if metadata('og:locale')!=OG_LOCALES[s.html['data-locale']]:errors.append([source,'wrong sharing language'])
 image_url=metadata('og:image')
 if image_url!=metadata('twitter:image') or not image_url.startswith(ORIGIN+BASE+'/social/'):errors.append([source,'invalid social image URL'])
 else:
  target=local_target(image_url,source)
  if not target.exists():errors.append([source,'missing social image'])
  if metadata('og:image:width')!='1200' or metadata('og:image:height')!='630':errors.append([source,'invalid social image dimensions'])
 alternates=s.select('head link[rel=alternate][hreflang]')
 if {e['hreflang']for e in alternates}!={'ko','en','zh-Hant','ja','x-default'} or len(alternates)!=5:errors.append([source,'incomplete language alternatives'])
 for e in alternates:
  path=urllib.parse.urlsplit(e['href']).path;target=local_target(path,source)
  if not target.exists():errors.append([source,'missing language alternative',e['href']])
  elif e['hreflang']!='x-default' and parsed.get(target) and parsed[target].html.get('lang')!=e['hreflang']:errors.append([source,'incorrect language alternative',e['href']])
 for selector in ['head link[rel=icon][type="image/svg+xml"]','head link[rel=icon][sizes="96x96"]','head link[rel=apple-touch-icon][sizes="180x180"]','head link[rel=manifest]']:
  if len(s.select(selector))!=1:errors.append([source,'missing browser metadata',selector])
 structured=s.select('head script[type="application/ld+json"]')
 try:
  graph=json.loads(structured[0].get_text())['@graph'];webpage=next(n for n in graph if n['@type']=='WebPage')
  if len(structured)!=1 or webpage['url']!=canonical or webpage['inLanguage']!=s.html['lang'] or webpage['name']!=s.title.get_text():errors.append([source,'inconsistent structured metadata'])
 except (IndexError,KeyError,StopIteration,ValueError):errors.append([source,'invalid structured metadata'])
 for anchor in s.select('a[href]'):
  url=urllib.parse.urlsplit(anchor['href'])
  if url.scheme or url.netloc or not url.fragment:continue
  target=local_target(url.path,source)if url.path else f
  if target in parsed and not parsed[target].find(id=urllib.parse.unquote(url.fragment)):errors.append([source,'missing fragment',anchor['href']])
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
    if e.name in['script','img','link','source','video']and(k!='href'or e.name=='link')and not(e.name=='link'and set(e.get('rel',[]))&{'canonical','alternate'}):remote_resources.add(u)
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
  if script['src'] not in[BASE+'/site.js?v='+hashlib.sha256((DIST/'site.js').read_bytes()).hexdigest()[:16],BASE+'/i18n.js?v='+hashlib.sha256((DIST/'i18n.js').read_bytes()).hexdigest()[:16]]and script['src']not in[BASE+'/i18n/'+p.name for p in(DIST/'i18n').glob('*.js')]:errors.append([source,'unexpected script',script['src']])
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
# The reported G-FAIR case and all event edges follow event start dates.
from datetime import date
from localize import EVENT_NAV_LABELS
calendar=[]
for row in index['events']:
 text=BeautifulSoup(row['html'],'html.parser').get_text(' ',strip=True);match=re.search(r'\b(20\d{2})\.(\d{2})\.(\d{2})',text)
 if not match:errors.append(['events','missing event start date',row['url']]);continue
 calendar.append((date(*map(int,match.groups())),row['url']))
calendar.sort(key=lambda row:row[0],reverse=True)
event_edges=0
for code,prefix in [('ko',''),('en','/en'),('zh-TW','/zh-TW'),('ja','/ja')]:
 for position,(_,url)in enumerate(calendar):
  route=prefix+url[len(BASE):];source=route;doc=parsed[DIST/route.strip('/')/'index.html'];actual=[];expected=[]
  for anchor in doc.select('.list_tap>a'):
   relation=' '.join(anchor.get('rel',[]));actual.append((relation,anchor.get('href')))
   label=EVENT_NAV_LABELS[code][0 if relation=='prev'else 1]
   if not anchor.get_text(' ',strip=True).startswith(label+' · '):errors.append([source,'incorrect event direction label'])
   event_edges+=1
  for relation,neighbor in [('prev',position+1),('next',position-1)]:
   if 0<=neighbor<len(calendar):expected.append((relation,BASE+prefix+calendar[neighbor][1][len(BASE):]))
  if actual!=expected:errors.append([source,'event chronology mismatch',actual,expected])
report={'pages':len(pages),'base_path':BASE,'noindex_pages':noindex_pages,'checked_local_references':refs,'board_entries':{k:len(v)for k,v in index.items()},'event_navigation_edges':event_edges,'remote_resource_dependencies':sorted(remote_resources),'errors':errors}
(ROOT/'reports/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if errors or remote_resources:raise SystemExit(1)
