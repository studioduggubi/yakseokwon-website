"""Static, locale-aware sharing and browser metadata. Search remains excluded."""
import json,re
ORIGIN='https://studioduggubi.github.io'
OG_LOCALES={'ko':'ko_KR','en':'en_US','zh-TW':'zh_TW','ja':'ja_JP'}
ALIASES={'legacy-company':'home','legacy-experience':'experience','legacy-food':'food','legacy-store':'food','newsroom-page-2':'newsroom','newsroom-page-3':'newsroom','terms':'home','privacy':'home'}

def section_for(key):
 if key.startswith('post-event-'):return 'resources'
 if key.startswith('post-news-'):return 'newsroom'
 return ALIASES.get(key,key)

def apply_metadata(doc,page,locale,locales,root,base,route):
 config=json.loads((root/'content/metadata.json').read_text());code=locale['code'];section=section_for(page['key']);copy=config['pages'].get(page['key'],config['pages'][section])[code]
 title=doc.title.get_text(' ',strip=True)
 if page['key']=='home':title=config['home_titles'][code]
 if page['key'].startswith('newsroom-page-'):title+=' · '+page['key'].rsplit('-',1)[1]
 doc.title.string=title
 description=copy['description']
 if page['key'].startswith('post-'):
  body=doc.select_one('.board_txt_area')
  excerpt=re.sub(r'\s+',' ',body.get_text(' ',strip=True)).strip()if body else''
  if excerpt:
   description=excerpt
   if len(description)>180:
    description=description[:177].rstrip()
    if code=='en':description=description.rsplit(' ',1)[0]
    description=description.rstrip(' ,;:')+'…'
  else:description=title.split(' | ')[0]+'. '+description
 head=doc.head
 for e in list(head.select('meta[name=description],meta[property^="og:"],meta[name^="twitter:"],link[rel=canonical],link[hreflang],meta[name=theme-color],link[rel=icon],link[rel=apple-touch-icon],link[rel=manifest],script[type="application/ld+json"]')):e.decompose()
 def meta(value,**attrs):head.append(doc.new_tag('meta',content=str(value),attrs=attrs))
 def link(href,**attrs):head.append(doc.new_tag('link',href=href,attrs=attrs))
 canonical=ORIGIN+base+locale['prefix']+route
 image_file=json.loads((root/'content/social-images.json').read_text())[section][code]
 image=ORIGIN+base+image_file
 meta(description,name='description');link(canonical,rel='canonical')
 for other in locales:link(ORIGIN+base+other['prefix']+route,rel='alternate',hreflang=other['html_lang'])
 link(ORIGIN+base+route,rel='alternate',hreflang='x-default')
 values={'title':title,'description':description,'type':'article'if page['key'].startswith('post-')else'website','url':canonical,'site_name':config['names'][code],'locale':OG_LOCALES[code],'image':image,'image:secure_url':image,'image:type':'image/jpeg','image:width':'1200','image:height':'630','image:alt':copy['label']+' — '+config['names'][code]}
 for key,value in values.items():meta(value,property='og:'+key)
 for other in locales:
  if other['code']!=code:meta(OG_LOCALES[other['code']],property='og:locale:alternate')
 for key,value in {'card':'summary_large_image','title':title,'description':description,'image':image,'image:alt':values['image:alt']}.items():meta(value,name='twitter:'+key)
 meta('#3e653e',name='theme-color');meta(config['names'][code],name='application-name');meta(config['names'][code],name='apple-mobile-web-app-title')
 for path,attrs in [('/icons/favicon.ico',{'rel':'icon','sizes':'16x16 32x32 48x48'}),('/icons/favicon.svg',{'rel':'icon','type':'image/svg+xml','sizes':'any'}),('/icons/favicon-96.png',{'rel':'icon','type':'image/png','sizes':'96x96'}),('/icons/apple-touch-icon.png',{'rel':'apple-touch-icon','sizes':'180x180'}),('/site.webmanifest',{'rel':'manifest'})]:link(base+path,**attrs)
 site_url=ORIGIN+base+locale['prefix']+'/'
 org_id=ORIGIN+base+'/#organization'
 graph=[{'@type':'Organization','@id':org_id,'name':'약석원','alternateName':['Yakseokwon','藥石院','ヤクソグォン'],'url':ORIGIN+base+'/','logo':{'@type':'ImageObject','url':ORIGIN+base+'/icons/icon-512.png','width':512,'height':512}}, {'@type':'WebSite','@id':site_url+'#website','url':site_url,'name':config['names'][code],'inLanguage':locale['html_lang'],'publisher':{'@id':org_id}}, {'@type':'WebPage','@id':canonical+'#webpage','url':canonical,'name':title,'description':description,'inLanguage':locale['html_lang'],'isPartOf':{'@id':site_url+'#website'},'primaryImageOfPage':{'@type':'ImageObject','url':image,'width':1200,'height':630}}]
 script=doc.new_tag('script',type='application/ld+json');script.string=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c');head.append(script)
 doc.html['prefix']='og: https://ogp.me/ns#'
