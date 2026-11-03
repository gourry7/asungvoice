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
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
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
<a href="tel:07087099911" class="mobile-nav__tel">070-8709-9911</a>
</nav>"""


def footer(depth: int) -> str:
    p = "../" * depth
    return f"""<footer class="footer"><div class="container">
<div class="footer__top"><div class="footer__brand"><span>아성<em>보이스</em></span><p>소리로 지키는 안전</p></div>
<nav class="footer__links"><a href="{p}company/greeting.html">회사소개</a><a href="{p}products/elevator.html">제품소개</a><a href="{p}business/index.html">사업영역</a><a href="{p}support/resources.html">자료실</a><a href="{p}support/notice.html">공지사항</a><a href="{p}support/inquiry.html">문의하기</a><a href="{p}sitemap.html">사이트맵</a></nav></div>
<div class="footer__legal"><a href="http://www.asungvoice.com/sub/pop_privacy.html" target="_blank" rel="noopener">개인정보처리방침</a><span>|</span><a href="http://www.asungvoice.com/sub/pop_email.html" target="_blank" rel="noopener">이메일수집거부</a></div>
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


def page_shell(depth, title, desc, breadcrumb, h1, sidebar, body, css_extra="", script_extra=""):
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
<body class="page-neu page-sub">
{header(depth)}
<section class="page-hero"><div class="container"><div class="breadcrumb">{breadcrumb}</div><h1>{h1}</h1></div></section>
<main id="main"><div class="container sub-layout">{sidebar}<div class="content-area">
{body}
</div></div></main>
{footer(depth)}
{script_extra}
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
  s = ROOT / "support"
  board_script = '<script src="../js/board.js"></script>'

  write(s / "resources.html", page_shell(1,
    "자료실", "워치독 설치메뉴얼·제품 자료",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>자료실</span>',
    "자료실", support_sidebar("resources.html"),
    f"""<div class="content-block reveal"><p>설치메뉴얼·대응매뉴얼·동영상 자료입니다. 제목을 클릭하면 파일을 다운로드할 수 있습니다.</p>
<div data-board="resources"></div>
<p class="board-admin-link"><a href="admin.html">관리자</a></p></div>""",
    script_extra=board_script,
  ))

  # FAQ - from support_data.json
  import json
  data = json.loads((ROOT / "scripts" / "support_data.json").read_text(encoding="utf-8"))
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

  write(s / "as-inquiry.html", page_shell(1,
    "A/S 문의", "워치독 A/S 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>A/S 문의</span>',
    "A/S 문의", support_sidebar("as-inquiry.html"),
    AS_INQUIRY_BODY,
  ))

  write(s / "cases.html", page_shell(1,
    "제품설치사례", "워치독 설치 사례",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품설치사례</span>',
    "제품설치사례", support_sidebar("cases.html"),
    f"""<div class="content-block reveal"><p>전국 아파트·대학·공공시설 설치 사례입니다. 사진을 클릭하면 상세 내용을 확인할 수 있습니다.</p>
<div data-board="cases"></div>
<p class="board-admin-link"><a href="admin.html">관리자</a></p></div>""",
    script_extra=board_script,
  ))

  write(s / "notice.html", page_shell(1,
    "공지사항", "아성보이스 공지사항·언론보도",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>공지사항</span>',
    "공지사항", support_sidebar("notice.html"),
    f"""<div class="content-block reveal"><p>워치독 비명감지기 관련 뉴스·언론보도·제품 소식입니다.</p>
<div data-board="notices"></div>
<p class="board-admin-link"><a href="admin.html">관리자</a></p></div>""",
    script_extra=board_script,
  ))

  write(s / "inquiry.html", page_shell(1,
    "제품문의", "아성보이스 제품 문의",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>제품문의</span>',
    "제품문의", support_sidebar("inquiry.html"),
    INQUIRY_BODY,
  ))

  admin_body = """
<div id="admin-login" class="admin-panel neu-card">
<h2>관리자 로그인</h2>
<p class="admin-hint">자료실 · 설치사례 · 공지사항을 등록·수정합니다.<br>권한이 있는 관리자만 로그인할 수 있습니다.</p>
<p id="login-error" class="admin-login-error" hidden></p>
<form id="login-form">
<label class="form__label">관리자 비밀번호</label>
<input type="password" id="login-pass" class="form__input" required autocomplete="current-password" minlength="4">
<button type="submit" class="btn btn--blue neu-btn">로그인</button>
</form>
</div>

<div id="admin-app" hidden>
<div id="github-banner" class="admin-banner" hidden>
<strong>GitHub 연결이 필요합니다</strong>
<p>파일·사진 업로드와 사이트 저장을 위해 아래 GitHub 설정을 완료해 주세요.</p>
</div>

<div class="admin-toolbar">
<div class="admin-tabs">
<button type="button" class="admin-tab is-active" data-tab="resources">자료실</button>
<button type="button" class="admin-tab" data-tab="cases">설치사례</button>
<button type="button" class="admin-tab" data-tab="notices">공지사항</button>
</div>
<div class="admin-toolbar__actions">
<span id="session-badge" class="admin-session-badge" hidden></span>
<button type="button" id="btn-new" class="btn btn--blue btn--sm">+ 새 글</button>
<button type="button" id="btn-save-github" class="btn btn--blue btn--sm">사이트에 저장</button>
<button type="button" id="btn-export" class="btn btn--ghost btn--sm">JSON보내기</button>
<button type="button" id="btn-import" class="btn btn--ghost btn--sm">JSON 가져오기</button>
<input type="file" id="import-file" accept=".json" hidden>
<button type="button" id="btn-logout" class="btn btn--ghost btn--sm">로그아웃</button>
</div></div>
<p id="save-status" class="admin-status"></p>
<div id="admin-list"></div>

<div id="admin-form" class="admin-form neu-card" hidden>
<h3 id="form-title">새 글</h3>
<p id="form-guide" class="admin-form-guide"></p>
<form id="item-form">
<label class="form__label">제목 <span class="req">*</span></label>
<input id="f-title" class="form__input" required>

<div class="admin-field" data-field="date">
<label class="form__label">날짜</label>
<input type="date" id="f-date" class="form__input">
</div>

<div class="admin-field" data-field="file-upload">
<label class="form__label">자료 파일 <span class="req">*</span></label>
<div id="zone-file" class="admin-upload" tabindex="0" role="button" aria-label="자료 파일 업로드">
<div class="admin-upload__inner">
<div class="admin-upload__icon">📄</div>
<p><strong>파일을 끌어다 놓거나 클릭</strong></p>
<p class="admin-upload__hint">PDF, DOC, ZIP, HWP 등 (최대 20MB)</p>
<input type="file" hidden>
</div>
<div class="admin-upload__progress" hidden><div class="admin-upload__bar-wrap"><div class="admin-upload__bar"></div></div></div>
<div class="admin-upload__done" hidden></div>
</div>
</div>

<div class="admin-field" data-field="image-upload">
<label class="form__label">설치 사진 <span class="req">*</span></label>
<div class="admin-image-row">
<div id="zone-image" class="admin-upload admin-upload--image" tabindex="0" role="button" aria-label="설치 사진 업로드">
<div class="admin-upload__inner">
<div class="admin-upload__icon">📷</div>
<p><strong>사진을 끌어다 놓거나 클릭</strong></p>
<p class="admin-upload__hint">JPG, PNG, WEBP (최대 8MB)</p>
<input type="file" hidden accept="image/*">
</div>
<div class="admin-upload__progress" hidden><div class="admin-upload__bar-wrap"><div class="admin-upload__bar"></div></div></div>
<div class="admin-upload__done" hidden></div>
</div>
<div class="admin-image-preview">
<img id="image-preview" alt="미리보기" hidden>
<div id="image-preview-empty" class="admin-image-preview__empty">미리보기</div>
<button type="button" id="btn-clear-image" class="btn btn--ghost btn--sm">사진 제거</button>
</div>
</div>
</div>

<div class="admin-field" data-field="note">
<label class="form__label">비고</label>
<input id="f-note" class="form__input" value="다운로드">
</div>

<div class="admin-field" data-field="content">
<label class="form__label">본문 <span class="admin-optional">(링크 없을 때 모달로 표시)</span></label>
<textarea id="f-content" class="form__textarea" rows="5"></textarea>
</div>

<details class="admin-field admin-advanced" data-field="url-advanced">
<summary>고급 — URL 직접 입력</summary>
<label class="form__label">링크 URL</label>
<input id="f-url" class="form__input" placeholder="https://...">
<div data-field="image-url">
<label class="form__label">이미지 URL</label>
<input id="f-image" class="form__input" placeholder="https://...">
</div>
</details>

<div class="form__actions">
<button type="submit" class="btn btn--blue neu-btn">항목 저장</button>
<button type="button" id="btn-cancel" class="btn btn--ghost">취소</button>
</div>
</form></div>

<details id="github-setup" class="admin-github neu-card" open>
<summary>GitHub 연결 (파일 업로드 · 사이트 저장)</summary>
<p class="admin-hint">GitHub Personal Access Token (<code>repo</code> 권한)을 발급해 입력하면 파일 업로드와 「사이트에 저장」이 가능합니다.<br>
토큰은 이 브라우저에만 저장되며 서버로 전송되지 않습니다.</p>
<form id="github-form">
<label class="form__label">GitHub 사용자</label><input id="gh-owner" class="form__input" placeholder="gourry7">
<label class="form__label">저장소 이름</label><input id="gh-repo" class="form__input" placeholder="asungvoice">
<label class="form__label">브랜치</label><input id="gh-branch" class="form__input" value="main">
<label class="form__label">Pages URL <span class="admin-optional">(업로드 파일 주소)</span></label>
<input id="gh-pages" class="form__input" placeholder="https://gourry7.github.io/asungvoice">
<label class="form__label">Personal Access Token</label>
<input type="password" id="gh-token" class="form__input" autocomplete="off" placeholder="ghp_...">
<button type="submit" class="btn btn--outline btn--sm">연결 저장</button>
</form>
</details>

<details class="admin-github neu-card">
<summary>비밀번호 변경</summary>
<p class="admin-hint">8자 이상의 새 비밀번호를 설정하세요. GitHub 연결 시 자동으로 저장됩니다.</p>
<form id="pw-form">
<label class="form__label">현재 비밀번호</label>
<input type="password" id="pw-current" class="form__input" autocomplete="current-password">
<label class="form__label">새 비밀번호</label>
<input type="password" id="pw-new" class="form__input" autocomplete="new-password" minlength="8">
<label class="form__label">새 비밀번호 확인</label>
<input type="password" id="pw-confirm" class="form__input" autocomplete="new-password" minlength="8">
<button type="submit" class="btn btn--outline btn--sm">비밀번호 변경</button>
</form>
</details>
</div>

"""
  write(s / "admin.html", page_shell(1,
    "게시판 관리", "고객지원 게시판 관리",
    f'<a href="../index.html">홈</a> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>고객지원</span> <svg viewBox="0 0 24 24" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg> <span>관리자</span>',
    "게시판 관리",
    support_sidebar("resources.html").replace(
      '</nav></aside>',
      '<a href="admin.html" class="is-active">게시판 관리</a></nav></aside>',
    ),
    admin_body,
    script_extra='<script src="../js/admin.js"></script>',
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
</table></div>"""
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
        text = text.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
        )
        if 'format-detection' not in text and '<head>' in text:
            text = text.replace(
                '<meta charset="UTF-8">',
                '<meta charset="UTF-8">\n<meta name="format-detection" content="telephone=no">',
                1,
            )
        if path.name != "index.html":
            if 'class="page-neu page-sub"' not in text:
                text = text.replace('class="page-neu"', 'class="page-neu page-sub"', 1)
            if 'class="page-neu"' not in text and "<body>" in text:
                text = text.replace('<body>', '<body class="page-neu page-sub">', 1)
        elif 'class="page-neu"' not in text:
            text = text.replace('<body>', '<body class="page-neu page-home">', 1)
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
