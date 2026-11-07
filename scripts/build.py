"""Generate the independently served site from public content and localized assets."""
import hashlib,html,json,pathlib,re,shutil,urllib.parse,zipfile,os
from bs4 import BeautifulSoup
from assets import preferred_fonts,URL,IMPORT,canonical
ROOT=pathlib.Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
RUNTIME_JS_HASH=hashlib.sha256((ROOT/'src/site.js').read_bytes()).hexdigest()[:16]
RUNTIME_CSS_HASH=hashlib.sha256((ROOT/'src/site.css').read_bytes()).hexdigest()[:16]
BASE_PATH='/'+os.environ.get('SITE_BASE_PATH','').strip('/')if os.environ.get('SITE_BASE_PATH','').strip('/')else''
if not re.fullmatch(r'(?:/[A-Za-z0-9._-]+)*',BASE_PATH)or any(x in['.','..']for x in BASE_PATH.split('/')):raise ValueError('Invalid SITE_BASE_PATH')
MAP=json.loads((ROOT/'content/asset-map.json').read_text())
DOWNLOADS={x['href']:'/downloads/'+x['file']for x in json.loads((ROOT/'content/downloads.json').read_text())}
ROUTES={'home':'/','experience':'/Yakssuk/','food':'/food/','resources':'/events/','newsroom':'/newsroom/','brand':'/bi/','directions':'/2xlqqbbm/','tea':'/index2/','legacy-experience':'/2zf7yx5i/','legacy-food':'/2vu8cpl9/','legacy-store':'/20/','legacy-company':'/cq90acnd/','newsroom-page-2':'/newsroom/page/2/','newsroom-page-3':'/newsroom/page/3/'}
def public_path(value):
 if not BASE_PATH or not value.startswith('/')or value.startswith('//'):return value
 if value==BASE_PATH or value.startswith(BASE_PATH+'/'):return value
 return BASE_PATH+value

def prefix_css(text):
 text=URL.sub(lambda m:'url("'+public_path(m.group(1))+'")',text)
 return IMPORT.sub(lambda m:'@import "'+public_path(m.group(1))+'"',text)

def prefix_html(text):
 if not BASE_PATH:return text
 doc=BeautifulSoup(text,'html.parser')
 for e in doc.find_all(True):
  for attr in['href','src','poster','data-href','data-original','action']:
   if e.get(attr):e[attr]=public_path(e[attr])
  if e.get('srcset'):
   e['srcset']=', '.join(public_path(part.strip().split(' ')[0])+(' '+part.strip().split(' ',1)[1]if' 'in part.strip()else'')for part in e['srcset'].split(','))
  if e.get('style'):e['style']=prefix_css(e['style'])
  if e.name=='style':e.string=prefix_css(e.get_text())
 return str(doc)

def page_route(key):
 if key.startswith('post-'):
  _,kind,idx=key.split('-');return '/'+('events'if kind=='event'else'newsroom')+'/'+idx+'/'
 return ROUTES[key]
def href(value,base):
 if not value:return value
 if value.startswith(('tel:','mailto:','#')):return value
 u=urllib.parse.urlsplit(urllib.parse.urljoin(base,value));q=urllib.parse.parse_qs(u.query)
 if u.hostname not in ['yakseokwon.com','www.yakseokwon.com']:return value
 path=u.path.rstrip('/')or'/'
 if path=='/download.cm':return DOWNLOADS.get(u.path+'?'+u.query,'https://yakseokwon.com'+u.path+'?'+u.query)
 if 'idx'in q and path in ['/newsroom','/events']:return path+'/'+q['idx'][0]+'/'
 if q.get('mode')==['policy']:return '/terms/'
 if q.get('mode')==['privacy']:return '/privacy/'
 if path=='/newsroom'and q.get('page',['1'])[0]!='1':return '/newsroom/page/'+q['page'][0]+'/'
 if path in ['/','/index']:path='/'
 elif path=='/about':path='/events/'
 elif path in [r.rstrip('/')for r in ROUTES.values()]:path=path+'/'
 else:return value
 return path+('#'+u.fragment if u.fragment else'')
def asset(v,base):
 u=canonical(v,base)
 if not u:return v
 out=MAP.get(u,v);fragment=urllib.parse.urlsplit(v).fragment
 return out+('#'+fragment if fragment and u in MAP else'')
