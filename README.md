# 약석원 독립 웹사이트

약석원 원본 로고·서체·사진·민화·패키지와 승인된 GUI를 유지한 독립 정적 사이트입니다. 한국어·영어·중국어 번체·일본어로 55개 경로, 총 220개 HTML을 생성합니다. 현재 공개된 GitHub Pages 미리보기와 정식 도메인용 빌드를 구분합니다.

## 빌드 환경과 주소

`content/site.json`이 모든 페이지·이미지·언어 링크·공유 메타데이터의 주소 기준입니다.

| 프로필 | 기준 주소 | 경로 접두사 | 용도 |
| --- | --- | --- | --- |
| `preview` | `https://studioduggubi.github.io` | `/yakseokwon-website` | 현재 공개 미리보기, 기본값 |
| `production` | `https://yakseokwon.com` | 없음 | 정식 도메인 연결을 위한 준비본 |

Python 3.11 이상에서 `python -m pip install -r requirements.txt`로 의존성을 설치합니다. 가상환경과 패키지 캐시는 각 컴퓨터에 둡니다.

```sh
# 현재 GitHub 미리보기용: dist/
SITE_PROFILE=preview python scripts/build.py
SITE_PROFILE=preview python scripts/verify.py

# 정식 주소용: dist-production/
SITE_PROFILE=production SITE_OUTPUT_DIR=dist-production python scripts/build.py
SITE_PROFILE=production SITE_OUTPUT_DIR=dist-production python scripts/verify.py

# 정식 주소용 결과물을 로컬 루트에서 검토
python -m http.server 4333 --bind 127.0.0.1 --directory dist-production
```

`http://127.0.0.1:4333/`에서 보는 정식 주소 준비본의 내부 페이지·이미지는 로컬 서버에서 동작하고, canonical·hreflang·공유 이미지·구조화 데이터의 절대 주소는 `https://yakseokwon.com`을 가리킵니다. 실제 도메인은 아직 기존 아임웹을 가리킬 수 있으므로, 준비본의 canonical 주소를 클릭해 새 사이트 배포 여부를 판단하지 않습니다.

`SITE_OUTPUT_DIR`는 프로젝트 안의 `dist` 또는 `dist-*`만 허용합니다. 과거의 `SITE_BASE_PATH` 명령은 선택한 프로필 값과 같을 때만 허용하며, 정식 도메인과 GitHub 접두사를 섞으면 빌드를 중단합니다. 프로필별 주소·경로 기록과 검사 결과는 `reports/build-<profile>.json`, `reports/verification-<profile>.json`에 남습니다.

## GitHub Pages 배포와 전환

`.github/workflows/pages.yml`은 main 변경 시 정식 도메인용 패키지를 먼저 만들고 검사하여 `yakseokwon-production-<run>-<attempt>` 아티팩트로 14일 동안 보관합니다. 이어 현재 배포 프로필을 빌드·검사하고 GitHub Pages에 게시합니다. `PAGES_DEPLOY_PROFILE` 저장소 변수가 없으면 `preview`를 게시하므로, 준비 코드를 배포해도 현재 미리보기 주소를 유지합니다.

정식 연결은 별도 전환 작업입니다. 도메인 구매처와 DNS 권한을 확인하고, GitHub에서 도메인 소유 확인·Pages custom domain 설정을 준비한 뒤 `PAGES_DEPLOY_PROFILE=production`과 DNS 연결을 계획한 시점에 전환합니다. `https://yakseokwon.com`, `www`, HTTPS, 내부 링크·다국어·다운로드·공유 미리보기를 검수한 뒤 기존 아임웹을 정리합니다. 이 저장소는 custom GitHub Actions로 배포하므로, 소스의 CNAME 파일은 연결 설정을 대신하지 않습니다.

현재는 도메인·DNS·아임웹·GA4 설정을 변경하지 않습니다. 모든 HTML의 `noindex, nofollow, noarchive`도 유지합니다. robots.txt는 이 지시와 공유 메타데이터를 읽을 수 있도록 크롤링을 허용합니다. 검색 허용·사이트맵 제출·검색 등록은 별도 결정입니다. 개인정보처리방침의 기존 담당자·연락처 등 양식은 실제 운영 정보가 확정되면 정리해야 합니다.

## 편집 위치

- `content/pages/`: 수집한 원본 페이지·게시물 내용과 스타일.
- `content/locales/`: 한국어·영어·중국어 번체·일본어 번역 원본.
- `src/site.css`, `src/site.js`, `src/i18n.js`: 반응형 GUI·메뉴·검색·리뷰·언어 전환.
- `scripts/gui.py`, `scripts/localize.py`: 페이지 구성과 정적 다국어 생성.
- `scripts/site_config.py`, `content/site.json`: 배포 프로필·도메인·경로·출력 폴더.
- `scripts/metadata.py`, `content/metadata.json`: 정적 canonical·언어 대체 링크·공유·브라우저 메타데이터.
- `content/social-images.json`, `public/social/`, `scripts/social_templates.py`: 승인된 공유 이미지, 편집 가능한 HTML/CSS 원본. 건강식 공유 이미지는 원본 흰 로고와 강화도 지도이며, 중앙 정사각형 크롭에도 로고가 온전히 보입니다.
- `public/icons/`, `public/site.webmanifest`: 원본 로고 파비콘·Apple 아이콘·브라우저 매니페스트. 서비스 워커는 없습니다.
- `public/downloads/`: 브랜드 파일과 한국어·영어·중국어 번체·일본어 건강밥/좌훈 브로셔 PDF. 기존 파일은 덮어쓰거나 삭제하지 않습니다.
- `assets-*.zip`, `content/asset-map.json`: 이미지·GIF·서체·스타일의 휴대 가능한 묶음과 대응표. 빌드에 외부 아임웹 접속은 필요하지 않습니다.

메뉴·게시판 상세·검색·페이지 이동·리뷰·이미지 확대·YouTube 외부 재생·네이버 구매/예약·전화·지도 연결을 제공합니다. 결제·회원·아임웹 관리자 기능은 구현 범위에 포함하지 않으며, 게시물은 현재 JSON 수정과 재빌드로 관리합니다. 언론/행사 상세 공유 제목과 설명은 해당 게시물 내용을 사용하고, 원본 근거 없는 리뷰 평점·효능·판매가는 구조화 데이터에 추가하지 않습니다.

원시 수집 자료·검수 기록은 Duggubi-Workspace 작업 폴더에 보존하고 Git과 배포에서는 제외합니다. Google Drive 로컬 저장과 서버 업로드 확인은 구분합니다. GitHub 배포를 되돌릴 때에는 최신 소스의 변경 범위를 확인하고 이전 커밋을 기준으로 새 커밋을 만들어 롤백합니다.

## 에셋 권리

약석원·스튜디오두꺼비의 이미지·민화·로고·3D 아트워크·영상과 브로셔는 각 권리자의 자산입니다. 사이트와 소스 공개는 이 자료의 재사용 허가를 뜻하지 않습니다. 서체·아이콘·공개 스타일에는 원본 라이선스가 적용됩니다.
