"""Explicit page hierarchy for the migrated site, independent of Imweb's runtime."""
import html,re,json
from pathlib import Path
from bs4 import BeautifulSoup
DIMENSIONS=json.loads((Path(__file__).resolve().parents[1]/'content/image-dimensions.json').read_text())

PAGES={'home':'약석원','experience':'강화 약쑥 좌훈 체험','food':'약식동원 건강식','brand':'브랜드 이야기','directions':'오시는 길','resources':'행사 일정','newsroom':'뉴스룸','newsroom-page-2':'뉴스룸','newsroom-page-3':'뉴스룸','tea':'차와 쉼','legacy-company':'기업 소개','legacy-experience':'좌훈 안내','legacy-food':'제품 이야기','legacy-store':'제품 안내','terms':'이용약관','privacy':'개인정보처리방침'}
SECTIONS={
'home':[
('s2025082708e37bc9e4299','약석원의 철학','자연과 사람을 잇는 건강의 순환','철학','white'),
('s2025082735e169b78daa4','세 가지 경험','몸을 돌보고, 일상을 채우는 시간','체험','soft'),
('s202508270af596c0f134f','공간의 이야기','자연을 닮은 약석원의 공간','공간','white'),
('s20250827ed93354d7f794','강화에서 일상으로','강화에서 시작된 치유의 철학','이야기','dark'),
('s202508292f3f057464dfa','방문 안내','약석원에 오시는 길','방문 안내','white')],
'experience':[
('s20261105de741ddc25f0f','영상으로 만나보세요','약석원 좌훈 이야기','소개 영상','white'),
('s202508280a754fcb85685','좌훈 알아보기','전통의 지혜, 현대의 웰니스','좌훈 소개','soft'),
('s2025082903c5b6a7df730','약쑥과 옹기의 온기','약석원의 좌훈 체험','체험 안내','white'),
('s202508288e97ef60eeab2','따뜻하게 쉬어가는 시간','전통 좌훈과 쑥 온열법','온열 체험','dark'),
('s20250829f1c8d62e09ed7','체험 과정','좌훈 체험은 이렇게 진행돼요','체험 순서','white'),
('s20250829a7d95a6c94093','함께한 사람들의 이야기','체험자들이 전하는 회복의 순간','체험 후기','soft'),
('s202508311b03563c846fd','창업·제휴','약석원과 함께할 파트너를 찾습니다','제휴 문의','white')],
'food':[
('s202611054eb3f0835e4d0','영상으로 만나보세요','약석원 건강밥 이야기','소개 영상','white'),
('s2025083182a0e00d9782d','밥상에 담은 마음','밥은 단순한 한 끼가 아닙니다','건강식 소개','soft'),
('s20250831745b0f79e4873','좋은 한 끼의 시작','정직한 재료로 만드는 건강한 밥','만드는 마음','white'),
('s202508318c66279bacdf6','곡물 하나하나, 정성껏','가족을 위한 마음으로, 가장 좋은 재료로','곡물 소개','soft'),
('s202508318fc100fe1710e','데워서 간편하게','전자레인지 3분, 따뜻한 건강밥','건강밥','white'),
('s20251019888fa302fab4d','밥을 지을 때 한 포','매일의 밥상에 더하는 건강미','건강미','soft'),
('s20250831d8a568156473c','함께한 사람들의 이야기','한 번 드시면 다시 찾는 이유','제품 후기','white'),
('s20250831129c8141b6c35','믿고 선택하는 기준','제품의 품질을 확인하는 인증','인증 안내','soft')],
'brand':[
('s2025101986f01b02ee63c','약석원의 브랜드','자연과 삶을 잇는 치유 웰니스 브랜드','브랜드 철학','white'),
('s20251019a146d1c24e08a','이름과 상징에 담긴 뜻','약석원의 브랜드 아이덴티티','로고 이야기','soft'),
('s20251019493148d80680d','브랜드 자료','약석원 로고와 가이드라인','자료 받기','white')]
}
HERO={'home':'s202509079207ed6c50305','experience':'s202508288408bd2e272a9','food':'s20250831c3dc1b0969b90'}

def clean(e):return re.sub(r'\s+',' ',e.get_text(' ',strip=True)).strip()
def add(e,*classes):e['class']=list(dict.fromkeys(e.get('class',[])+list(classes)))
def tag(doc,name,text=None,**attrs):
 e=doc.new_tag(name,attrs=attrs)
 if text is not None:e.string=text
 return e
def replace_inside(section,markup):
 inside=section.select_one('main .inside')
 if inside:inside.clear();inside.append(BeautifulSoup(markup,'html.parser'))

