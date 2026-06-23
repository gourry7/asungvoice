#!/usr/bin/env python3
"""Generate shared layout fragments and update all site pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MOB_PROD_SHORT = {
    "home-keeper.html": "홈 안전지킴이",
    "elevator.html": "승강기",
    "restroom.html": "화장실",
    "light-switch.html": "일괄소등",
    "module.html": "모듈",
}

PRODUCTS = [
    ("home-keeper.html", "홈 안전지킴이"),
    ("elevator.html", "승강기 비명감지기"),
    ("restroom.html", "화장실 비명감지기"),
    ("light-switch.html", "비명인식 일괄소등스위치"),
    ("module.html", "비명인식 모듈"),
]

SUPPORT = [
    ("inquiry.html", "제품문의"),
    ("as-inquiry.html", "A/S 문의"),
    ("faq.html", "자주하는질문"),
    ("resources.html", "자료실"),
    ("cases.html", "제품설치사례"),
    ("notice.html", "공지사항"),
]

HEAD = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic+Round:wght@700;800&display=swap" rel="stylesheet">
<link rel="icon" href="{icon}" type="image/png">"""


def header(depth: int, active_nav: str = "") -> str:
    p = "../" * depth
    prod_drop = "".join(
        f'<a href="{p}products/{slug}">{label}</a>' for slug, label in PRODUCTS
    )
    sup_drop = "".join(
        f'<a href="{p}support/{slug}">{label}</a>' for slug, label in SUPPORT
    )
    mob_prod = "".join(
        f'<a href="{p}products/{slug}">{MOB_PROD_SHORT.get(slug, label)}</a>'
        for slug, label in PRODUCTS
    )
    mob_sup = "".join(
        f'<a href="{p}support/{slug}">{label}</a>' for slug, label in SUPPORT
    )
    css = f"{p}css/style.css"
    return f"""<a href="#main" class="skip">본문 바로가기</a>
<header class="header is-solid"><div class="container header__inner">
<a href="{p}index.html" class="logo"><img src="{p}assets/images/logo.png" alt="아성보이스" width="32" height="32"><span>아성<em>보이스</em></span></a>
<nav class="nav" aria-label="주메뉴">
<div class="nav__item"><a href="{p}company/greeting.html" class="nav__link">회사소개</a><div class="nav__drop"><a href="{p}company/greeting.html">인사말</a><a href="{p}company/location.html">오시는 길</a></div></div>
<div class="nav__item"><a href="{p}products/elevator.html" class="nav__link">제품소개</a><div class="nav__drop">{prod_drop}</div></div>
<div class="nav__item"><a href="{p}business/index.html" class="nav__link">사업영역</a></div>
<div class="nav__item"><a href="{p}support/inquiry.html" class="nav__link">고객지원</a><div class="nav__drop">{sup_drop}</div></div>
</nav>
<div class="header__right"><a href="tel:07087099911" class="btn btn--outline btn--sm">070-8709-9911</a><a href="{p}support/inquiry.html" class="btn btn--blue btn--sm">문의하기</a>
<button class="menu-btn" aria-label="메뉴" aria-expanded="false"><span></span><span></span><span></span></button></div>
</div></header>
<nav class="mobile-nav" aria-label="모바일 메뉴">
<div class="mobile-nav__label">회사소개</div><a href="{p}company/greeting.html">인사말</a><a href="{p}company/location.html">오시는 길</a>
<div class="mobile-nav__label">제품소개</div>{mob_prod}
<div class="mobile-nav__label">고객지원</div>{mob_sup}
</nav>"""