def css(t,base):
 t=preferred_fonts(t)
 t=URL.sub(lambda m:'url("'+asset(m.group(1),base)+'")',t)
 return IMPORT.sub(lambda m:'@import "'+asset(m.group(1),base)+'"',t)
def sanitize(p):
 s=BeautifulSoup(p['html'],'html.parser')
 for e in s.select('script,iframe,input[type=hidden],.like_btn,.like_token,.post_tools,.comment_write,.imweb_footer,#fo_board_spam_guard_notice'):
  e.decompose()
 for e in s.select('a[href^="/admin/"]'):e.decompose()
 for e in list(s.select('a,button')):
  if e.get_text(' ',strip=True)in ['수정','지우기','글쓰기','작성','저장','공유하기']:e.decompose()
 for e in s.find_all(True):
  if not e.attrs:continue
  for k in list(e.attrs):
   if k.startswith('on'):
    old=e.attrs.pop(k)
    if k=='onclick'and isinstance(old,str):
     if 'MOBILE_SLIDE_MENU' in old:e['data-menu-toggle']='';e['role']='button';e['aria-label']='메뉴 열기';e['aria-expanded']='false';e['href']='#ys-mobile-nav'
     m=re.search(r"location\.href\s*=\s*['\"]([^'\"]+)",old)
     if m:e['data-href']=href(m.group(1),p['url']);e['tabindex']='0';e['role']='link'
   elif any(x in k.lower()for x in ['token','csrf','session','member_id','user_id']):del e.attrs[k]
  for k in ['src','poster','data-original']:
   if e.get(k):e[k]=asset(e[k],p['url'])
  if e.get('srcset'):
   e['srcset']=', '.join(asset(part.strip().split(' ')[0],p['url'])+(' '+part.strip().split(' ',1)[1]if' 'in part.strip()else'')for part in e['srcset'].split(','))
  if e.get('href'):e['href']=href(e['href'],p['url'])
  if e.get('style'):e['style']=css(e['style'],p['url'])
  if e.name=='style':e.string=css(e.get_text(),p['url'])
  if e.name=='form':e['action']='#';e['method']='get'
 for a in s.select('header a[href]'):
  if a.get('href','').startswith('/')and not a.get('href','').startswith('//'):
   a['class']=[c for c in a.get('class',[])if c!='disabled']
   a.attrs.pop('data-toggle',None);a.attrs.pop('aria-disabled',None)
 for box in s.select('[data-widget-type="video"]'):
  old=box.select_one('[data-vimeo-id]');img=box.select_one('img')
  vid=old.get('data-vimeo-id')if old else None
  if not vid:continue
  target=box.select_one('.widget.movie')or box
  src=img.get('src','')if img else''
  target.clear();target['class']=['widget','movie','ys-video'];target.attrs.pop('style',None)
  button=s.new_tag('button',type='button',attrs={'data-youtube':vid,'aria-label':'약석원 '+('좌훈'if vid=='eSqoQWNZdxw'else'건강밥'if vid=='v2MK2laprFI'else'체험')+' 소개 영상 재생'})
  image=s.new_tag('img',src=src,alt='');button.append(image);play=s.new_tag('span',attrs={'class':'ys-play','aria-hidden':'true'});button.append(play);target.append(button)
 for card in s.select('[data-href]'):
  for a in card.select('a._fade_link'):a['href']=card['data-href']
 for b in s.select('button'):
  if b.get_text(strip=True)=='목록':b['data-href']='/events/'if'/events'in p['url']else'/newsroom/'
 if'/newsroom'in p['url']:
  current=int(urllib.parse.parse_qs(urllib.parse.urlsplit(p['url']).query).get('page',['1'])[0])
  for a in s.select('.pagination a'):
   text=a.get_text(' ',strip=True)
   if'Previous'in text or'Next'in text:
    target=current+(-1 if'Previous'in text else 1)
    if 1<=target<=3:a['href']='/newsroom/'if target==1 else'/newsroom/page/'+str(target)+'/'
    else:a.attrs.pop('href',None);a['aria-disabled']='true';a['tabindex']='-1'
 for e in s.select('.owl-item.cloned'):e.decompose()
 for link in s.select('a[href="/events/"]'):
  if link.get_text(strip=True)=='자료실'and link.parent and not link.parent.select_one('.ys-subnav'):
   parent=link.parent
   if parent.name not in ['li','div']:continue
   parent['class']=list(parent.get('class',[]))+['ys-data-menu']
   nav=s.new_tag('div',attrs={'class':'ys-subnav'})
   for label,url in [('행사 일정','/events/'),('뉴스룸','/newsroom/'),('브랜드','/bi/'),('오시는 길','/2xlqqbbm/')]:
    a=s.new_tag('a',href=url);a.string=label;nav.append(a)
   parent.append(nav)
 return str(s)