def visit_markup(map_image=None):
 image='<figure class="ys-visit-map"><img src="'+map_image+'" alt="강화도 약석원 위치 안내 지도" loading="lazy"></figure>'if map_image else''
 return '<div class="ys-visit-layout">'+image+'''<div class="ys-visit-details"><div class="ys-section-intro"><p class="ys-kicker">방문 안내</p><h2 class="ys-section-title">약석원에 오시는 길</h2><p class="ys-body">인천광역시 강화군 양도면 중앙로787번길 56-53</p></div><div class="ys-visit-actions"><a class="ys-button" href="https://naver.me/G1wSjzbe" target="_blank" rel="noopener">네이버 지도에서 보기 ↗</a><a class="ys-button ys-button-outline" href="https://kko.kakao.com/GQpNRu2V-J" target="_blank" rel="noopener">카카오맵에서 보기 ↗</a></div><div class="ys-fact-grid"><section><h3>이용 시간</h3><dl><div><dt>평일</dt><dd>09:00–21:00</dd></div><div><dt>토요일</dt><dd>08:00–20:00</dd></div></dl></section><section><h3>문의 전화</h3><a href="tel:0329375338">032-937-5338</a><a href="tel:01020355455">010-2035-5455</a></section><section class="ys-fact-wide"><h3>찾아오시는 방법</h3><p>강화군 농업기술센터와 인산저수지 인근입니다. GS 강화베리점 맞은편 명태어장 강화점을 지나 우측 길로 들어오신 후, 약석원 이정표를 따라오세요.</p></section><section class="ys-fact-wide"><h3>편의 안내</h3><p>예약 · 주차 · 무선인터넷 · 남녀 화장실 구분</p></section></div></div></div>'''

def explore(doc):
 section=doc.find(id='s2025082735e169b78daa4')
 if not section:return
 photos=[i.get('src')for i in section.select('img.org_image')]
 texts=[clean(w)for w in section.select('[data-widget-type=text]')]
 if len(photos)!=3 or len(texts)!=5:raise ValueError('Home experience source changed')
 cards=[]
 for image,title,description,url in zip(photos,['강화 약쑥 좌훈','약식동원 건강식','차와 쉼'],texts[2:],['/Yakssuk/','/food/','/index2/']):
  cards.append('<article class="ys-explore-card"><a href="'+url+'"><img src="'+image+'" alt="" loading="lazy"><div><h3>'+title+'</h3><p>'+html.escape(description)+'</p><span class="ys-text-link">자세히 알아보기 →</span></div></a></article>')
 replace_inside(section,'<div class="ys-section-intro"><p class="ys-kicker">세 가지 경험</p><h2 class="ys-section-title">몸을 돌보고, 일상을 채우는 시간</h2><p class="ys-body">몸과 마음을 돌보는 약석원의 체험과 먹거리를 만나보세요.</p></div><div class="ys-explore-grid">'+''.join(cards)+'</div>')

def tea_page(body):
 doc=BeautifulSoup(body,'html.parser');head=doc.select_one('header');foot=doc.select_one('footer')
 return str(head)+'''<main id="ys-main" class="ys-tea-page"><section class="ys-tea-hero"><img src="/assets/e868746e1cf9608f99.png" alt="따뜻한 차를 찻잔에 따르는 모습"><div><p class="ys-kicker">약석원의 세 가지 경험</p><h1>차 한 잔과 함께,<br>고요하게 쉬어가는 시간</h1><p>우리 땅의 약재와 전통을 담은 차는 몸을 맑히고 마음을 고요히 하며, 쉼과 명상을 선사하는 치유의 시간입니다.</p></div></section><section class="ys-tea-content"><p class="ys-kicker">차와 쉼</p><h2>좌훈의 온기와 함께 즐기는 차</h2><p>약석원의 좌훈 체험에서는 따뜻한 약쑥차도 함께 즐길 수 있습니다. 몸을 돌보는 시간에 차 한 잔의 여유를 더해보세요.</p><div class="ys-visit-actions"><a class="ys-button" href="/Yakssuk/">좌훈 체험 알아보기 →</a><a class="ys-button ys-button-outline" href="tel:0329375338">체험 문의 032-937-5338</a></div></section></main>'''+str(foot)