def footer(depth: int) -> str:
    p = "../" * depth
    return f"""<footer class="footer"><div class="container">
<div class="footer__top"><div class="footer__brand"><img src="{p}assets/images/logo.png" alt="" width="36" height="36"><span>아성보이스</span><p>소리로 지키는 안전, 워치독</p></div>
<nav class="footer__links"><a href="{p}company/greeting.html">회사소개</a><a href="{p}products/elevator.html">제품소개</a><a href="{p}business/index.html">사업영역</a><a href="{p}support/resources.html">자료실</a><a href="{p}support/notice.html">공지사항</a><a href="{p}support/inquiry.html">문의하기</a><a href="{p}sitemap.html">사이트맵</a></nav></div>
<div class="footer__legal"><a href="http://www.asungvoice.com/sub/pop_privacy.html" target="_blank" rel="noopener">개인정보처리방침</a><span>|</span><a href="http://www.asungvoice.com/sub/pop_email.html" target="_blank" rel="noopener">이메일수집거부</a><span>|</span><a href="http://www.celtechworld.com/" target="_blank" rel="noopener">(주)셀텍월드</a></div>
<address class="footer__info">대표: 이승현 | 서울시 금천구 가산디지털1로 149, 3층 304디-14호 | <a href="tel:07087099911">070-8709-9911</a> | 팩스: 02-6203-1689<br>사업자등록번호 118-87-00016 | Copyright &copy; 2016 아성보이스.</address>
</div></footer>
<script src="{p}js/main.js"></script>"""


def product_sidebar(active: str) -> str:
    links = "".join(
        f'<a href="{slug}" class="{"is-active" if slug == active else ""}">{label}</a>'
        for slug, label in PRODUCTS
    )
    return f'<aside class="sidebar"><div class="sidebar__title">제품소개</div><nav class="sidebar__nav">{links}</nav></aside>'


def support_sidebar(active: str) -> str:
    links = "".join(
        f'<a href="{slug}" class="{"is-active" if slug == active else ""}">{label}</a>'
        for slug, label in SUPPORT
    )
    return f'<aside class="sidebar"><div class="sidebar__title">고객지원</div><nav class="sidebar__nav">{links}</nav></aside>'


def page_shell(depth, title, desc, breadcrumb, h1, sidebar, body, css_extra=""):
    p = "../" * depth
    icon = f"{p}assets/images/logo.png"
    css = f"{p}css/style.css"
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
{HEAD.format(icon=icon)}
<title>{title} | 아성보이스</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{css}">
{css_extra}
</head>
<body>
{header(depth)}
<section class="page-hero"><div class="container"><div class="breadcrumb">{breadcrumb}</div><h1>{h1}</h1></div></section>
<main id="main"><div class="container sub-layout">{sidebar}<div class="content-area">
{body}
</div></div></main>
{footer(depth)}
</body></html>"""


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


def build_products():
  p = ROOT / "products"

  # Restroom - WatchDog (same product family as elevator)
  write(p / "restroom.html", page_shell(1,
    "화장실 비명감지기",
    "워치독 화장실용 비명감지기 — 노출형·매입형, 승강기와 동일한 워치독 제품",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>화장실 비명감지기</span>',
    "화장실 비명감지기",
    product_sidebar("restroom.html"),
    """<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/logo-watchdog.png" alt="워치독 화장실 비명감지기"></div>
