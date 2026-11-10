/* Exercise tracking boundaries without contacting Google or a real browser. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('src/analytics.js', 'utf8');
function run(overrides = {}) {
  const requests = [], stored = new Map(), handlers = {}, attributes = {};
  const button = {dataset: {allowLabel:'Allow',stopLabel:'Stop',blockedLabel:'Blocked'},setAttribute:(k,v)=>attributes[k]=v,addEventListener:(k,v)=>handlers[k]=v};
  const status = {};
  const context = {
    document: {currentScript:{dataset:{measurementId:'G-SL8TJDFEEP',origin:'https://yakseokwon.com'}},documentElement:{dataset:{siteProfile:'production'}},head:{appendChild:e=>requests.push(e.src)},createElement:()=>({}),querySelector:s=>s==='[data-analytics-choice]'?button:status,referrer:'https://search.example/find?q=private',cookie:''},
    location:{origin:'https://yakseokwon.com',pathname:'/food/',search:'?name=private',hash:'#private',reload:()=>{context.reloaded=true;}},
    navigator:{},localStorage:{getItem:k=>stored.get(k),setItem:(k,v)=>stored.set(k,v)},URL,Date
  };
  context.window = context;
  if (overrides.origin) context.location.origin=overrides.origin;
  if (overrides.profile) context.document.documentElement.dataset.siteProfile=overrides.profile;
  if (overrides.dnt) context.navigator.doNotTrack='1';
  if (overrides.gpc) context.navigator.globalPrivacyControl=true;
  if (overrides.saved) stored.set('ys-analytics-disabled','1');
  if (overrides.externalDisable) context['ga-disable-G-SL8TJDFEEP']=true;
  if (overrides.storageFailure) context.localStorage.getItem=()=>{throw Error('blocked');};
  vm.runInNewContext(source,context);
  return {context,requests,stored,handlers,button,status,attributes};
}
let cases=0;
for (const origin of ['https://studioduggubi.github.io','http://localhost:8000','https://www.yakseokwon.com','http://yakseokwon.com']) {assert.equal(run({origin}).requests.length,0);cases++;}
assert.equal(run({profile:'preview'}).requests.length,0);cases++;
for (const option of ['dnt','gpc','saved','externalDisable']) {const result=run({[option]:true});assert.equal(result.requests.length,0);assert.equal(result.context['ga-disable-G-SL8TJDFEEP'],true);cases++;}
const result=run();
assert.equal(result.requests.length,1);
assert.equal(result.requests[0],'https://www.googletagmanager.com/gtag/js?id=G-SL8TJDFEEP');
const config=Array.from(result.context.dataLayer[1]);
assert.equal(config[0],'config');assert.equal(config[1],'G-SL8TJDFEEP');
assert.equal(config[2].page_location,'https://yakseokwon.com/food/');
assert.equal(config[2].page_referrer,'https://search.example/');
assert.equal(config[2].allow_google_signals,false);assert.equal(config[2].allow_ad_personalization_signals,false);cases++;
result.handlers.click();assert.equal(result.context['ga-disable-G-SL8TJDFEEP'],true);assert.equal(result.stored.get('ys-analytics-disabled'),'1');assert.equal(result.button.textContent,'Allow');
result.handlers.click();assert.equal(result.context['ga-disable-G-SL8TJDFEEP'],false);assert.equal(result.context.reloaded,true);assert.equal(result.requests.length,1);cases++;
const stopped=run({saved:true});stopped.handlers.click();assert.equal(stopped.requests.length,1);assert.equal(stopped.button.textContent,'Stop');cases++;
const blocked=run({gpc:true});blocked.handlers.click();assert.equal(blocked.button.disabled,true);assert.equal(blocked.status.textContent,'Blocked');assert.equal(blocked.requests.length,0);cases++;
assert.equal(run({storageFailure:true}).requests.length,1);cases++;
console.log(JSON.stringify({cases,errors:[],networkRequestsSent:0}));