def enhance(key,body):
 if key=='tea':body=tea_page(body)
 doc=BeautifulSoup(body,'html.parser')
 for control in doc.select('.board_view .dropdown-toggle,.board_view .comment_num'):control.decompose()
 for image in doc.select('.section_bg img.fixed_bg'):image['alt']=''
 for anchor in doc.select('header a:has(img)'):
  anchor['aria-label']='약석원 홈'
  for image in anchor.select('img'):image['alt']=''
 if key=='food':
  hero=doc.find(id=HERO['food']);heading=hero.select_one('h1,h2,h3,h4,h5,h6')
  paragraphs=[clean(p)for w in hero.select('[data-widget-type=text]')if not w.select_one('h1,h2,h3,h4,h5,h6')for p in w.select('p')if clean(p)]
  title=clean(heading)
  replace_inside(hero,'<div class="ys-food-hero-copy"><h1 class="ys-hero-title">'+html.escape(title)+'</h1>'+''.join('<p>'+html.escape(p)+'</p>'for p in paragraphs)+'</div>')
 if key=='home':explore(doc)
 if key in ['home','directions']:
  section=doc.find(id='s202508292f3f057464dfa'if key=='home'else's20250620a7868d20b55ff')
  if section:
   image=section.select_one('img.org_image')if key=='directions'else None
   replace_inside(section,visit_markup(image.get('src')if image else None));add(section,'ys-content-section','ys-surface-white','ys-visit-section')
 # Semantic sections and one consistent heading hierarchy, without paragraph-by-paragraph boxes.
 mapped={row[0]:row for row in SECTIONS.get(key,[])}
 for section in doc.select('[doz_type=section]'):
  if section.find_parent(['header','footer']):continue
  is_hero=section.get('id')==HERO.get(key)
  if is_hero:
   add(section,'ys-page-hero');heading=next((h for h in section.select('h1,h2,h3,h4,h5,h6')if clean(h)),None)
   if heading:heading.name='h1';add(heading,'ys-hero-title')
   # The second headline is supporting copy, not another title.
   for h in section.select('h2,h3,h4,h5,h6'):h.name='p';add(h,'ys-hero-description')
   continue
  if section.get('id')in mapped:
   _,kicker,title,short,surface=mapped[section['id']];add(section,'ys-content-section','ys-surface-'+surface)
   section['data-section-label']=short
   if section.select_one('.ys-section-title'):continue
   if section.select_one('.ys-food-ingredients'):
    intro=section.select_one('.ys-ingredients-intro');intro.insert(0,tag(doc,'p',kicker,**{'class':'ys-kicker'}));add(intro.select_one('h2'),'ys-section-title');continue
   if section.select_one('.ys-video'):
    inside=section.select_one('main .inside');intro=tag(doc,'div',**{'class':'ys-section-intro ys-video-intro'});intro.append(tag(doc,'p',kicker,**{'class':'ys-kicker'}));intro.append(tag(doc,'h2',title,**{'class':'ys-section-title'}));inside.insert(0,intro);continue
   heading=next((h for h in section.select('h1,h2,h3,h4,h5,h6')if clean(h)and'★★★★★'not in clean(h)and not h.find_parent(class_='gallery2')),None)
   if heading:
    heading.name='h2';heading.clear();heading.string=title;heading.attrs.pop('style',None);add(heading,'ys-section-title');heading.insert_before(tag(doc,'p',kicker,**{'class':'ys-kicker'}));add(heading.parent,'ys-title-block')
   else:
    inside=section.select_one('main .inside')
    if inside:
     intro=tag(doc,'div',**{'class':'ys-section-intro'});intro.append(tag(doc,'p',kicker,**{'class':'ys-kicker'}));intro.append(tag(doc,'h2',title,**{'class':'ys-section-title'}));inside.insert(0,intro)
  elif section.get_text(strip=True)or section.select_one('.gallery2,img,.board_view'):
   if not section.select_one('.board_view'):add(section,'ys-content-section','ys-surface-white')
  else: add(section,'ys-empty-section')
  for heading in section.select('h1,h2,h3,h4,h5,h6'):
   if not clean(heading):heading.decompose();continue
   if 'ys-section-title'in heading.get('class',[]):continue
   if clean(heading)=='★★★★★':heading.name='p';add(heading,'ys-review-rating');continue
   if heading.find_parent(class_='gallery2'):continue
   if heading.find_parent(class_='board_view'):continue
   heading.name='h3';add(heading,'ys-item-title')
 # Use natural wrapping in long prose. Preserve links and emphasis.
 for p in doc.select('[data-widget-type=text] p'):
  if p.find_parent(['header','footer'])or p.find_parent(class_='ys-page-hero'):continue
  if len(clean(p))>=32:
   add(p,'ys-body')
   for br in p.select('br'):br.replace_with(' ')
   if len(clean(p))>=24:
    for emphasis in list(p.select('strong,b')):
     if clean(emphasis)==clean(p):emphasis.unwrap()
 for p in doc.select('.ys-ingredient-description p,.ys-ingredients-intro>p:not(.ys-kicker)'):add(p,'ys-body')
 # Correct reservation links which accidentally landed in reviews.
 for a in doc.select('a[href]'):
  if '예약' in clean(a):a['href']=a['href'].replace('#REVIEW','')
  if a.get('target')=='_blank':a['rel']='noopener noreferrer'
  if a.get('href','').endswith('yakseokwon-logo-png.zip'):a.clear();a.string='PNG 로고 모음 다운로드 (ZIP)';a['download']=''
  if '/downloads/'in a.get('href',''):a['download']=''
 for field in doc.select('input[name=keyword]'):
  field['aria-label']='게시글 검색';field['placeholder']='제목이나 내용으로 검색'
  form=field.find_parent('form');board=form.find_parent(class_='board')
  if board:
   form.extract();add(form,'ys-search-form');toolbar=tag(doc,'div',**{'class':'ys-search-toolbar'});toolbar.append(tag(doc,'label','게시글 검색',**{'for':field.get('id','ys-search-keyword')}));field['id']='ys-search-keyword';toolbar.append(form)
   submit=form.select_one('.ico-search')
   if submit:submit.replace_with(tag(doc,'button','검색',type='submit',**{'class':'ys-search-submit'}))
   container=board.select_one('[id^=post_card_]')
   if container:container.insert_before(toolbar)
   for footer in board.select('.li_footer'):footer.decompose()
 for button in doc.select('form .ico-search'):button['role']='button';button['tabindex']='0';button['aria-label']='검색'
 for h in doc.select('h1,h2,h3,h4,h5,h6'):
  if '본딴'in clean(h):
   for text in list(h.find_all(string=True)):text.replace_with(str(text).replace('본딴','본뜬'))
 for image in doc.select('img[src]'):
  size=DIMENSIONS.get(image['src'])
  if size:image['width']=str(size[0]);image['height']=str(size[1])
 # The source duplicated desktop/sticky navigation IDs. No runtime relies on those IDs.
 ids={}
 for e in doc.select('[id]'):
  value=e['id'];ids[value]=ids.get(value,0)+1
  if ids[value]>1:e['id']=value+'--'+str(ids[value])
 # News previews are a single accessible link per card, including dynamically searched cards.
 for card in doc.select('.ma-item'):
  link=card.select_one('[data-href]')
  if not link:continue
  url=link['data-href'];title=card.select_one('.ysw-title')
  for a in card.select('a'):a.unwrap()
  for e in card.select('[data-href]'):
   for attr in ['data-href','role','tabindex']:e.attrs.pop(attr,None)
  anchor=tag(doc,'a',href=url,**{'class':'ys-news-link','aria-label':clean(title)if title else'기사 읽기'})
  frame=card.select_one('.card');children=list(frame.contents);frame.clear()
  for child in children:anchor.append(child)
  frame.append(anchor)
  if title:title.name='h2'
 # Name primary pages and provide a useful title even for old directly linked pages.
 if key in PAGES and key not in HERO and key not in ['terms','privacy','tea']:
  main_section=next((s for s in doc.select('[doz_type=section]')if not s.find_parent(['header','footer'])and s.get_text(strip=True)),None)
  if main_section:
   h=main_section.select_one('.ys-section-title')or main_section.select_one('h1,h2,h3,h4,h5,h6')
   if h and key in ['newsroom','newsroom-page-2','newsroom-page-3','resources']:h.name='h1';add(h,'ys-page-title')
   elif h and key=='brand':h.name='h1';add(h,'ys-page-title')
   elif key=='directions':h=main_section.select_one('.ys-section-title');h.name='h1';add(h,'ys-page-title')
   else:
    inside=main_section.select_one('main .inside')
    if inside:inside.insert(0,tag(doc,'h1',PAGES[key],**{'class':'ys-page-title ys-legacy-title'}))
 # Skip link uses the first content section; nested legacy main tags remain for CSS compatibility.
 first=next((s for s in doc.select('[doz_type=section]')if not s.find_parent(['header','footer'])),None)or doc.select_one('main')
 if first:first['tabindex']='-1';first['data-main-content']=''
 if first:
  skip=tag(doc,'a','본문으로 바로가기',href='#'+(first.get('id')or'ys-main'),**{'class':'ys-skip-link'});doc.insert(0,skip)
 # A compact contents bar gives the three long pages a clear reading path.
 if key in HERO:
  nav=tag(doc,'nav',**{'class':'ys-page-nav','aria-label':'이 페이지에서'})
  nav.append(tag(doc,'span','이 페이지에서',**{'class':'ys-nav-label'}))
  for sid,kicker,title,short,surface in SECTIONS[key]:
   if key!='home'and's20261105'in sid:continue
   nav.append(tag(doc,'a',short,href='#'+sid))
  after=doc.find(id=SECTIONS[key][0][0])if key!='home'else doc.find(id=HERO[key])
  if after:after.insert_after(nav)
 return str(doc)

def page_title(key,p):
 if key=='home':return '약석원 | 자연과 사람을 잇는 치유의 길'
 if key in ['newsroom-page-2','newsroom-page-3']:return '뉴스룸 '+key[-1]+'페이지 | 약석원'
 if key in PAGES:return PAGES[key]+' | 약석원'
 return p['title'].split(' : 약석원')[0]+' | 약석원'