<div class="prod-hero__info"><span class="model">워치독 WatchDog · WD 시리즈</span><h2>화장실 비명인식기</h2>
<p>승강기용 워치독과 <strong>동일한 비명인식 기술</strong>을 적용한 제품입니다. 노출형·매입형으로 화장실 천정에 설치하며, 대화는 녹음·전송되지 않고 비명 발생 시에만 경보합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>
<div class="content-block reveal"><h2>개발 배경</h2>
<p>공공 화장실은 개인정보보호법상 CCTV 설치가 불가능한 안전 사각지대입니다. 몰카·성범죄·폭행 등 여성 대상 강력범죄가 빈번하며, 기존 비상벨은 제압당하거나 당황한 상황에서 사용하기 어렵습니다.</p>
<p>워치독은 "사람살려", "아악" 등 비명만으로 위급 상황을 즉시 인지하여 버튼 조작 없이 112·경비실로 자동 호출합니다.</p></div>
<div class="content-block reveal"><h2>시스템 구성</h2>
<p>화장실 센서(노출형/매입형) → 유선·RF 중계기 또는 3G/LTE 모듈 → 112 상황실·경비실·관제센터 연동</p>
<div class="content-img"><img src="../assets/images/pages/sub2_2.jpg" alt="화장실 비명감지기 시스템 구성도"></div></div>
<div class="content-block reveal"><h2>제품 유형</h2>
<div class="feature-grid">
<div class="feature-box"><h4>노출형</h4><p>천정·벽면 표면 부착 설치</p></div>
<div class="feature-box"><h4>매입형</h4><p>다운라이트 홀 규격 매립, 미관 우수</p></div>
<div class="feature-box"><h4>유·무선 연동</h4><p>접점식 유선 및 RF 무선 중계 지원</p></div>
</div></div>
<div class="content-block reveal"><h2>동작 흐름</h2><div class="flow">
<div class="flow__step"><div class="num">1</div><h4>비명 대기</h4><p>365일 24시간</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">2</div><h4>AI 비명 인식</h4><p>오인식 필터링</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">3</div><h4>경광등·방송</h4><p>범행 억제</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">4</div><h4>비상호출</h4><p>25초 내 전파</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">5</div><h4>출동·대응</h4><p>음성통화·긴급출동</p></div></div></div>
<div class="content-block reveal"><h2>적용 사례</h2>
<div class="feature-grid">
<div class="feature-box"><h4>부산대학교</h4><p>400개소 설치</p></div>
<div class="feature-box"><h4>여의도 파크원</h4><p>217개소 설치</p></div>
</div></div>
<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>제품군</th><td>워치독 WatchDog (승강기용과 동일 기술)</td></tr>
<tr><th>적용기술</th><td>딥러닝, 멀티트리거, 실시간 고속인식</td></tr>
<tr><th>인식방식</th><td>음원인식 — 여성·아동 음성 최적화</td></tr>
<tr><th>마이크</th><td>2 MIC (DIGITAL)</td></tr>
<tr><th>인식 단어</th><td>아악, 꺄악, 강도야, 사람살려, 도와주세요</td></tr>
<tr><th>프라이버시</th><td>녹음·감청 없음, 소리 패턴만 분석</td></tr>
<tr><th>설치장소</th><td>화장실, 탈의실, 독서실 등</td></tr></table></div>
<div class="content-block reveal"><p class="note-box">※ 화장실 비명감지기는 <a href="elevator.html">승강기 비명감지기</a>와 동일한 워치독 제품군이며, 설치 환경에 따라 노출형·매입형을 선택합니다. 세대 현관용 제품은 <a href="light-switch.html">비명인식 일괄소등스위치</a>를 참고하세요.</p></div>"""
  ))

  # Light switch - separate product
  write(p / "light-switch.html", page_shell(1,
    "비명인식 일괄소등스위치",
    "신축 아파트 세대현관용 홈네트워크 연동 비명인식 일괄소등스위치",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>일괄소등스위치</span>',
    "비명인식 일괄소등스위치",
    product_sidebar("light-switch.html"),
    """<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/control-panel.png" alt="비명인식 일괄소등스위치"></div>
