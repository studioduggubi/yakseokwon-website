/* Static page translations load before this small controller. */
(()=>{
 const locale=document.documentElement.dataset.locale||'ko';
 const controls=[...document.querySelectorAll('.ys-language')];
 controls.forEach(control=>{
  control.querySelectorAll('a[data-language]').forEach(link=>link.addEventListener('click',()=>{
   const url=new URL(link.href);url.hash=location.hash;link.href=url.href;
   try{localStorage.setItem('yakseokwon-language',link.dataset.language);}catch(error){}
  }));
 });
 document.addEventListener('click',event=>controls.forEach(control=>{if(!control.contains(event.target))control.open=false;}));
 document.addEventListener('keydown',event=>{if(event.key==='Escape')controls.forEach(control=>{if(control.open){control.open=false;control.querySelector('summary').focus();}});});
 if(locale==='ko')return;
 const strings=window.ysLocale?.strings||{};
 const normalize=value=>String(value).replace(/\s+/g,' ').trim();
 const translate=value=>{
  const key=normalize(value);
  if(Object.prototype.hasOwnProperty.call(strings,key))return strings[key];
  const found=key.match(/^검색 결과 (\d+)건$/);
  if(found)return locale==='en'?`${found[1]} search result${found[1]==='1'?'':'s'}`:locale==='ja'?`検索結果 ${found[1]}件`:`搜尋結果 ${found[1]}筆`;
  return value;
 };
 const visit=node=>{
  if(node.nodeType===Node.TEXT_NODE){
   if(node.parentElement?.closest('script,style,svg,.ys-language'))return;
   const original=node.nodeValue,next=translate(original);
   if(next!==original)node.nodeValue=next;
   return;
  }
  if(node.nodeType!==Node.ELEMENT_NODE||node.matches('script,style,svg,.ys-language'))return;
  for(const attr of ['aria-label','title','placeholder','alt']){
   const value=node.getAttribute(attr);if(!value)continue;const next=translate(value);if(next!==value)node.setAttribute(attr,next);
  }
  node.childNodes.forEach(visit);
 };
 // This covers controls created by the video, gallery and review controllers.
 new MutationObserver(records=>{
  for(const record of records){
   if(record.type==='childList')record.addedNodes.forEach(visit);
   else if(record.type==='characterData')visit(record.target);
   else if(record.type==='attributes')visit(record.target);
  }
 }).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['aria-label','title','placeholder','alt']});
})();
