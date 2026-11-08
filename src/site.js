const root=document.documentElement;
const siteBase=root.dataset.siteBase||'';
root.classList.add('ys-independent');
const drawer=document.querySelector('#ys-mobile-nav');
function toggleMenu(open){if(!drawer)return;drawer.hidden=!open;document.body.classList.toggle('ys-menu-open',open);document.querySelectorAll('[data-menu-toggle]').forEach(b=>b.setAttribute('aria-expanded',String(open)));if(open)drawer.querySelector('button')?.focus();else document.querySelector('[data-menu-toggle]')?.focus();}
document.querySelectorAll('[data-menu-toggle]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();toggleMenu(drawer?.hidden??true);}));
document.querySelectorAll('[data-menu-close]').forEach(b=>b.addEventListener('click',()=>toggleMenu(false)));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!drawer?.hidden)toggleMenu(false);if(e.key==='Tab'&&drawer&&!drawer.hidden){const items=[...drawer.querySelectorAll('button,a[href]')],first=items[0],last=items[items.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});
drawer?.addEventListener('click',e=>{if(e.target===drawer)toggleMenu(false)});
document.addEventListener('click',e=>{const el=e.target.closest('[data-href]');if(el&&!e.target.closest('a[href]'))location.assign(el.dataset.href);});
document.addEventListener('keydown',e=>{const el=e.target.closest('[data-href]');if(el&&e.key==='Enter'){e.preventDefault();location.assign(el.dataset.href);}});
document.querySelectorAll('[data-youtube]').forEach(button=>button.addEventListener('click',()=>{const iframe=document.createElement('iframe');iframe.src=`https://www.youtube-nocookie.com/embed/${button.dataset.youtube}?autoplay=1&mute=1&playsinline=1&rel=0`;iframe.title=button.getAttribute('aria-label')||'약석원 소개 영상';iframe.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';button.replaceWith(iframe);}));
document.querySelectorAll('.owl-carousel').forEach(g=>{const track=g.querySelector('.owl-stage'),outer=g.querySelector('.owl-stage-outer');if(!track||!outer)return;g.querySelectorAll('.owl-item.cloned').forEach(e=>e.remove());track.style.transform='none';track.style.width='max-content';track.style.display='flex';g.querySelectorAll('.owl-item').forEach(e=>{e.style.float='none';e.style.flexShrink='0';});g.querySelectorAll('.owl-prev,.owl-next').forEach((b)=>{b.setAttribute('role','button');b.setAttribute('tabindex','0');b.setAttribute('aria-label',b.classList.contains('owl-prev')?'이전 이미지':'다음 이미지');const move=()=>{const back=b.classList.contains('owl-prev'),end=outer.scrollWidth-outer.clientWidth;const left=back?(outer.scrollLeft<2?end:Math.max(0,outer.scrollLeft-outer.clientWidth)):(outer.scrollLeft>end-2?0:Math.min(end,outer.scrollLeft+outer.clientWidth));outer.scrollTo({left,behavior:'smooth'});};b.addEventListener('click',move);b.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();move()}});});});
let boardIndexPromise;
document.querySelectorAll('form').forEach(form=>{const input=form.querySelector('input[name="keyword"]');if(!input)return;const kind=location.pathname.slice(siteBase.length).startsWith('/events')?'events':'newsroom';const container=document.querySelector('[id^="post_card_"]');if(!container)return;const original=container.innerHTML;let generation=0;const search=async()=>{const current=++generation,q=input.value.trim().toLocaleLowerCase();let count=0;container.closest('.widget.board')?.classList.toggle('ys-searching',Boolean(q));if(!q){container.innerHTML=original;}else{boardIndexPromise??=fetch(siteBase+'/data/boards.json').then(r=>{if(!r.ok)throw new Error('search index unavailable');return r.json();}).catch(()=>{boardIndexPromise=null;return {newsroom:[],events:[]};});const index=await boardIndexPromise;if(current!==generation)return;const rows=(index[kind]||[]).filter(x=>x.text.toLocaleLowerCase().includes(q));container.innerHTML=rows.map(x=>x.html).join('');count=rows.length;container.querySelectorAll('img').forEach(img=>img.addEventListener('load',masonryLayout,{once:true}));}let status=form.querySelector('[role="status"]');if(!status){status=document.createElement('p');status.setAttribute('role','status');form.append(status);}status.textContent=q?`검색 결과 ${count}건`:'';masonryLayout();};form.addEventListener('submit',e=>{e.preventDefault();search();});form.querySelector('.ico-search')?.addEventListener('click',e=>{e.preventDefault();search();});form.querySelector('.ico-search')?.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();search();}});input.addEventListener('input',search);});
// Captured desktop gallery widths are preserved; mobile retains the original one-card layout.
const slideSettings={
container_w2025101929b00fb99f7ed:{desktop:1,mobile:1,photo:true,heightRatio:1180/2800},
container_w2025061725f96a32fa9af:{desktop:1,mobile:1,photo:true},
container_w2025082987ea855904493:{desktop:1,mobile:1,photo:true},
container_w20250831361b8541764b1:{desktop:1,mobile:1,photo:true},
container_w2025082915f1675319bb0:{desktop:5,mobile:2,gap:5,ratio:1,review:true},
container_w20250831c7a044df617b7:{desktop:3,mobile:2,gap:5,ratio:1,review:true},
container_w2025083174a89b144d397:{desktop:2,mobile:2,gap:5,ratio:9/16,center:true},
container_w202508310dd6b120da1bc:{desktop:3,mobile:2,gap:2.5,ratio:16/9,center:true}
};
function gallerySize(){document.querySelectorAll('.owl-carousel').forEach(g=>{const outer=g.querySelector('.owl-stage-outer'),track=g.querySelector('.owl-stage');if(!outer||!track)return;const config=slideSettings[g.id];if(!config)return;const mobile=innerWidth<992,cols=mobile?config.mobile:config.desktop;const gap=config.gap?(mobile?config.gap/2:config.gap):0;const edge=config.center?(mobile?40:60):0;if(config.gap)g.style.margin=`0 -${gap}px`;track.style.paddingLeft=edge+'px';track.style.paddingRight=edge+'px';const width=Math.ceil((outer.clientWidth-edge*2)/cols);g.querySelectorAll('.owl-item').forEach(e=>{e.style.width=width+'px';const item=e.querySelector('.item_gallary'),image=e.querySelector('.img_wrap');if(!item||!image)return;if(config.photo){const h=outer.clientWidth*(config.heightRatio||.6);g.style.height=h+'px';outer.style.height=h+'px';track.style.height=h+'px';e.style.height=h+'px';[item,image,e.querySelector('.text_wrap')].filter(Boolean).forEach(x=>x.style.height=h+'px');}else{item.style.padding=gap+'px';const height=Math.ceil(image.clientWidth/config.ratio);image.style.height=height+'px';image.style.minHeight=height+'px';}});});}
gallerySize();addEventListener('resize',gallerySize,{passive:true});document.fonts.ready.then(gallerySize);
function masonryLayout(){document.querySelectorAll('[id^="post_card_"].type_masonry').forEach(container=>{container.classList.add('ys-news-grid');container.style.removeProperty('height');container.style.removeProperty('margin');container.querySelectorAll(':scope>.ma-item').forEach(item=>{for(const prop of ['width','padding','left','top','position'])item.style.removeProperty(prop);});});}
addEventListener('resize',masonryLayout,{passive:true});document.fonts.ready.then(masonryLayout);document.querySelectorAll('[id^="post_card_"].type_masonry img').forEach(i=>i.addEventListener('load',masonryLayout));masonryLayout();
// Match the published gallery ratios and column counts at each breakpoint.
const gridSettings={container_w2025061748308c435b872:{columns:4,mobile:1,grid:true,ratio:1,gap:10,rows:1},container_w20250617007057ebca8e1:{columns:4,mobile:2,grid:true,ratio:4/3,gap:5},container_w202506172c0dbaad909bc:{columns:4,mobile:1,grid:true,ratio:1,gap:10,caption:true},container_w20250828797696ec76d58:{columns:2,ratio:16/9,gap:2},container_w20250829541d8450817b8:{columns:3,ratio:4/3,gap:2.5,rows:2}};
function gridSize(){for(const [id,config]of Object.entries(gridSettings)){const grid=document.getElementById(id);if(!grid)continue;const cols=innerWidth<992?(config.mobile||2):config.columns;const gap=innerWidth<992?config.gap/2:config.gap;if(grid.dataset.layoutColumns!==String(cols)){const items=[...grid.querySelectorAll('.item_gallary:not(._dummy_item)')];items.forEach((x,i)=>x.classList.toggle('_item_hide',!!config.rows&&i>=cols*config.rows));grid.querySelectorAll('._gallery_row').forEach(x=>x.remove());for(let i=0;i<items.length;i+=cols){const row=document.createElement('div');row.className='_gallery_row gallery_row tabled';items.slice(i,i+cols).forEach(x=>row.append(x));grid.append(row);}grid.dataset.layoutColumns=String(cols);}grid.style.margin=`0 -${gap}px`;if(config.grid)grid.querySelectorAll('._gallery_row').forEach(row=>{row.style.display='grid';row.style.width='100%';row.style.gridTemplateColumns=`repeat(${cols},minmax(0,1fr))`;});grid.querySelectorAll('.item_gallary').forEach(item=>{item.style.padding=gap+'px';if(config.grid){item.style.display='block';item.style.width='100%';}const image=item.querySelector('.img_wrap'),text=item.querySelector('.text_wrap');if(!image)return;const height=Math.ceil(image.clientWidth/config.ratio);image.style.minHeight=height+'px';if(text&&!config.caption)text.style.height=height+'px';});}}
gridSize();addEventListener('resize',gridSize,{passive:true});document.fonts.ready.then(gridSize);
// Imweb recomputes original-size image dimensions after each breakpoint change.
// Retain the configured desktop size, fit narrower containers, and keep the aspect ratio.
const originalImages=[...document.querySelectorAll('.widget.image.org_size img.org_image')].map(img=>({img,width:parseFloat(img.style.width)||0,height:parseFloat(img.style.height)||0}));
const cropImages=[...document.querySelectorAll('img[id^="img_w202506"]')].filter(img=>!img.closest('.org_size')&&img.closest('._img_box')?.style.height==='170px');
function imageSize(){for(const {img,width:originalWidth,height:originalHeight}of originalImages){if(!img.naturalWidth||!originalHeight)continue;const box=img.closest('.widget.image'),frame=img.closest('._img_box');const configuredHeights={img_w20251019b65a70a5e6b2b:300,img_w20251019f81baa52e996f:300,img_w2025101955cb4370b9949:300,img_w2025083188e9061346ccd:470};const maxWidth=configuredHeights[img.id]?configuredHeights[img.id]*img.naturalWidth/img.naturalHeight:(originalWidth||originalHeight*img.naturalWidth/img.naturalHeight);const width=Math.min(box.clientWidth,maxWidth);img.style.width=width+'px';img.style.height=Math.round(width*img.naturalHeight/img.naturalWidth)+'px';if(frame)frame.style.height='auto';}
for(const img of cropImages){if(!img.naturalWidth)continue;const frame=img.closest('._img_box'),height=Math.round(frame.clientWidth*170/159.5);frame.style.height=height+'px';img.style.marginLeft=(frame.clientWidth-height*img.naturalWidth/img.naturalHeight)/2+'px';}
const graphic=document.getElementById('img_w202508293867862ba2389');if(graphic?.naturalWidth){const frame=graphic.closest('._img_box');if(frame)frame.style.height=Math.round(frame.clientWidth*graphic.naturalHeight/graphic.naturalWidth)+'px';}}
imageSize();addEventListener('resize',imageSize,{passive:true});document.querySelectorAll('.widget.image img').forEach(i=>i.addEventListener('load',imageSize));
// Restore image enlargement without relying on Imweb's removed runtime.
const lightbox=document.createElement('dialog');lightbox.className='ys-lightbox';lightbox.setAttribute('aria-label','이미지 크게 보기');lightbox.innerHTML='<button type="button" class="ys-lightbox-close" aria-label="닫기">×</button><button type="button" class="ys-lightbox-prev" aria-label="이전 이미지">‹</button><img alt=""><button type="button" class="ys-lightbox-next" aria-label="다음 이미지">›</button>';document.body.append(lightbox);let lightboxImages=[],lightboxIndex=0;
function showLightbox(index){lightboxIndex=(index+lightboxImages.length)%lightboxImages.length;lightbox.querySelector('img').src=lightboxImages[lightboxIndex];lightbox.querySelectorAll('.ys-lightbox-prev,.ys-lightbox-next').forEach(b=>b.hidden=lightboxImages.length<2);if(!lightbox.open)lightbox.showModal();}
lightbox.querySelector('.ys-lightbox-close').addEventListener('click',()=>lightbox.close());lightbox.querySelector('.ys-lightbox-prev').addEventListener('click',()=>showLightbox(lightboxIndex-1));lightbox.querySelector('.ys-lightbox-next').addEventListener('click',()=>showLightbox(lightboxIndex+1));lightbox.addEventListener('click',e=>{if(e.target===lightbox)lightbox.close();});lightbox.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')showLightbox(lightboxIndex-1);if(e.key==='ArrowRight')showLightbox(lightboxIndex+1);});
function localImage(element){const img=element.querySelector('img.org_image');if(img)return img.currentSrc||img.src;const bg=getComputedStyle(element.querySelector('.img_wrap')||element).backgroundImage;return bg.match(/^url\(["']?(.*?)["']?\)$/)?.[1];}
document.querySelectorAll('.gallery2 ._lightbox_item,._img_box._image_widget_lightbox').forEach(target=>{if(target.closest('a[href]'))return;target.setAttribute('role','button');target.setAttribute('tabindex','0');target.setAttribute('aria-label','이미지 크게 보기');const open=()=>{const item=target.closest('.item_gallary')||target,gallery=target.closest('.gallery2');const items=gallery?[...gallery.querySelectorAll('.item_gallary:not(._dummy_item)')]:[item];lightboxImages=items.map(localImage).filter(Boolean);if(!lightboxImages.length)return;showLightbox(Math.max(0,lightboxImages.indexOf(localImage(item))));};target.addEventListener('click',open);target.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}});});

// Readable body copy and clearer controls, approved as the site-wide GUI update.
root.classList.add('ys-readable');
document.querySelectorAll('[doz_type="section"] [data-widget-type="text"] .text-table p,.board_txt_area p').forEach(p=>{
 const article=!!p.closest('.board_txt_area');
 if(p.querySelector('img')||p.textContent.trim().length<(article?8:24))return;
 const sizes=[p,...p.querySelectorAll('span,strong,b,em')].map(e=>parseFloat(getComputedStyle(e).fontSize));
 if(Math.max(...sizes)>15)return;
 p.classList.add('ys-copy');
 if(getComputedStyle(p).textAlign==='center')p.classList.add('ys-copy-centered');
});
document.querySelectorAll('[doz_type="section"] .widget.button a.btn,.board_view .action-area a.btn,.board_view .action-area button').forEach(button=>{
 if(parseFloat(getComputedStyle(button).fontSize)<=16)button.classList.add('ys-action');
});
function readableLayout(){gallerySize();gridSize();imageSize();masonryLayout();}
readableLayout();document.fonts.ready.then(readableLayout);

// A shared visual hierarchy for every page; artwork and original copy stay intact.
root.classList.add('ys-designed');
const pageKey=root.dataset.pageKey||'';
const pageNames={brand:'브랜드',directions:'오시는 길',resources:'행사 일정',newsroom:'뉴스룸','newsroom-page-2':'뉴스룸','newsroom-page-3':'뉴스룸',tea:'차 이야기','legacy-company':'약석원 소개','legacy-experience':'좌훈 이야기','legacy-food':'건강식 이야기','legacy-store':'약석원 안내',terms:'이용약관',privacy:'개인정보처리방침'};
const article=pageKey.startsWith('post-');
const pageName=article?(pageKey.startsWith('post-event')?'행사 일정':'뉴스룸'):pageNames[pageKey];
if(pageName){
 const target=article?document.querySelector('.board_view'):document.querySelector('.ys-policy')||document.querySelector('[doz_type="section"] main .inside');
 if(target){
  const nav=document.createElement('nav');nav.className='ys-breadcrumb';nav.setAttribute('aria-label','현재 위치');
  const home=document.createElement('a');home.href=siteBase+'/';home.textContent='약석원';nav.append(home);
  const sep=document.createElement('span');sep.textContent='›';sep.setAttribute('aria-hidden','true');nav.append(sep);
  const current=document.createElement(article?'a':'span');current.textContent=pageName;
  if(article)current.href=siteBase+(pageKey.startsWith('post-event')?'/events/':'/newsroom/');else current.setAttribute('aria-current','page');
  nav.append(current);target.prepend(nav);
 }
}
// Section titles and surfaces are defined explicitly at build time.
// Keep each process illustration and its two text widgets together in one card.
['img_w202508290a1083c8f3778','img_w20250829d5999780c2966','img_w20250829fd5234282324e','img_w202508298c26dac1c5ec4'].forEach(id=>{
 const img=document.getElementById(id);if(!img)return;
 let col=img.parentElement;
 while(col&&!col.matches('[doz_type="section"]')){
  if(col.classList.contains('col-dz-3')&&col.querySelectorAll('img').length===1&&col.querySelector('[data-widget-type="text"]')){
   const frame=document.createElement('div');frame.className='ys-step-card';while(col.firstChild)frame.append(col.firstChild);col.append(frame);
   col.classList.add('ys-step-column');break;
  }col=col.parentElement;
 }
});
if(document.querySelector('.board_view'))root.classList.add('ys-article-page');
document.querySelectorAll('[id^="post_card_"].type_row>ul.list').forEach(row=>row.classList.add('ys-event-card'));
document.querySelectorAll('.ys-policy').forEach(p=>p.classList.add('ys-paper'));
readableLayout();document.fonts.ready.then(readableLayout);

// Animated images on phones avoid media autoplay restrictions. Desktop uses the lighter MP4.
document.querySelectorAll('[data-hero-motion]').forEach(section=>{
 const video=section.querySelector('video.ys-hero-motion'),button=section.querySelector('.ys-motion-toggle');
 const picture=section.querySelector('.ys-hero-mobile-picture'),image=picture?.querySelector('img'),imageSource=picture?.querySelector('source');
 if(!video)return;
 const mobile=matchMedia('(max-width:991px)'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let userPaused=false,manualPlay=false,inView=true,imageFailed=false,generation=0;
 video.muted=true;video.defaultMuted=true;
 const wantsMotion=()=>inView&&!document.hidden&&!userPaused&&(!reduced.matches||manualPlay);
 const label=playing=>{
  section.dataset.motionState=playing?'playing':'paused';if(!button)return;button.hidden=false;
  button.textContent=playing?'일시정지':'움직임 재생';
  button.setAttribute('aria-label','배경 움직임 '+(playing?'일시정지':'재생'));
  button.setAttribute('aria-pressed',String(userPaused));
 };
 const imageMedia=active=>{if(imageSource){const value=active?'(max-width:991px)':'not all';if(imageSource.media!==value)imageSource.media=value;}};
 const sync=()=>{
  const current=++generation,active=wantsMotion();
  if(mobile.matches&&imageSource){
   section.dataset.motionMode='image';video.pause();
   if(video.hasAttribute('src')){video.removeAttribute('src');video.load();}
   imageMedia(active&&!imageFailed);label(active&&!imageFailed);return;
  }
  section.dataset.motionMode='video';imageMedia(false);
  if(!active){video.pause();label(false);return;}
  video.classList.remove('ys-motion-failed');
  if(!video.hasAttribute('src'))video.src=video.dataset.motionSrc;
  else if(video.error)video.load();
  video.play().then(()=>{if(current===generation)label(!video.paused);}).catch(()=>{if(current===generation)label(false);});
 };
 button?.addEventListener('click',()=>{
  const playing=section.dataset.motionMode==='image'?section.dataset.motionState==='playing':!video.paused;
  userPaused=playing;manualPlay=!playing;if(!playing)imageFailed=false;sync();
 });
 video.addEventListener('playing',()=>{if(section.dataset.motionMode==='video')label(true);});
 video.addEventListener('pause',()=>{if(section.dataset.motionMode==='video')label(false);});
 video.addEventListener('error',()=>{if(section.dataset.motionMode==='video'){video.classList.add('ys-motion-failed');label(false);}});
 image?.addEventListener('error',()=>{imageFailed=true;imageMedia(false);label(false);});
 mobile.addEventListener('change',sync);
 reduced.addEventListener('change',()=>{manualPlay=false;sync();});
 document.addEventListener('visibilitychange',sync);addEventListener('pageshow',sync);
 new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;sync();},{threshold:.02}).observe(section);
 sync();
});

// The contents bar also indicates the section currently being read.
document.querySelectorAll('.ys-page-nav').forEach(nav=>{const links=[...nav.querySelectorAll('a[href^="#"]')],targets=links.map(a=>document.getElementById(a.hash.slice(1))).filter(Boolean);const update=()=>{const current=targets.filter(s=>s.getBoundingClientRect().top<180).pop()||targets[0];links.forEach(a=>{if(a.hash==='#'+current?.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});};addEventListener('scroll',update,{passive:true});update();});