<div class="prod-hero__info"><span class="model">5&quot; FTS · 홈네트워크 연동</span><h2>비명인식 일괄소등스위치</h2>
<p>신축 아파트 세대현관에 설치되는 스마트 스위치입니다. 일괄소등·엘리베이터 호출 등 생활편의 기능과 함께, 재택 중 침입 위협 시 비명을 감지하여 월패드·경비실로 즉시 통보합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>
<div class="content-block reveal"><h2>개발 배경</h2>
<p>기존 방범은 외출 시 도난 방지에 초점이 맞춰져 있습니다. 택배·배달원 위장 침입, 귀가 직후 도어락 래그 범죄 등 <strong>재실 중 대면 범죄</strong>에 취약합니다.</p>
<p>비명인식 일괄소등스위치는 현관문 내측에 설치되어, 위급 상황에서 비명만으로 경비실·월패드·휴대폰에 동시 알림을 전송합니다.</p></div>
<div class="content-block reveal"><h2>시스템 구성</h2>
<div class="content-img"><img src="../assets/images/pages/sub2_4.jpg" alt="일괄소등스위치 시스템 구성도"></div>
<p>세대현관 5&quot; FTS 스위치 → HN 월패드(RS-485) → 단지 서버 → 경비실·입주민 스마트폰</p></div>
<div class="content-block reveal"><h2>특허 기술 — 오작동 방지</h2>
<p>특허 제10-2132316호, 제10-2237852호. 평상시 비명인식 비활성 → <strong>방문자 호출·현관문 개방 등 외부인 대면 시에만 활성화</strong>하여 TV·생활소음 오작동을 원천 차단합니다.</p></div>
<div class="content-block reveal"><h2>제품 특징</h2>
<div class="feature-grid">
<div class="feature-box"><h4>일괄 소등</h4><p>외출 시 세대 조명 일괄 제어</p></div>
<div class="feature-box"><h4>엘리베이터 호출</h4><p>외출 전 승강기 미리 호출</p></div>
<div class="feature-box"><h4>비명인식 보안</h4><p>HN 월패드·경비실 자동 연동</p></div>
<div class="feature-box"><h4>생활 정보</h4><p>날씨·미세먼지·택배 알림</p></div>
</div></div>
<div class="content-block reveal"><h2>적용 실적</h2>
<div class="feature-grid">
<div class="feature-box"><h4>진주 아너스</h4><p>840세대 (2024.08)</p></div>
<div class="feature-box"><h4>유승한내들</h4><p>444세대</p></div>
<div class="feature-box"><h4>협력사</h4><p>(주)스필 배선기구 전문</p></div>
</div></div>
<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>디스플레이</th><td>5&quot; Full Touch LCD (정전식)</td></tr>
<tr><th>전원</th><td>AC 220V / 60Hz</td></tr>
<tr><th>통신</th><td>RS-485 (홈넷 연동)</td></tr>
<tr><th>설치</th><td>세대 현관 벽면 매입</td></tr>
<tr><th>인식 단어</th><td>강도야, 사람살려, 도와주세요</td></tr>
<tr><th>특허</th><td>제10-2132316호, 제10-2237852호</td></tr>
<tr><th>설치위치</th><td>세대현관문 내측</td></tr></table></div>"""
  ))


def build_support():
  import json
  data = json.loads((ROOT / "scripts" / "support_data.json").read_text(encoding="utf-8"))
  s = ROOT / "support"

  # 자료실
  res_rows = "".join(
    f'<tr><td>{len(data["resources"])-i}</td>'
    f'<td><a href="{r["url"]}" target="_blank" rel="noopener">{r["title"]}</a></td>'
    f'<td><span class="board-badge">다운로드</span></td></tr>'
    for i, r in enumerate(data["resources"])
  )
  write(s / "resources.html", page_shell(1,
    "자료실", "워치독 설치메뉴얼·제품 자료",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>자료실</span>',
    "자료실", support_sidebar("resources.html"),
    f"""<div class="content-block reveal"><p>설치메뉴얼·대응매뉴얼·동영상 자료입니다. 제목을 클릭하면 상세 페이지에서 파일을 다운로드할 수 있습니다.</p>
<table class="board-table"><thead><tr><th>번호</th><th>제목</th><th>비고</th></tr></thead><tbody>{res_rows}</tbody></table>
<p style="margin-top:16px"><a href="http://www.asungvoice.com/sub/sub04_04.php?boardid=data" class="btn btn--blue btn--sm" target="_blank" rel="noopener">자료실 전체 보기 →</a></p></div>"""
  ))

  # FAQ - original dl/dt style
  faq_html = "".join(
    f'<details class="faq-item"><summary>{f["q"]}</summary><p>{f["a"]}</p></details>'
    for f in data["faqs"]
  )
  write(s / "faq.html", page_shell(1,
    "자주하는질문", "워치독 비명감지기 FAQ",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>자주하는질문</span>',
    "자주하는질문", support_sidebar("faq.html"),
    f'<div class="content-block reveal"><div class="faq-list">{faq_html}</div>'
    f'<p style="margin-top:20px"><a href="http://www.asungvoice.com/sub/sub04_03.php?boardid=faq" class="btn btn--outline btn--sm" target="_blank" rel="noopener">FAQ 전체 보기 →</a></p></div>'
  ))

  # A/S - original image content
  write(s / "as-inquiry.html", page_shell(1,
    "A/S 문의", "워치독 A/S 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>A/S 문의</span>',
    "A/S 문의", support_sidebar("as-inquiry.html"),
    """<div class="content-block reveal">
