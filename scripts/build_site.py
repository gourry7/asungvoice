#!/usr/bin/env python3
"""Generate shared layout fragments and update all site pages."""
import re
from pathlib import Path

from page_content import (
    AS_INQUIRY_BODY,
    BUSINESS_BODY,
    ELEVATOR_BODY,
    HOME_KEEPER_BODY,
    INQUIRY_BODY,
    LIGHT_SWITCH_BODY,
    MODULE_BODY,
    RESTROOM_BODY,
)

ROOT = Path(__file__).resolve().parent.parent

MOB_PROD_SHORT = {
    "home-keeper.html": "마이안심이",
    "elevator.html": "승강기",
    "restroom.html": "화장실",
    "light-switch.html": "일괄소등",
    "module.html": "모듈",
}

PRODUCTS = [
    ("home-keeper.html", "마이안심이"),
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
<header class="header header--neu is-solid"><div class="container header__inner">
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
<body class="page-neu">
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

  write(p / "home-keeper.html", page_shell(1,
    "마이안심이",
    "마이안심이 — 1인 여성 가구 라이프스타일 안심 오브제, On-Device AI 비명 인식",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>마이안심이</span>',
    "마이안심이",
    product_sidebar("home-keeper.html"),
    HOME_KEEPER_BODY,
  ))

  # Restroom - WatchDog (same product family as elevator)
  write(p / "restroom.html", page_shell(1,
    "화장실 비명감지기",
    "워치독 화장실용 비명감지기 — 노출형·매입형, 승강기와 동일한 워치독 제품",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>화장실 비명감지기</span>',
    "화장실 비명감지기",
    product_sidebar("restroom.html"),
    RESTROOM_BODY,
  ))

  write(p / "elevator.html", page_shell(1,
    "승강기 비명감지기",
    "WD-600MD 승강기 비명감지기 — 딥러닝 AI 비명인식, 삼성 에스원 공급",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>승강기 비명감지기</span>',
    "승강기 비명감지기",
    product_sidebar("elevator.html"),
    ELEVATOR_BODY,
  ))

  write(p / "light-switch.html", page_shell(1,
    "비명인식 일괄소등스위치",
    "신축 아파트 세대현관용 홈네트워크 연동 비명인식 일괄소등스위치",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>일괄소등스위치</span>',
    "비명인식 일괄소등스위치",
    product_sidebar("light-switch.html"),
    LIGHT_SWITCH_BODY,
  ))

  write(p / "module.html", page_shell(1,
    "비명인식 모듈",
    "WD-Module-V2 비명인식 임베디드 모듈 — 지하주차장·OEM/ODM",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품소개</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>비명인식 모듈</span>',
    "비명인식 모듈",
    product_sidebar("module.html"),
    MODULE_BODY,
  ))


def build_business():
  write(ROOT / "business" / "index.html", page_shell(1,
    "사업영역",
    "아성보이스 비명인식 사업 — B2B 워치독, B2C 마이안심이",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>사업영역</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>비명인식사업</span>',
    "사업영역",
    '<aside class="sidebar"><div class="sidebar__title">사업영역</div><nav class="sidebar__nav"><a href="index.html" class="is-active">비명인식사업</a></nav></aside>',
    BUSINESS_BODY,
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

  # A/S
  write(s / "as-inquiry.html", page_shell(1,
    "A/S 문의", "워치독 A/S 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>A/S 문의</span>',
    "A/S 문의", support_sidebar("as-inquiry.html"),
    AS_INQUIRY_BODY,
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

  # 제품문의
  write(s / "inquiry.html", page_shell(1,
    "제품문의", "아성보이스 제품 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품문의</span>',
    "제품문의", support_sidebar("inquiry.html"),
    INQUIRY_BODY,
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
    '<a href="{p}products/home-keeper.html">마이안심이</a>'
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
    '<a href="home-keeper.html">마이안심이</a>'
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
        text = text.replace('홈 안전지킴이', '마이안심이')
        if 'class="page-neu"' not in text:
            text = text.replace('<body>', '<body class="page-neu">', 1)
        text = text.replace('class="header is-solid"', 'class="header header--neu is-solid"')
        text = re.sub(
            r'\n?<script src="https://cdn\.jsdelivr\.net/npm/swiper@11/swiper-bundle\.min\.js"></script>',
            '',
            text,
        )
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print(f"  patched {path.relative_to(ROOT)}")


if __name__ == "__main__":
    print("Building site pages...")
    build_products()
    build_business()
    build_support()
    build_greeting()
    print("Patching navigation...")
    patch_nav()
    print("Done.")
