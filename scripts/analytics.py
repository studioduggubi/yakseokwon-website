"""Add GA4 only to the official-domain build and disclose the traffic counter."""
import hashlib,json,re
from site_config import PROFILE,ORIGIN

COPY={
 'ko':('방문 통계','방문자 수와 페이지 이용 현황을 파악하기 위해 Google Analytics를 사용합니다. 광고 개인 최적화와 Google 신호 수집은 사용하지 않습니다. 통계에 전송하는 페이지 주소에서 검색어와 URL 매개변수를 제외합니다. 브라우저의 추적 거부 설정을 존중하며, 아래에서 이 브라우저의 통계 수집을 중지하거나 다시 허용할 수 있습니다.','방문 통계 수집 중지','방문 통계 수집 허용','브라우저의 추적 거부 설정이 적용되어 있습니다.'),
 'en':('Visitor statistics','We use Google Analytics to understand visitor numbers and page usage. Ad personalization and Google signals are disabled. Search terms and URL parameters are excluded from the page addresses sent for statistics. We respect browser tracking preferences. You can stop or allow statistics collection in this browser below.','Stop visitor statistics','Allow visitor statistics','Your browser’s do-not-track preference is active.'),
 'zh-TW':('瀏覽統計','我們使用 Google Analytics 了解訪客人數與網頁使用情況，並停用廣告個人化及 Google 信號。傳送的網頁網址不包含搜尋字詞或網址參數。我們尊重瀏覽器的拒絕追蹤設定，您也可在下方停止或允許此瀏覽器的統計收集。','停止瀏覽統計','允許瀏覽統計','已套用瀏覽器的拒絕追蹤設定。'),
 'ja':('アクセス統計','訪問者数とページの利用状況を把握するため、Google Analytics を使用します。広告のパーソナライズと Google シグナルは無効です。統計に送信するページ URL から検索語と URL パラメータを除外します。ブラウザの追跡拒否設定を尊重し、以下でこのブラウザの統計収集を停止または許可できます。','アクセス統計を停止','アクセス統計を許可','ブラウザの追跡拒否設定が適用されています。')
}

def analytics_settings(root):
 config=json.loads((root/'content/analytics.json').read_text())
 if not re.fullmatch(r'G-[A-Z0-9]+',config['measurement_id']):raise ValueError('Invalid GA4 measurement ID')
 return config

def apply_analytics(doc,page,code,root,base):
 config=analytics_settings(root)
 if not config['enabled']or PROFILE!='production':return
 if ORIGIN!=config['origin']:raise ValueError('Analytics origin must match the production build')
 digest=hashlib.sha256((root/'src/analytics.js').read_bytes()).hexdigest()[:16]
 doc.head.append(doc.new_tag('script',src=base+'/analytics.js?v='+digest,attrs={'defer':'','data-measurement-id':config['measurement_id'],'data-origin':config['origin']}))
 if page['key']!='privacy':return
 policy=doc.select_one('.ys-policy-copy')
 if policy is None:raise ValueError('Privacy policy content not found')
 title,copy,stop,allow,blocked=COPY[code]
 section=doc.new_tag('section',attrs={'class':'ys-analytics-notice'})
 heading=doc.new_tag('h2');heading.string=title;section.append(heading)
 paragraph=doc.new_tag('p');paragraph.string=copy;section.append(paragraph)
 button=doc.new_tag('button',type='button',attrs={'class':'ys-button ys-button-outline','data-analytics-choice':'','data-stop-label':stop,'data-allow-label':allow,'data-blocked-label':blocked,'aria-pressed':'false'})
 button.string=stop;section.append(button)
 status=doc.new_tag('p',attrs={'data-analytics-status':'','role':'status'});section.append(status)
 policy.append(section)