<div class="content-img"><img src="../assets/images/support/as-inquiry.jpg" alt="A/S 문의 안내"></div>
<p style="margin-top:16px">A/S 문의는 대표전화 <a href="tel:07087099911"><strong>070-8709-9911</strong></a> 또는 팩스 02-6203-1689로 연락 주세요.</p>
<a href="http://www.asungvoice.com/sub/sub04_02.php" class="btn btn--outline btn--sm" target="_blank" rel="noopener">기존 A/S 페이지 →</a></div>"""
  ))

  # 설치사례 - gallery grid like original
  thumbs = [
    ("11", "41dae014647e3adaf5e9fa359f7870990.jpg", "삼성 래미안 (영등포 프레비뉴)"),
    ("8", "003eac7cce7a101ca313bbbe6bdca16a0.png", "부산대학교 여자화장실"),
    ("7", "84ebf4e1f9c5debf43e73ca50a9b9dcb0.jpg", "대림산업 E편한세상 (수지)"),
    ("6", "0b08395c42464f12a37efb96cc1d4c0d0.png", "개포우성3차 아파트"),
    ("80", "6550ae467015f7a700da337310e1555b0.png", "롯데캐슬리버파크시그니처"),
    ("79", "c12f12b4a8f415d89f04413a5d93f23e0.png", "경희궁자이3단지"),
    ("78", "0a4570f1f6b715f7044be3bc1aa361170.png", "시티오씨엘1단지"),
    ("77", "ceb0fd28f3a3edb6a60d0b9c4622cc080.png", "독립문극동아파트"),
    ("76", "f3b7d97fffec38d7214acbc8da7fc6820.png", "이편한세상고덕어반브릿지"),
  ]
  case_grid = "".join(
    f'<a class="case-card" href="http://www.asungvoice.com/sub/sub04_05.php?boardid=result&mode=view&idx={idx}" target="_blank" rel="noopener">'
    f'<img src="http://www.asungvoice.com/uploaded/board/result/{img}" alt="{title}" loading="lazy">'
    f'<span>{title}</span></a>'
    for idx, img, title in thumbs
  )
  write(s / "cases.html", page_shell(1,
    "제품설치사례", "워치독 설치 사례",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품설치사례</span>',
    "제품설치사례", support_sidebar("cases.html"),
    f"""<div class="content-block reveal"><p>전국 아파트·대학·공공시설 설치 사례입니다. 사진을 클릭하면 상세 내용을 확인할 수 있습니다.</p>
<div class="case-grid">{case_grid}</div>
<p style="margin-top:20px"><a href="http://www.asungvoice.com/sub/sub04_05.php?boardid=result" class="btn btn--blue btn--sm" target="_blank" rel="noopener">설치사례 전체 보기 →</a></p></div>"""
  ))

  # 공지사항
  notice_rows = "".join(
    f'<tr><td>{n["date"]}</td><td><a href="{n["url"]}" target="_blank" rel="noopener">{n["title"]}</a></td></tr>'
    for n in data["notices"]
  )
  write(s / "notice.html", page_shell(1,
    "공지사항", "아성보이스 공지사항·언론보도",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>공지사항</span>',
    "공지사항", support_sidebar("notice.html"),
    f"""<div class="content-block reveal"><p>워치독 비명감지기 관련 뉴스·언론보도·제품 소식입니다.</p>
<table class="board-table"><thead><tr><th>날짜</th><th>제목</th></tr></thead><tbody>{notice_rows}</tbody></table>
<p style="margin-top:16px"><a href="http://www.asungvoice.com/sub/sub04_06.php?boardid=notice" class="btn btn--blue btn--sm" target="_blank" rel="noopener">공지사항 전체 보기 →</a></p></div>"""
  ))

  # 제품문의 - original form fields POST
  write(s / "inquiry.html", page_shell(1,
    "제품문의", "아성보이스 제품 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품문의</span>',
    "제품문의", support_sidebar("inquiry.html"),
    """<div class="content-block reveal"><p>워치독 비명감지기 도입 상담을 환영합니다.</p></div>
