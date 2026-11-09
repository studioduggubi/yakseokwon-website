"""Editable HTML/CSS sharing-card originals; browser renders use original brand SVGs."""
from pathlib import Path
import json,html,re
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports/metadata-20261108';R.mkdir(parents=True,exist_ok=True);P=ROOT/'public';(P/'icons').mkdir(exist_ok=True);(P/'social').mkdir(exist_ok=True)
data=json.loads((ROOT/'content/metadata.json').read_text())
source=(P/'brand/logo-primary-white.svg').read_text();inside=source[source.index('>')+1:source.rfind('</svg>')]
favicon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="#3e653e"/><g transform="translate(118.08 36) scale(.79521)">'+inside+'</g></svg>'
(P/'icons/favicon.svg').write_text(favicon)
(R/'icon.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>약석원 아이콘 원본</title><style>html,body{margin:0;width:512px;height:512px}img{display:block;width:512px;height:512px}</style></head><body><img src="../../public/icons/favicon.svg" alt="약석원 파비콘"></body></html>')
photos={'experience':'media/experience-hero-poster.webp','food':'assets/b49aebad50555e597b.png','tea':'assets/e868746e1cf9608f99.png','directions':'assets/5d842fdb8c02f1d609.png'}
footers={'ko':'강화에서, 일상으로','en':'From Ganghwa, with care.','zh-TW':'從江華島，走進日常','ja':'江華島から、日々の暮らしへ'}
styles='''@font-face{font-family:Maru;src:url(../../public/brand/MaruBuri-Bold.woff2);font-weight:700}*{box-sizing:border-box}html,body{margin:0;width:1200px;background:#f6f5ef;color:#293b2b}body{font-family:"Apple SD Gothic Neo","Hiragino Kaku Gothic ProN","PingFang TC",sans-serif}.card{width:1200px;height:630px;position:relative;overflow:hidden;background:#f6f5ef}.identity{position:absolute;left:66px;top:52px;display:flex;align-items:center;gap:22px}.identity img{width:50px;height:80px;object-fit:contain}.name{font-size:25px;letter-spacing:.08em;font-weight:600}.place{font-size:15px;letter-spacing:.15em;color:#78816e;margin-top:8px}.copy{position:absolute;left:66px;top:222px;width:570px}.label{font-size:21px;color:#62705b;margin-bottom:22px;font-weight:500}.headline{font-size:54px;line-height:1.3;letter-spacing:-.035em;margin:0;font-weight:700;white-space:pre-line}.card[lang=ko] .headline{font-family:Maru,serif;font-size:55px}.card[lang=ja] .headline{font-size:49px}.card[lang=zh-TW] .headline{font-size:55px}.foot{position:absolute;left:66px;bottom:59px;font-size:20px;color:#69745f}.visual{position:absolute;left:684px;right:0;top:0;bottom:0;background:#3e653e;overflow:hidden}.visual.photo img{height:100%;width:100%;object-fit:cover}.visual.photo.experience img{object-position:35% center}.visual.photo.food img{object-position:48% center}.visual.logo{display:flex;align-items:center;justify-content:center}.visual.logo>img{width:217px;height:346px;object-fit:contain}.seal{position:absolute;bottom:46px;left:0;right:0;text-align:center;color:#d9e1ce;font-size:15px;letter-spacing:.19em}.visual.logo{background:#3e653e url(../../public/assets/c3b585a452fc9196c4.png) center/cover no-repeat}.visual.type .word{position:absolute;left:53px;top:158px;color:#f6f5ef;font-family:Georgia,serif;font-size:78px;line-height:1.03}.visual.type .sub{position:absolute;left:56px;bottom:104px;color:#cedbc4;font-size:18px;letter-spacing:.13em}.visual.type:after{content:"";position:absolute;left:56px;right:56px;bottom:74px;height:1px;background:#7f9971}'''
styles+='''.card.logo-map{display:flex;align-items:center;justify-content:center;background:#3e653e url(../../public/assets/c3b585a452fc9196c4.png) center/cover no-repeat}.logo-map>img{display:block;width:248px;height:396px;object-fit:contain}'''
cards=[];manifest=[]
for section in ['home','experience','food','tea','brand','directions','resources','newsroom']:
 for code,copy in data['pages'][section].items():
  lang='zh-TW'if code=='zh-TW'else code
  if section in photos:visual='<div class="visual photo '+section+'"><img src="../../public/'+photos[section]+'" alt=""></div>'
  elif section in ['home','brand']:visual='<div class="visual logo"><img src="../../public/brand/logo-primary-white.svg" alt=""><div class="seal">NATURE · PEOPLE · EVERYDAY</div></div>'
  else:
   word='Meet<br>Yakseokwon.'if section=='resources'else'Our<br>stories.'
   visual='<div class="visual type"><div class="word">'+word+'</div><div class="sub">YAKSEOKWON</div></div>'
  if section=='food':
   cards.append('<article class="card logo-map" lang="'+lang+'" data-key="'+section+'-'+code+'"><img src="../../public/brand/logo-primary-white.svg" alt="'+html.escape(data['names'][code])+'"></article>')
  else:
   cards.append('<article class="card" lang="'+lang+'" data-key="'+section+'-'+code+'"><div class="identity"><img src="../../public/brand/logo-primary-green.svg" alt=""><div><div class="name">'+html.escape(data['names'][code])+'</div><div class="place">GANGHWA, KOREA</div></div></div><div class="copy"><div class="label">'+html.escape(copy['label'])+'</div><h1 class="headline">'+html.escape(copy['headline'])+'</h1></div><div class="foot">'+footers[code]+'</div>'+visual+'</article>')
  manifest.append({'section':section,'locale':code,'key':section+'-'+code,'x':0,'y':len(manifest)*630,'width':1200,'height':630})
(R/'cards.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>약석원 공유 카드 원본 · 4개 언어</title><style>'+styles+'</style></head><body>'+''.join(cards)+'</body></html>')
(R/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared',len(manifest),'native HTML/CSS cards and original-logo favicon')
