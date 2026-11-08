"""Build static language pages using reviewed, versioned local copy dictionaries."""
import hashlib,html,json,re,urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup,Comment,NavigableString
from media_links import localize_videos
from metadata import apply_metadata
KR=re.compile('[가-힣]')
BLOCKS=['h1','h2','h3','h4','h5','h6','p','label','legend','option']
def norm(text):return re.sub(r'\s+',' ',str(text)).strip()
def collect_units(doc):
 blocks=[];selected=set()
 for e in doc.find_all(BLOCKS):
  if e.find_parent(['script','style','svg','noscript'])or e.select_one('a,img,svg,input,textarea,button,video,iframe,h1,h2,h3,h4,h5,h6,p'):continue
  value=norm(e.get_text(' ',strip=True))
  if KR.search(value):blocks.append((e,'block',value));selected.add(id(e))
 result=list(blocks)
 for n in doc.find_all(string=True):
  if isinstance(n,Comment)or n.find_parent(['script','style','svg','noscript']):continue
  if any(id(p)in selected for p in n.parents):continue
  value=norm(n)
  if KR.search(value):result.append((n,'text',value))
 for e in doc.find_all(True):
  for attr in['aria-label','title','placeholder','alt']:
   if e.get(attr)and KR.search(e[attr]):result.append((e,attr,norm(e[attr])))
  if e.name=='meta'and e.get('name')=='description'and KR.search(e.get('content','')):result.append((e,'content',norm(e['content'])))
 return result

def translate(doc,strings,missing,context):
 for node,kind,value in collect_units(doc):
  translated=strings.get(value)
  if translated is None:missing.add((context,kind,value));continue
  if kind=='block':
   # Preserve a uniform inline text colour when replacing styled source spans.
   # Font sizes and line breaks stay with the responsive semantic CSS.
   colours=[]
   for leaf in node.find_all(string=True):
    if isinstance(leaf,Comment)or not norm(leaf):continue
    colour=None
    for ancestor in leaf.parents:
     match=re.search(r'(?:^|;)\s*color\s*:\s*([^;]+)',ancestor.get('style',''),re.I)
     if match:colour=match[1].strip();break
     if ancestor is node:break
    colours.append(colour)
   if colours and colours[0]and len(set(colours))==1:
    style=re.sub(r'(?:^|;)\s*color\s*:[^;]*','',node.get('style',''),flags=re.I).strip('; ')
    node['style']=style+';color:'+colours[0]+';'
   node.clear();node.append(translated)
  elif kind=='text':
   raw=str(node);leading=re.match(r'^\s*',raw)[0];trailing=re.search(r'\s*$',raw)[0]
   node.replace_with(NavigableString(leading+translated+trailing))
  else:node[kind]=translated

def route_url(route,locale,base):return base+locale['prefix']+route

def rewrite_links(doc,locale,base,routes):
 for e in doc.find_all(True):
  for attr in['href','data-href','action']:
   value=e.get(attr,'')
   if not value or value.startswith('#'):continue
   if value.startswith('tel:')and locale['code']!='ko':
    number=re.sub(r'[^+0-9]','',value[4:])
    if number.startswith('0'):
     e[attr]='tel:+82'+number[1:]
     if e.name=='a'and re.fullmatch(r'[0-9\-\s]+',e.get_text(strip=True)):
      e.clear();e.append('+82 '+value[5:])
    continue
   u=urllib.parse.urlsplit(value)
   if u.scheme or u.netloc:continue
   if base and not(u.path==base or u.path.startswith(base+'/')):continue
   route=u.path[len(base):]or'/'
   canonical=route if route.endswith('/')else route+'/'
   if canonical not in routes:continue
   e[attr]=route_url(canonical,locale,base)+('?' +u.query if u.query else'')+('#'+u.fragment if u.fragment else'')

def language_control(doc,locale,locales,base,route):
 labels={'ko':('언어 선택','언어'),'en':('Choose language','Languages'),'zh-TW':('選擇語言','語言'),'ja':('言語を選択','言語')}
 control=doc.new_tag('details',attrs={'class':'ys-language'})
 summary=doc.new_tag('summary',attrs={'aria-label':labels[locale['code']][0]})
 flag=doc.new_tag('span',attrs={'class':'ys-language-flag','aria-hidden':'true'});flag.string=locale['flag'];summary.append(flag)
 short=doc.new_tag('span');short.string=locale['short'];summary.append(short)
 chevron=doc.new_tag('span',attrs={'class':'ys-language-chevron','aria-hidden':'true'});chevron.string='⌄';summary.append(chevron);control.append(summary)
 nav=doc.new_tag('nav',attrs={'aria-label':labels[locale['code']][1]})
 for item in locales:
  a=doc.new_tag('a',href=route_url(route,item,base),attrs={'lang':item['html_lang'],'hreflang':item['html_lang'],'data-language':item['code']})
  flag=doc.new_tag('span',attrs={'aria-hidden':'true'});flag.string=item['flag'];a.append(flag);a.append(' '+item['name'])
  if item['code']==locale['code']:a['aria-current']='true'
  nav.append(a)
 control.append(nav)
 header=doc.select_one('header#doz_header_wrap')or doc.select_one('header')
 if header:header.append(control)
 else:doc.body.insert(0,control)