<form class="form reveal" action="http://www.asungvoice.com/module/online/online_evn.php" method="post" target="_blank">
<input type="hidden" name="evnMode" value="join">
<input type="hidden" name="o_type" value="1">
<input type="hidden" name="returnURL" value="/sub/sub04_01.php">
<div class="form__row"><div class="form__group"><label class="form__label">회사명 / 단지명 <span class="req">*</span></label><input class="form__input" name="company" required></div>
<div class="form__group"><label class="form__label">승강기 설치대수</label><input class="form__input" name="serial" placeholder="대"></div></div>
<div class="form__row"><div class="form__group"><label class="form__label">성명 <span class="req">*</span></label><input class="form__input" name="user_name" required></div>
<div class="form__group"><label class="form__label">직위</label><input class="form__input" name="duty"></div></div>
<div class="form__group"><label class="form__label">연락처 <span class="req">*</span></label>
<div class="form__row"><select name="phone_1" class="form__input"><option>010</option><option>02</option><option>070</option></select>
<input class="form__input" name="phone_2" placeholder="국번" required> <input class="form__input" name="phone_3" placeholder="번호" required></div></div>
<div class="form__group"><label class="form__label">이메일</label>
<input class="form__input" name="email_id" placeholder="계정"> @ <input class="form__input" name="email_domain" placeholder="도메인"></div>
<div class="form__group"><label class="form__label">관심분야</label>
<div class="form__checks">
<label class="form__check"><input type="checkbox" name="field[]" value="1"> 승강기 보안설비</label>
<label class="form__check"><input type="checkbox" name="field[]" value="2"> 택배/배달 사칭 현관문보안</label>
<label class="form__check"><input type="checkbox" name="field[]" value="3"> 화장실 보안설비</label>
<label class="form__check"><input type="checkbox" name="field[]" value="4"> 비명인식 협업</label>
</div></div>
<div class="form__group"><label class="form__label">문의사항 <span class="req">*</span></label><textarea class="form__textarea" name="contents" required></textarea></div>
<label class="form__check"><input type="checkbox" name="agree" value="Y" required> 개인정보 수집 및 이용에 동의합니다.</label>
<div class="form__actions"><button type="submit" class="btn btn--blue">제출</button>
<a href="tel:07087099911" class="btn btn--ghost">전화 문의</a></div>
</form>
<div class="card reveal" style="margin-top:24px;text-align:center"><p>카카오 플러스친구: <strong>아성보이스</strong></p></div>"""
  ))


def build_greeting():
  write(ROOT / "company" / "greeting.html", page_shell(1,
    "인사말",
    "아성보이스 인사말 — AI 음성 인식 비명감지기 전문 기업",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>회사소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>인사말</span>',
    "인사말",
    '<aside class="sidebar"><div class="sidebar__title">회사소개</div><nav class="sidebar__nav"><a href="greeting.html" class="is-active">인사말</a><a href="location.html">오시는 길</a></nav></aside>',
    """<div class="content-block reveal">
