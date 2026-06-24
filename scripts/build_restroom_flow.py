#!/usr/bin/env python3
"""화장실 비명감지기 동작 흐름도 — 사용자 원본 좌표·토폴로지 그대로, 플랫 스타일."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/diagrams/restroom-flow.png"
FONT_BOLD = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

SW, SH = 875, 521
OUT_W = 1024
SCALE = OUT_W / SW

BG = (245, 247, 250)
NAVY = (22, 58, 110)
SHADOW = (190, 198, 210)
ORANGE = (232, 140, 60)
RED = (210, 70, 70)
ARROW = (88, 98, 110)
LABEL = (95, 105, 118)
WHITE = (255, 255, 255)

# 사용자 원본(875×521) connected-component 좌표
BOXES = [
    (151, 27, 333, 68, "비명입력대기"),
    (152, 96, 333, 140, "소음발생"),
    (69, 349, 176, 386, "경광등 점멸"),
    (190, 349, 297, 386, "경고 방송"),
    (326, 349, 433, 386, "비상 호출"),
    (325, 428, 432, 465, "호출 접수"),
    (484, 423, 645, 464, "위치확인"),
    (683, 256, 824, 331, "통화/감청"),
    (514, 119, 623, 165, "긴급 출동"),
]
DIAMONDS = [
    (242, 226, "비명인식"),
    (131, 460, "알람시간"),
    (567, 293, "음성통화"),
]
WATCHDOG_GROUP = (62, 338, 303, 392, "워치독")
SITROOM_GROUP = (318, 415, 655, 472)
SITROOM_LABEL = (668, 432, "112상황실 / 경비실")
PATH_LABELS = [
    (118, 208, "일반소음"),
    (248, 252, "비명"),
    (52, 448, "25초"),
    (362, 402, "유선/무선"),
    (652, 278, "Yes"),
]
H_CONN = (432, 446, 484, 446)

PATHS = [
    [(242, 68), (242, 96)],
    [(242, 140), (242, 185)],
    [(165, 226), (95, 226), (95, 48), (151, 48)],
    [(242, 267), (242, 310), (122, 310), (122, 349)],
    [(242, 267), (242, 349)],
    [(242, 267), (379, 310), (379, 349)],
    [(122, 386), (122, 410), (131, 410), (131, 428)],
    [(243, 386), (243, 410), (175, 410), (131, 410)],
    [(69, 460), (45, 460), (45, 48), (151, 48)],
    [(379, 386), (379, 410), (378, 410), (378, 428)],
    [(564, 423), (564, 340), (567, 340), (567, 335)],
    [(645, 293), (683, 293)],
    [(567, 253), (568, 165)],
    [(753, 256), (753, 180), (623, 180), (623, 165)],
]


def sc(v: float) -> int:
    return int(round(v * SCALE))


def fonts():
    return (
        ImageFont.truetype(FONT_BOLD, sc(13)),
        ImageFont.truetype(FONT_BOLD, sc(14)),
    )


def spt(x: float, y: float) -> tuple[int, int]:
    return sc(x), sc(y)


def arrowhead(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], size: int = 7) -> None:
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 and dy == 0:
        return
    ang = math.atan2(dy, dx)
    left = (b[0] - size * math.cos(ang - 0.45), b[1] - size * math.sin(ang - 0.45))
    right = (b[0] - size * math.cos(ang + 0.45), b[1] - size * math.sin(ang + 0.45))
    draw.polygon([b, left, right], fill=ARROW)


def draw_path(draw: ImageDraw.ImageDraw, pts: list[tuple[float, float]]) -> None:
    sp = [spt(x, y) for x, y in pts]
    for i in range(len(sp) - 1):
        draw.line([sp[i], sp[i + 1]], fill=ARROW, width=2)
    arrowhead(draw, sp[-2], sp[-1])


def draw_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], text: str, font) -> None:
    x0, y0, x1, y1 = xy
    r = sc(8)
    draw.rounded_rectangle((x0 + 2, y0 + 2, x1 + 2, y1 + 2), radius=r, fill=SHADOW)
    draw.rounded_rectangle(xy, radius=r, fill=NAVY)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2), text, font=font, fill=WHITE)


def draw_diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str, font) -> None:
    w, h = sc(54), sc(30)
    pts = [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]
    draw.polygon([(p[0] + 2, p[1] + 2) for p in pts], fill=SHADOW)
    draw.polygon(pts, fill=ORANGE)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, font=font, fill=WHITE)


def dashed_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = xy
    dash, gap = sc(7), sc(5)
    for x in range(x0, x1, dash + gap):
        draw.line([(x, y0), (min(x + dash, x1), y0)], fill=RED, width=2)
        draw.line([(x, y1), (min(x + dash, x1), y1)], fill=RED, width=2)
    for y in range(y0, y1, dash + gap):
        draw.line([(x0, y), (x0, min(y + dash, y1))], fill=RED, width=2)
        draw.line([(x1, y), (x1, min(y + dash, y1))], fill=RED, width=2)


def dashed_hline(draw: ImageDraw.ImageDraw, x0: int, y: int, x1: int) -> None:
    dash, gap = sc(5), sc(4)
    for x in range(x0, x1, dash + gap):
        draw.line([(x, y), (min(x + dash, x1), y)], fill=RED, width=2)


def main() -> None:
    box_f, grp_f = fonts()
    oh = int(SH * SCALE)
    canvas = Image.new("RGB", (OUT_W, oh), BG)
    draw = ImageDraw.Draw(canvas)

    gx0, gy0, gx1, gy1, glabel = WATCHDOG_GROUP
    dashed_rect(draw, (sc(gx0), sc(gy0), sc(gx1), sc(gy1)))
    draw.text((sc(gx0) + sc(4), sc(gy0) - sc(18)), glabel, font=grp_f, fill=RED)

    sx0, sy0, sx1, sy1 = SITROOM_GROUP
    dashed_rect(draw, (sc(sx0), sc(sy0), sc(sx1), sc(sy1)))
    lx, ly, ltext = SITROOM_LABEL
    draw.text((sc(lx), sc(ly)), ltext, font=grp_f, fill=RED)

    hx0, hy, hx1, _ = H_CONN
    dashed_hline(draw, sc(hx0), sc(hy), sc(hx1))

    for pts in PATHS:
        draw_path(draw, pts)

    for x0, y0, x1, y1, text in BOXES:
        draw_box(draw, (sc(x0), sc(y0), sc(x1), sc(y1)), text, box_f)

    for cx, cy, text in DIAMONDS:
        draw_diamond(draw, sc(cx), sc(cy), text, box_f)

    for x, y, text in PATH_LABELS:
        draw.text((sc(x), sc(y)), text, font=box_f, fill=LABEL)

    canvas.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