def localize_site(root,dist,route_index,base):
 (root/'reports/posters-i18n-20261108').mkdir(parents=True,exist_ok=True)
 folder=root/'content/locales';config=folder/'config.json'
 if not config.exists():return route_index
 locales=json.loads(config.read_text())['locales'];catalogue=json.loads((folder/'catalogue.json').read_text());raw_ui=json.loads((folder/'ui.json').read_text())
 sources={r['route']:(dist/r['route'].strip('/')/'index.html').read_text()for r in route_index}
 routes=set(sources);missing=set();runtime_files={};dictionaries={}
 runtime_folder=dist/'i18n';runtime_folder.mkdir(exist_ok=True)
 helper=(root/'src/i18n.js').read_bytes();(dist/'i18n.js').write_bytes(helper);helper_hash=hashlib.sha256(helper).hexdigest()[:16]
 for index,code in enumerate(['en','zh-TW','ja']):
  data=json.loads((folder/(code+'.json')).read_text());strings={source:data[key]for key,source in catalogue.items()if key in data};strings.update({s:v[index]for s,v in raw_ui.items()});dictionaries[code]=strings
  payload=('window.ysLocale='+json.dumps({'code':code,'strings':strings},ensure_ascii=False,separators=(',',':'))+';\n').encode();digest=hashlib.sha256(payload).hexdigest()[:16];name=code+'-'+digest+'.js';(runtime_folder/name).write_bytes(payload);runtime_files[code]='/i18n/'+name
 result=[]
 for page in route_index:
  route=page['route']
  for locale in locales:
   code=locale['code'];doc=BeautifulSoup(sources[route],'html.parser')
   if code!='ko':translate(doc,dictionaries[code],missing,code+route)
   doc.html['lang']=locale['html_lang'];doc.html['data-locale']=code;doc.html['data-locale-base']=locale['prefix']
   rewrite_links(doc,locale,base,routes);language_control(doc,locale,locales,base,route)
   # Metadata describes the current article, rather than a captured adjacent post.
   if page['key'].startswith('post-'):
    body=doc.select_one('.board_txt_area');description=doc.select_one('meta[name=description]')
    if body and description:description['content']=norm(body.get_text(' ',strip=True))[:190]
   if code!='ko'and page['key']in['terms','privacy']:
    source_label={'en':('Reference translation of the current Korean policy.','Read the Korean original'),'zh-TW':('依目前韓文政策原文翻譯，供參考。','閱讀韓文原文'),'ja':('現在の韓国語原文に基づく参考訳です。','韓国語の原文を読む')}[code]
    policy=doc.select_one('.ys-policy')
    if policy:
     note=doc.new_tag('p',attrs={'class':'ys-policy-source'});note.append(source_label[0]+' ');a=doc.new_tag('a',href=base+route,attrs={'lang':'ko'});a.string=source_label[1];note.append(a);policy.select_one('h1').insert_after(note)
   localize_videos(doc,code,base)
   main_script=doc.select_one('script[src*="/site.js"]')
   if code!='ko':
    script=doc.new_tag('script',src=base+runtime_files[code],attrs={'defer':''});main_script.insert_before(script)
   main_script.insert_before(doc.new_tag('script',src=base+'/i18n.js?v='+helper_hash,attrs={'defer':''}))
   apply_metadata(doc,page,locale,locales,root,base,route)
   output_route=locale['prefix']+route;target=dist/output_route.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(str(doc))
   result.append({**page,'route':output_route,'locale':code,'title':doc.title.get_text()})
 # Every language gets its own searchable article text and preview markup.
 index=json.loads((dist/'data/boards.json').read_text())
 for locale in locales:
  if locale['code']=='ko':continue
  strings=dictionaries[locale['code']];translated_index={kind:[]for kind in index}
  for kind,rows in index.items():
   for row in rows:
    fragment=BeautifulSoup(row['html'],'html.parser');translate(fragment,strings,missing,'search:'+locale['code']);rewrite_links(fragment,locale,base,routes)
    path=urllib.parse.urlsplit(row['url']).path;route=path[len(base):]if base else path
    article_path=dist/(locale['prefix']+route).strip('/')/'index.html';article=BeautifulSoup(article_path.read_text(),'html.parser')
    text=norm(fragment.get_text(' ',strip=True))+' '+' '.join(norm(n.get_text(' ',strip=True))for n in article.select('.view_tit,.board_txt_area'))
    translated_index[kind].append({'url':route_url(route,locale,base),'text':text,'html':str(fragment)})
  target=dist/locale['prefix'].strip('/')/'data/boards.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(translated_index,ensure_ascii=False))
 report={'locales':[l['code']for l in locales],'routes':len(result),'source_units':len(catalogue),'missing':[{'context':a,'kind':b,'source':c}for a,b,c in sorted(missing)],'runtime_files':runtime_files}
 (root/'reports/posters-i18n-20261108/localization-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if missing:raise RuntimeError('Missing translations: '+str(len(missing))+'; see localization-build.json')
 return result
