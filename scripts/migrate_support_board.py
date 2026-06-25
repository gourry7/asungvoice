#!/usr/bin/env python3
"""Migrate 자료실·설치사례·공지사항 from asungvoice.com into local JSON + files."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data/support-board.json"
DL_RES = ROOT / "data/downloads/resources"
DL_NOTICE = ROOT / "data/downloads/notices"
IMG_CASE = ROOT / "data/board/cases"
IMG_NOTICE = ROOT / "data/board/notices"
BASE = "http://www.asungvoice.com"
UA = {"User-Agent": "Mozilla/5.0 (compatible; AsungVoiceMigrator/1.0)"}


def fetch(url: str, binary: bool = False) -> bytes | str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8", "ignore")


def download_file(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        data = fetch(url, binary=True)
        if len(data) < 32:
            return False
        dest.write_bytes(data)
        return True
    except Exception as exc:
        print(f"  ! download failed {dest.name}: {exc}")
        return False


def guess_ext(name: str, url: str = "") -> str:
    name = unescape(name or "")
    if "." in name:
        return "." + name.rsplit(".", 1)[-1].lower()[:8]
    if ".pdf" in url.lower():
        return ".pdf"
    if ".mp4" in url.lower():
        return ".mp4"
    if ".jpg" in url.lower() or ".jpeg" in url.lower():
        return ".jpg"
    if ".png" in url.lower():
        return ".png"
    return ".bin"


def abs_url(path: str) -> str:
    if path.startswith("http"):
        return path
    if path.startswith("/"):
        return BASE + path
    return BASE + "/" + path


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_gallery_list(html: str, boardid: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    by_idx: dict[str, dict] = {}
    for a in soup.select('.gallery-list a[href*="mode=view"]'):
        m = re.search(r"idx=(\d+)", a.get("href", ""))
        if not m:
            continue
        idx = m.group(1)
        item = by_idx.setdefault(idx, {"idx": idx, "title": "", "date": "", "file_idx": None, "thumb": ""})
        title = a.get_text(strip=True)
        if title:
            item["title"] = title
        img = a.select_one("img")
        if img and img.get("src"):
            item["thumb"] = abs_url(img["src"])
    return [v for v in by_idx.values() if v["title"]]


def parse_list_rows(html: str, boardid: str) -> list[dict]:
    if "gallery-list" in html:
        return parse_gallery_list(html, boardid)
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("table tr"):
        a = tr.select_one(f'a[href*="boardid={boardid}"][href*="mode=view"]')
        if not a:
            continue
        m = re.search(r"idx=(\d+)", a.get("href", ""))
        if not m:
            continue
        idx = m.group(1)
        title = a.get_text(strip=True)
        dl = tr.select_one('a[href*="download("]')
        file_idx = None
        if dl:
            dm = re.search(r"download\('[^']+','(\d+)','(\d+)'\)", dl.get("href", "") or "")
            if not dm:
                dm = re.search(r"download\('[^']+','(\d+)','(\d+)'\)", tr.decode_contents())
            if dm and dm.group(1) == idx:
                file_idx = dm.group(2)
        tds = [td.get_text(strip=True) for td in tr.select("td")]
        date = ""
        for td in reversed(tds):
            if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", td):
                date = td.replace(".", "-")
                break
        rows.append({"idx": idx, "title": title, "date": date, "file_idx": file_idx})
    return rows


def collect_paginated(list_path: str, boardid: str, step: int) -> list[dict]:
    seen: set[str] = set()
    items: list[dict] = []
    offset = 0
    while True:
        q = f"?offset={offset}" if offset else ""
        html = fetch(f"{BASE}{list_path}{q}")
        batch = parse_list_rows(html, boardid)
        new = [r for r in batch if r["idx"] not in seen]
        if not new:
            break
        for r in new:
            seen.add(r["idx"])
            items.append(r)
        if len(batch) < step and offset > 0:
            break
        offset += step
        if offset > 500:
            break
        time.sleep(0.15)
    return items


def parse_view(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(".board-view .tit")
    title = title_el.get_text(strip=True) if title_el else ""
    date_el = soup.select_one(".board-view .date")
    date_raw = date_el.get_text(strip=True) if date_el else ""
    date = date_raw[:10].replace(".", "-") if date_raw else ""

    attachments = []
    for a in soup.select('.fileLayer a[href*="download("]'):
        dm = re.search(r"download\('([^']+)','(\d+)','(\d+)'\)", a.get("href", ""))
        if dm:
            attachments.append({
                "boardid": dm.group(1),
                "b_idx": dm.group(2),
                "idx": dm.group(3),
                "name": a.get("title") or a.get_text(strip=True),
            })

    body = soup.select_one(".board-view .body")
    body_html = ""
    if body:
        for tag in body.select("script, style"):
            tag.decompose()
        body_html = body.decode_contents().strip()

    images = []
    if body:
        for img in body.select("img[src]"):
            src = img.get("src", "")
            if "/uploaded/" in src:
                images.append(abs_url(src))

    return {
        "title": title,
        "date": date,
        "attachments": attachments,
        "body_html": body_html,
        "images": images,
    }


def sanitize_html(html: str, url_map: dict[str, str]) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(f"<div>{html}</div>", "html.parser")
    root = soup.div
    for tag in root.select("script, style, iframe, object, embed"):
        tag.decompose()
    for img in root.select("img"):
        src = img.get("src", "")
        full = abs_url(src)
        if full in url_map:
            img["src"] = "../" + url_map[full]
            for attr in ("width", "height", "border"):
                if attr in img.attrs:
                    del img[attr]
        else:
            img.decompose()
    for a in root.select("a"):
        href = a.get("href", "")
        if href.startswith("javascript:") or href == "#":
            a.unwrap()
        elif href.startswith("/") or "asungvoice.com" in href:
            a.unwrap()
    allowed = {"p", "br", "strong", "b", "em", "i", "span", "div", "ul", "ol", "li", "a", "img", "h3", "h4"}
    for tag in root.find_all(True):
        if tag.name not in allowed:
            tag.unwrap()
    text = root.decode_contents().strip()
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def migrate_resources() -> list[dict]:
    print("Migrating resources…")
    items = []
    for page in ["", "?offset=10"]:
        batch = parse_list_rows(fetch(f"{BASE}/sub/sub04_04.php{page}"), "data")
        for row in batch:
            if any(x["idx"] == row["idx"] for x in items):
                continue
            items.append(row)
    items.sort(key=lambda x: int(x["idx"]), reverse=True)

    out = []
    for row in items:
        idx = row["idx"]
        view = parse_view(fetch(f"{BASE}/sub/sub04_04.php?boardid=data&mode=view&idx={idx}"))
        title = view["title"] or row["title"]
        date = row["date"] or view["date"]
        att = view["attachments"][0] if view["attachments"] else None
        if not att and row.get("file_idx"):
            att = {"boardid": "data", "b_idx": idx, "idx": row["file_idx"], "name": title}
        file_field = ""
        if att:
            ext = guess_ext(att["name"], "")
            fname = f"res-{idx}-{att['idx']}{ext}"
            dest = DL_RES / fname
            url = (
                f"{BASE}/module/board/download.php?boardid={att['boardid']}"
                f"&b_idx={att['b_idx']}&idx={att['idx']}"
            )
            if download_file(url, dest):
                file_field = rel(dest)
                print(f"  ✓ {title[:50]} -> {fname}")
        out.append({
            "id": f"res-{idx}",
            "title": title,
            "date": date,
            "file": file_field,
            "note": "다운로드" if file_field else "자료",
        })
        time.sleep(0.1)
    return out


def migrate_cases() -> list[dict]:
    print("Migrating cases…")
    rows = collect_paginated("/sub/sub04_05.php", "result", 9)
    # 원본 사이트 순서 유지 (대표 4건 → 최신순). idx 내림차순 정렬하면 순서가 달라짐.
    out = []
    for row in rows:
        idx = row["idx"]
        view = parse_view(fetch(f"{BASE}/sub/sub04_05.php?boardid=result&mode=view&idx={idx}"))
        title = view["title"] or row["title"]
        date = view["date"] or row.get("date", "")
        url_map: dict[str, str] = {}
        image = ""
        thumb = row.get("thumb")
        if thumb:
            ext = Path(urllib.parse.urlparse(thumb).path).suffix or ".jpg"
            dest = IMG_CASE / f"case-{idx}-thumb{ext}"
            if download_file(thumb, dest):
                image = rel(dest)
                url_map[thumb] = image
        for i, img_url in enumerate(view["images"]):
            ext = Path(urllib.parse.urlparse(img_url).path).suffix or ".jpg"
            dest = IMG_CASE / f"case-{idx}-{i}{ext}"
            if download_file(img_url, dest):
                url_map[img_url] = rel(dest)
                if not image:
                    image = rel(dest)
        content = sanitize_html(view["body_html"], url_map)
        out.append({
            "id": f"case-{idx}",
            "title": title,
            "date": date,
            "image": image,
            "contentHtml": content,
        })
        print(f"  ✓ {title[:50]}")
        time.sleep(0.1)
    return out


def migrate_notices() -> list[dict]:
    print("Migrating notices…")
    rows = collect_paginated("/sub/sub04_06.php", "notice", 10)
    rows.sort(key=lambda x: int(x["idx"]), reverse=True)
    out = []
    for n, row in enumerate(rows, 1):
        idx = row["idx"]
        view = parse_view(fetch(f"{BASE}/sub/sub04_06.php?boardid=notice&mode=view&idx={idx}"))
        title = view["title"] or row["title"]
        date = row["date"] or view["date"]
        url_map: dict[str, str] = {}
        for i, img_url in enumerate(view["images"]):
            ext = Path(urllib.parse.urlparse(img_url).path).suffix or ".jpg"
            dest = IMG_NOTICE / f"notice-{idx}-{i}{ext}"
            if download_file(img_url, dest):
                url_map[img_url] = rel(dest)
        files = []
        for att in view["attachments"]:
            ext = guess_ext(att["name"], "")
            fname = f"notice-{idx}-{att['idx']}{ext}"
            dest = DL_NOTICE / fname
            url = (
                f"{BASE}/module/board/download.php?boardid={att['boardid']}"
                f"&b_idx={att['b_idx']}&idx={att['idx']}"
            )
            if download_file(url, dest):
                files.append({"name": att["name"], "file": rel(dest)})
                if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                    url_map[abs_url(f"/{rel(dest)}")] = rel(dest)
        content = sanitize_html(view["body_html"], url_map)
        if files:
            links = "".join(
                f'<p><a href="../{f["file"]}" download>{f["name"]}</a></p>' for f in files
            )
            content = (content + links) if content else links
        pinned = idx in {"207", "205", "203", "180"}
        out.append({
            "id": f"notice-{idx}",
            "date": date,
            "title": title,
            "pinned": pinned,
            "contentHtml": content,
        })
        if n % 20 == 0:
            print(f"  … {n}/{len(rows)}")
        time.sleep(0.08)
    out.sort(key=lambda x: (not x.get("pinned"), x["date"]), reverse=True)
    return out


def write_board_files(data: dict) -> None:
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for key, fname in (
        ("resources", "board-resources.json"),
        ("cases", "board-cases.json"),
        ("notices", "board-notices.json"),
    ):
        path = ROOT / "data" / fname
        path.write_text(json.dumps(data[key], ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    data = {
        "resources": migrate_resources(),
        "cases": migrate_cases(),
        "notices": migrate_notices(),
    }
    write_board_files(data)
    print(
        f"\nDone: {len(data['resources'])} resources, "
        f"{len(data['cases'])} cases, {len(data['notices'])} notices"
    )
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
