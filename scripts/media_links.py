"""Native YouTube links and language-independent illustrated cooking instructions."""
import html,json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
VIDEOS=json.loads((ROOT/'content/video-links.json').read_text())['videos']

def rice_instructions(content):
 doc=BeautifulSoup(content,'html.parser')
 for image in list(doc.select('img[src]')):
  if not image['src'].endswith('/56e18e40fd2d498f5a.png'):continue
  widget=image.find_parent(attrs={'doz_type':'widget'})or image.parent
  steps=[('쌀과 물 준비하기',''),('건강미 한 포 넣기','1인분 기준 1포를 사용하세요.'),('평소처럼 밥 짓기',''),('따뜻한 밥 즐기기','')]
  items=[]
  for i,(title,description)in enumerate(steps,1):
   items.append('<li class="ys-rice-step ys-rice-step--'+str(i)+'"><span class="ys-rice-step-art" aria-hidden="true"><img src="/assets/56e18e40fd2d498f5a.png" alt="" loading="lazy" decoding="async" width="1920" height="3040"></span><div class="ys-rice-step-copy"><span class="ys-rice-step-number" aria-hidden="true">0'+str(i)+'</span><h3>'+html.escape(title)+'</h3>'+('<p>'+html.escape(description)+'</p>'if description else'')+'</div></li>')
  markup='<ol class="ys-rice-instructions" aria-label="건강미 사용법">'+''.join(items)+'</ol>'
  widget.replace_with(BeautifulSoup(markup,'html.parser'))
 return str(doc)

def localize_videos(doc,locale,base):
 for link in doc.select('a[data-video-id]'):
  item=VIDEOS.get(link['data-video-id'],{})
  link['href']=item.get('youtube_by_locale',{}).get(locale,link['href'])
  thumbnail=item.get('thumbnails',{}).get(locale)
  if thumbnail:
   image=link.select_one('img');image['src']=base+thumbnail;image['width']='1280';image['height']='720';image.attrs.pop('srcset',None)