def drawer():
 links=[('약석원','/'),('좌훈 치유 체험관','/Yakssuk/'),('약식동원 건강식','/food/'),('행사 일정','/events/'),('뉴스룸','/newsroom/'),('브랜드','/bi/'),('오시는 길','/2xlqqbbm/')]
 return '<div class="ys-mobile-nav" id="ys-mobile-nav" hidden><div class="ys-mobile-panel" role="dialog" aria-modal="true" aria-label="전체 메뉴"><button class="ys-menu-close" data-menu-close>닫기 ×</button>'+''.join('<a href="'+u+'">'+t+'</a>'for t,u in links)+'</div></div>'
def hero_motion(key,body):
 config=ROOT/'content/hero-motion.json'
 if not config.exists():return body
 motion=json.loads(config.read_text()).get(key)
 if not motion:return body
 if not(ROOT/'public'/motion['src'].lstrip('/')).is_file():raise RuntimeError('Hero video is missing')
 doc=BeautifulSoup(body,'html.parser');section=doc.find(id=motion['section'])
 if not section:return body
 bg=section.select_one('.section_bg')
 if not bg:return body
 bg['class']=list(bg.get('class',[]))+['ys-motion-bg']
 # Preserve the captured positioning: the mobile fixed-image wrapper clips its children.
 # Replacing the whole style removes its absolute inset and collapses that wrapper to zero height.
 original_style=bg.get('style','')
 replacement='background-image:url("'+motion['poster']+'");'
 bg['style']=re.sub(r'background-image\s*:[^;]*;?',replacement,original_style,flags=re.I)if re.search(r'background-image\s*:',original_style,re.I)else original_style+';'+replacement
 for image in bg.select('img'):
  image['src']=motion['poster'];image.attrs.pop('srcset',None)
 video=doc.new_tag('video',attrs={'class':'ys-hero-motion','autoplay':'','muted':'','loop':'','playsinline':'','preload':'metadata','poster':motion['poster'],'aria-hidden':'true','tabindex':'-1'})
 video.append(doc.new_tag('source',src=motion['src'],type='video/mp4'));bg.append(video)
 button=doc.new_tag('button',type='button',attrs={'class':'ys-motion-toggle','aria-label':'배경 영상 일시정지','aria-pressed':'false','hidden':''});button.string='일시정지';section.append(button)
 return str(doc)
def write_page(key,p,content=None):
 route=page_route(key)if key not in ['terms','privacy']else'/'+key+'/'
 head='<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow, noarchive"><title>'+html.escape(p['title'])+'</title><meta name="description" content="'+html.escape(p.get('description',''),quote=True)+'">'
 early='\n'.join(css(t,p['url'])for t in p['styles'][:2])
 early_name='base-'+hashlib.sha256(early.encode()).hexdigest()[:16]+'.css';(DIST/'assets'/early_name).write_text(early)
 head+='<link rel="stylesheet" href="/assets/'+early_name+'">'
 head+=''.join('<link rel="stylesheet" href="'+MAP.get(u,u)+'">'for u in p['stylesheets'])
 style='\n'.join(css(t,p['url'])for t in p['styles'][2:])
 name='page-'+hashlib.sha256(style.encode()).hexdigest()[:16]+'.css';(DIST/'assets'/name).write_text(style)
 head+='<link rel="stylesheet" href="/assets/'+name+'"><link rel="stylesheet" href="/site.css?v='+RUNTIME_CSS_HASH+'">'
 body=hero_motion(key,content if content is not None else sanitize(p))
 doc='<!doctype html><html lang="ko" data-page-key="'+html.escape(key,quote=True)+'" data-site-base="'+html.escape(BASE_PATH,quote=True)+'" class="'+html.escape(p['htmlClass'],quote=True)+'"><head>'+head+'</head><body id="doz_body" class="'+html.escape(p['bodyClass'],quote=True)+'">'+body+drawer()+'<script src="/site.js?v='+RUNTIME_JS_HASH+'" defer></script></body></html>'
 dest=DIST/route.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(prefix_html(doc))
 return route
