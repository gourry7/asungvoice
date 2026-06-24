#!/usr/bin/env python3
"""사업영역 — 비명인식 Smart Security 통합 소개 이미지."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/diagrams/biz-overview.png"
OUT_MOBILE = ROOT / "assets/images/diagrams/biz-overview-mobile.png"
FB = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
FR = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

W, H = 1600, 1100

BG = (245, 249, 255)
NAVY = (18, 49, 96)
BLUE = (32, 88, 168)
BLUE_DK = (22, 62, 128)
WHITE = (255, 255, 255)
TEXT = (52, 62, 78)
MUTED = (108, 120, 140)
BORDER = (210, 222, 238)
RED = (218, 64, 64)

AREAS = [
    {
        "title": "워치독 비명감지기",
        "desc": "승강기, 화장실, 독서실, 탈의실",
        "img": ROOT / "assets/images/diagrams/biz-env/biz-env-public.png",
    },
    {
        "title": "비명인식 일괄소등스위치(HN 연동)",
        "desc": "택배/배달기사사칭범죄예방",
        "img": ROOT / "assets/images/diagrams/biz-env/biz-env-entrance.png",
    },
    {
        "title": "지능형 비명인식 SOS 모듈",
        "desc": "지하주차장비상벨시스템",
        "img": ROOT / "assets/images/diagrams/biz-env/biz-env-parking.png",
    },
    {
        "title": "마이안심이",
        "desc": "1인여성가구 맞춤 AI Smart Security",
        "img": ROOT / "assets/images/diagrams/biz-env/biz-env-home.png",
        "badge": "출시예정",
    },
]


def ft(bold: bool, n: int):
    return ImageFont.truetype(FB if bold else FR, n)


def box(d, xy, fill, r=18, outline=None, w=0):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


def center(d, rect, text, f, fill, sp=6):
    x0, y0, x1, y1 = rect
    bb = d.multiline_textbbox((0, 0), text, font=f, spacing=sp)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.multiline_text(
        (x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2),
        text, font=f, fill=fill, align="center", spacing=sp,
    )


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)


def draw_panel(base: Image.Image, idx: int, rect: tuple[int, int, int, int]):
    x0, y0, x1, y1 = rect
    area = AREAS[idx]
    d = ImageDraw.Draw(base)

    box(d, (x0 + 3, y0 + 5, x1 + 3, y1 + 5), (228, 235, 246), 22)
    box(d, (x0, y0, x1, y1), WHITE, 22, BORDER, 2)

    header_h = 58
    box(d, (x0, y0, x1, y0 + header_h), BLUE_DK, 22)
    d.rectangle((x0, y0 + header_h - 18, x1, y0 + header_h), fill=BLUE_DK)
    center(d, (x0 + 16, y0 + 8, x1 - 16, y0 + header_h - 8), area["title"], ft(True, 26), WHITE)

    img_top = y0 + header_h + 14
    img_bottom = y1 - 92
    img_pad = 14
    photo = fit_image(area["img"], (x1 - x0 - img_pad * 2, img_bottom - img_top))
    base.paste(photo, (x0 + img_pad, img_top))

    if area.get("badge"):
        bw, bh = 150, 42
        bx, by = x1 - img_pad - bw - 8, img_top + 12
        box(d, (bx, by, bx + bw, by + bh), RED, 12)
        center(d, (bx, by, bx + bw, by + bh), area["badge"], ft(True, 22), WHITE)

    desc_y0 = y1 - 78
    box(d, (x0 + 14, desc_y0, x1 - 14, y1 - 14), (236, 243, 252), 14, BORDER, 1)
    center(d, (x0 + 24, desc_y0 + 6, x1 - 24, y1 - 20), area["desc"], ft(False, 22), TEXT)


def build_desktop():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    box(d, (36, 28, W - 36, 118), BLUE, 24)
    center(d, (60, 40, W - 60, 106), "비명인식 기반의 Smart Security 시스템", ft(True, 40), WHITE)
    margin_x, margin_y = 40, 140
    gap = 24
    cell_w = (W - margin_x * 2 - gap) // 2
    cell_h = (H - margin_y - 40 - gap) // 2
    for row in range(2):
        for col in range(2):
            i = row * 2 + col
            x0 = margin_x + col * (cell_w + gap)
            y0 = margin_y + row * (cell_h + gap)
            draw_panel(img, i, (x0, y0, x0 + cell_w, y0 + cell_h))
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}")


def build_mobile():
    mw, pad, gap = 720, 20, 16
    title_h = 88
    card_h = 520
    mh = pad + title_h + gap + card_h * 4 + gap * 3 + pad
    img = Image.new("RGB", (mw, mh), BG)
    d = ImageDraw.Draw(img)
    box(d, (pad, pad, mw - pad, pad + title_h), BLUE, 20)
    center(d, (pad + 12, pad + 10, mw - pad - 12, pad + title_h - 10),
           "비명인식 기반의\nSmart Security 시스템", ft(True, 30), WHITE, sp=4)
    y = pad + title_h + gap
    pw = mw - pad * 2
    for i in range(4):
        draw_panel(img, i, (pad, y, pad + pw, y + card_h))
        y += card_h + gap
    img.save(OUT_MOBILE, "PNG", optimize=True)
    print(f"Wrote {OUT_MOBILE}")


def main():
    build_desktop()
    build_mobile()


if __name__ == "__main__":
    main()