<h2>보이지 않는 곳까지 지킵니다</h2>
<p>(주)아성보이스는 음성인식기술 기반의 비명감지기 전문업체입니다. 2015년 설립 이래 승강기·화장실·세대현관·1인 가구 등 범죄 사각지대를 AI 비명인식으로 보호하고 있습니다.</p>
<div class="quote-box">
<p>강력범죄/성범죄가 사라지는 그 날까지 기술개발에 모든 역량을 모으고 최선의 노력을 다 할 것을 약속 드립니다.</p>
<cite>— 주식회사 아성보이스 임직원 일동</cite>
</div></div>
<div class="content-block reveal"><h2>회사 개요</h2>
<table class="spec-table">
<tr><th>법인명</th><td>㈜ 아성보이스 (Asungvoice Co., Ltd.)</td></tr>
<tr><th>설립일</th><td>2015년 4월 1일</td></tr>
<tr><th>대표자</th><td>이승현</td></tr>
<tr><th>사업분야</th><td>비명인식 응용제품 기획·개발·유통</td></tr>
</table></div>
<div class="content-block reveal"><h2>주요 연혁</h2>
<ul class="timeline">
<li><strong>2017.09</strong> 삼성 에스원 업무협약 및 워치독 공급</li>
<li><strong>2020.11</strong> 승강기 안전기술 우수상 (한국승강기안전공단)</li>
<li><strong>2021.04</strong> 비명인식 특허 2건 확보</li>
<li><strong>2023.01</strong> (주)스필 사업협력 개시</li>
<li><strong>2024.07</strong> 마이안심이 실용신안 확보 (제20-0498161호)</li>
<li><strong>2024.08</strong> 일괄소등스위치 진주아너스 840세대 최초 적용</li>
<li><strong>2025.10</strong> 미쓰비시엘리베이터 협력사 등록</li>
</ul></div>
<div class="content-block reveal"><h2>보유 특허</h2>
<table class="spec-table">
<tr><th>제10-2132316호</th><td>비명인식 일괄소등스위치 오동작 방지 (2020.07)</td></tr>
<tr><th>제10-2237852호</th><td>비명인식 일괄소등스위치 오동작 방지 (2021.04)</td></tr>
<tr><th>제20-0498161호</th><td>마이안심이 1인여성가구용 방범장치 (2024.07)</td></tr>
</table></div>
<div class="content-block reveal"><h2>협력 파트너</h2>
<p>삼성 에스원 · 미쓰비시엘리베이터 · 후지테크코리아 · (주)스필 · 셀텍월드 · 아마노</p></div>"""
  ))


OLD_PROD_NAV = (
    '<a href="{p}products/home-keeper.html">홈 안전지킴이</a>'
    '<a href="{p}products/elevator.html">승강기 비명감지기</a>'
    '<a href="{p}products/restroom.html">화장실 비명감지기</a>'
    '<a href="{p}products/module.html">비명인식 모듈</a>'
)
NEW_PROD_NAV = (
    '<a href="{p}products/home-keeper.html">홈 안전지킴이</a>'
    '<a href="{p}products/elevator.html">승강기 비명감지기</a>'
    '<a href="{p}products/restroom.html">화장실 비명감지기</a>'
    '<a href="{p}products/light-switch.html">비명인식 일괄소등스위치</a>'
    '<a href="{p}products/module.html">비명인식 모듈</a>'
)
OLD_SUP_NAV = (
    '<a href="{p}support/notice.html">공지사항</a>'
    '<a href="{p}support/inquiry.html">문의하기</a>'
)
NEW_SUP_NAV = (
    '<a href="{p}support/inquiry.html">제품문의</a>'
    '<a href="{p}support/as-inquiry.html">A/S 문의</a>'
    '<a href="{p}support/faq.html">자주하는질문</a>'
    '<a href="{p}support/resources.html">자료실</a>'
    '<a href="{p}support/cases.html">제품설치사례</a>'
    '<a href="{p}support/notice.html">공지사항</a>'
)
OLD_SIDEBAR = (
    '<a href="home-keeper.html">홈 안전지킴이</a>'
    '<a href="elevator.html">승강기 비명감지기</a>'
    '<a href="restroom.html">화장실 비명감지기</a>'
    '<a href="module.html">비명인식 모듈</a>'
)
NEW_SIDEBAR = (
    '<a href="home-keeper.html">홈 안전지킴이</a>'
    '<a href="elevator.html">승강기 비명감지기</a>'
    '<a href="restroom.html">화장실 비명감지기</a>'
    '<a href="light-switch.html">비명인식 일괄소등스위치</a>'
    '<a href="module.html">비명인식 모듈</a>'
)


def patch_nav():
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        orig = text
        if "products/" in text or path.name in ("index.html", "sitemap.html"):
            for p in ("../", ""):
                text = text.replace(OLD_PROD_NAV.format(p=p), NEW_PROD_NAV.format(p=p))
        if "support/" in text or path.name in ("index.html", "sitemap.html"):
            for p in ("../", ""):
                text = text.replace(OLD_SUP_NAV.format(p=p), NEW_SUP_NAV.format(p=p))
        if path.parent.name == "products":
            text = text.replace(OLD_SIDEBAR, NEW_SIDEBAR)
            text = re.sub(
                r'(<a href="restroom\.html"(?: class="[^"]*")?>화장실 비명감지기</a>)'
                r'(<a href="module\.html")',
                r'\1<a href="light-switch.html">비명인식 일괄소등스위치</a>\2',
                text,
            )
        # mobile nav product lines
        text = text.replace(
            '<a href="../products/restroom.html">화장실</a><a href="../products/module.html">모듈</a>',
            '<a href="../products/restroom.html">화장실</a><a href="../products/light-switch.html">일괄소등</a><a href="../products/module.html">모듈</a>',
        )
        text = text.replace(
            '<a href="products/restroom.html">화장실 비명감지기</a>\n  <a href="products/module.html">비명인식 모듈</a>',
            '<a href="products/restroom.html">화장실 비명감지기</a>\n  <a href="products/light-switch.html">일괄소등스위치</a>\n  <a href="products/module.html">비명인식 모듈</a>',
        )
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print(f"  patched {path.relative_to(ROOT)}")


if __name__ == "__main__":
    print("Building site pages...")
    build_products()
    build_support()
    build_greeting()
    print("Patching navigation...")
    patch_nav()
    print("Done.")