def main():
    missing=[v for v in list(MAP.values())+list(DOWNLOADS.values())if not(ROOT/'public'/v.lstrip('/')).exists()]
    if missing:
     for archive in sorted(ROOT.glob('assets-*.zip')):
      with zipfile.ZipFile(archive)as z:
       for member in z.infolist():
        path=pathlib.PurePosixPath(member.filename)
        if path.is_absolute()or'..'in path.parts or path.parts[:2]not in[('public','assets'),('public','downloads')]:raise ValueError('Invalid asset archive entry')
       z.extractall(ROOT)
    missing=[v for v in list(MAP.values())+list(DOWNLOADS.values())if not(ROOT/'public'/v.lstrip('/')).exists()]
    if missing:raise RuntimeError('Missing bundled assets: '+str(len(missing)))
    (ROOT/'reports').mkdir(exist_ok=True)
    if DIST.exists():shutil.rmtree(DIST)
    shutil.copytree(ROOT/'public',DIST)
    for file in ['site.css','site.js']:shutil.copy2(ROOT/'src'/file,DIST/file)
    route_index=[]
    for f in sorted((ROOT/'content/pages').glob('*.json')):
     if f.name=='bundle-manifest.json':continue
     p=json.loads(f.read_text())
     if not isinstance(p,dict)or'html'not in p:continue
     route_index.append({'key':f.stem,'route':write_page(f.stem,p),'title':p['title'],'source':p['url']})
    board_index={'newsroom':[],'events':[]}
    for key in ['resources','newsroom','newsroom-page-2','newsroom-page-3']:
        data=json.loads((ROOT/'content/pages'/(key+'.json')).read_text());bs=BeautifulSoup(sanitize(data),'html.parser')
        kind='events'if key=='resources'else'newsroom'
        selector='.type_row>ul.list'if kind=='events'else'.type_masonry>.ma-item'
        for card in bs.select(selector):
            link=card.select_one('a[href]')if kind=='events'else card.select_one('[data-href]')
            url=link.get('href'if kind=='events'else'data-href','')if link else''
            match=re.search(r'/([0-9]+)/',url)
            if not match:continue
            detail=ROOT/'content/pages'/('post-'+('event'if kind=='events'else'news')+'-'+match[1]+'.json')
            text=card.get_text(' ',strip=True)
            if detail.exists():
             article=BeautifulSoup(json.loads(detail.read_text())['html'],'html.parser')
             for common in article.select('header,footer'):common.decompose()
             text+=' '+article.get_text(' ',strip=True)
            board_index[kind].append({'url':url,'text':text,'html':str(card)})
    (DIST/'data').mkdir(exist_ok=True);(DIST/'data/boards.json').write_text(json.dumps(board_index,ensure_ascii=False))
    # Preserve the published policy text as content; factual placeholders remain explicitly pending in the translation plan.
    home=json.loads((ROOT/'content/pages/home.json').read_text());hs=BeautifulSoup(sanitize(home),'html.parser')
    for key,name in [('terms','이용약관'),('privacy','개인정보처리방침')]:
     raw=json.loads((ROOT/'content'/('policy-'+key+'.json')).read_text())['text'].split('\n닫기\n',1)[1]
     p={**home,'title':name+' — 약석원','bodyClass':'doz_sys new_header_site page'}
     content=str(hs.select_one('header'))+'<main class="ys-policy"><h1>'+name+'</h1>'+html.escape(raw)+'</main>'+str(hs.select_one('footer'))
     route_index.append({'key':key,'route':write_page(key,p,content),'title':p['title']})
    (DIST/'_redirects').write_text('/index / 301\n/about /events/ 301\n/index.html / 301\n')
    (DIST/'robots.txt').write_text('# HTML noindex directives disable search indexing.\nUser-agent: *\nAllow: /\n')
    (DIST/'.nojekyll').touch()
    if BASE_PATH:
     for sheet in (DIST/'assets').glob('*.css'):sheet.write_text(prefix_css(sheet.read_text()))
     for rows in board_index.values():
      for row in rows:row['url']=public_path(row['url']);row['html']=prefix_html(row['html'])
     (DIST/'data/boards.json').write_text(json.dumps(board_index,ensure_ascii=False))
    (ROOT/'reports/routes.json').write_text(json.dumps(route_index,ensure_ascii=False,indent=2))
    print('Built',len(route_index),'pages; localized assets',len(MAP))

if __name__=="__main__":main()
