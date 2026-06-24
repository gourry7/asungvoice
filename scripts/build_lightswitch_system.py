#!/usr/bin/env python3
"""일괄소등스위치 — 소비자용 5단계 시스템 구성도."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/diagrams/lightswitch-system.png"
OUT_MOBILE = ROOT / "assets/images/diagrams/lightswitch-system-mobile.png"
FB = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
FR = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

W, H = 1536, 620

BG = (248, 251, 255)
NAVY = (18, 49, 96)
BLUE = (40, 95, 175)
BLUE_LT = (232, 241, 253)
MINT = (222, 245, 241)
PINK = (255, 236, 238)
RED = (218, 64, 64)
WHITE = (255, 255, 255)
TEXT = (46, 56, 72)
MUTED = (105, 119, 140)
BORDER = (216, 226, 240)

STEPS = [
    ("외부인 방문 감지", "세대카메라와 자석감지기가\n방문·문열림을 확인해요", MINT),
    ("비명인식 준비", "현관 상황일 때만\n스위치가 비명을 기다려요", BLUE_LT),
    ("월패드 즉시 경보", "「사람살려!」를 인식하면\n집 안 월패드에 경보가 울려요", PINK),
    ("단지서버로 전달", "월패드 경보 신호가\n아파트 서버로 전달돼요", BLUE_LT),
    ("도움 요청 알림", "경비실·휴대폰·인접세대에\n비상 상황을 알려요", PINK),
]

def ft(bold: bool, n: int):
    return ImageFont.truetype(FB if bold else FR, n)


def box(d, xy, fill, r=20, outline=None, w=0):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


def center(d, rect, text, f, fill, sp=8):
    x0, y0, x1, y1 = rect
    bb = d.multiline_textbbox((0, 0), text, font=f, spacing=sp)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.multiline_text(
        (x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2),
        text, font=f, fill=fill, align="center", spacing=sp,
    )


def arrow(d, x0, y, x1):
    d.line((x0, y, x1 - 18, y), fill=BLUE, width=5)
    d.polygon([(x1, y), (x1 - 20, y - 11), (x1 - 20, y + 11)], fill=BLUE)


def arrow_down(d, x, y0, y1):
    d.line((x, y0, x, y1 - 18), fill=BLUE, width=5)
    d.polygon([(x, y1), (x - 11, y1 - 20), (x + 11, y1 - 20)], fill=BLUE)


def draw_step(d, i, px, py, pw, ph):
    box(d, (px + 3, py + 5, px + pw + 3, py + ph + 5), (231, 237, 247), 24)
    box(d, (px, py, px + pw, py + ph), WHITE, 24, BORDER, 2)

    d.ellipse((px + 22, py + 22, px + 74, py + 74), fill=RED if i in (2, 4) else BLUE)
    center(d, (px + 22, py + 22, px + 74, py + 74), str(i + 1), ft(True, 30), WHITE)
    center(d, (px + 86, py + 27, px + pw - 18, py + 70), f"STEP {i + 1}", ft(True, 20), MUTED)

    icon_h = min(260, ph - 200)
    box(d, (px + 24, py + 98, px + pw - 24, py + 98 + icon_h), STEPS[i][2], 20)
    PICS[i](d, px + pw // 2, py + 98 + icon_h // 2)

    center(d, (px + 16, py + ph - 118, px + pw - 16, py + ph - 72), STEPS[i][0], ft(True, 29), NAVY)
    center(d, (px + 18, py + ph - 68, px + pw - 18, py + ph - 24), STEPS[i][1], ft(False, 22), TEXT, sp=10)


def build_desktop():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pw, gap, x0, top = 280, 18, 44, 30
    ph = 560
    for i in range(5):
        px = x0 + i * (pw + gap)
        draw_step(d, i, px, top, pw, ph)
        if i < 4:
            arrow(d, px + pw + 4, top + ph // 2, px + pw + gap - 4)
    img.save(OUT, "PNG")
    print(f"Wrote {OUT}")


def build_mobile():
    mw, pad, gap, card_h = 720, 20, 14, 470
    mh = pad * 2 + card_h * 5 + gap * 4
    img = Image.new("RGB", (mw, mh), BG)
    d = ImageDraw.Draw(img)
    pw = mw - pad * 2
    y = pad
    for i in range(5):
        draw_step(d, i, pad, y, pw, card_h)
        y += card_h
        if i < 4:
            arrow_down(d, mw // 2, y + 4, y + gap - 4)
            y += gap
    img.save(OUT_MOBILE, "PNG")
    print(f"Wrote {OUT_MOBILE}")


def pill(d, xy, text, fill, outline, text_fill=NAVY, size=21):
    box(d, xy, fill, 18, outline, 2)
    center(d, xy, text, ft(True, size), text_fill)


def pic_visit(d, cx, cy):
    # Door
    box(d, (cx - 100, cy - 60, cx - 22, cy + 70), WHITE, 14, NAVY, 3)
    box(d, (cx - 84, cy - 42, cx - 36, cy + 55), BLUE_LT, 8)
    d.ellipse((cx - 47, cy + 4, cx - 37, cy + 14), fill=NAVY)
    # Camera
    box(d, (cx + 14, cy - 72, cx + 82, cy - 18), WHITE, 12, NAVY, 3)
    d.ellipse((cx + 38, cy - 58, cx + 60, cy - 36), fill=BLUE)
    d.rectangle((cx + 43, cy - 18, cx + 53, cy + 4), fill=NAVY)
    # Magnetic sensor
    box(d, (cx + 18, cy + 24, cx + 48, cy + 74), WHITE, 8, NAVY, 3)
    box(d, (cx + 58, cy + 30, cx + 82, cy + 68), WHITE, 8, NAVY, 3)
    d.arc((cx - 5, cy - 8, cx + 35, cy + 32), 300, 60, fill=BLUE, width=4)
    d.arc((cx + 0, cy - 18, cx + 50, cy + 42), 300, 60, fill=BLUE, width=3)
    pill(d, (cx - 110, cy + 92, cx + 110, cy + 132), "방문·문열림", WHITE, (177, 211, 204), NAVY, 20)


def pic_scream(d, cx, cy):
    box(d, (cx - 76, cy - 58, cx + 76, cy + 72), NAVY, 18)
    box(d, (cx - 54, cy - 36, cx + 54, cy + 40), (62, 108, 190), 12)
    center(d, (cx - 52, cy - 30, cx + 52, cy + 34), "일괄소등\n스위치", ft(True, 22), WHITE, sp=3)
    box(d, (cx - 104, cy - 104, cx + 38, cy - 56), WHITE, 18, RED, 3)
    center(d, (cx - 104, cy - 104, cx + 38, cy - 56), "사람살려!", ft(True, 25), RED)
    d.polygon([(cx - 2, cy - 56), (cx + 20, cy - 56), (cx + 8, cy - 42)], fill=WHITE)
    pill(d, (cx - 102, cy + 98, cx + 102, cy + 138), "비명만 인식", WHITE, (187, 205, 235), NAVY, 20)


def pic_wallpad(d, cx, cy):
    box(d, (cx - 104, cy - 58, cx + 104, cy + 62), WHITE, 18, NAVY, 3)
    box(d, (cx - 84, cy - 38, cx + 84, cy + 40), BLUE_LT, 12)
    d.ellipse((cx - 25, cy - 12, cx + 25, cy + 30), fill=RED)
    d.rectangle((cx - 9, cy - 34, cx + 9, cy - 12), fill=RED)
    d.arc((cx - 54, cy - 30, cx - 18, cy + 24), 110, 250, fill=RED, width=5)
    d.arc((cx + 18, cy - 30, cx + 54, cy + 24), 290, 70, fill=RED, width=5)
    center(d, (cx - 70, cy + 82, cx + 70, cy + 122), "HN 월패드", ft(True, 21), NAVY)


def pic_server(d, cx, cy):
    box(d, (cx - 80, cy - 64, cx + 80, cy + 68), WHITE, 16, NAVY, 3)
    for idx, y in enumerate((cy - 38, cy - 8, cy + 22)):
        box(d, (cx - 56, y, cx + 56, y + 18), BLUE_LT, 7)
        d.ellipse((cx + 34, y + 5, cx + 44, y + 15), fill=BLUE if idx < 2 else RED)
    pill(d, (cx - 92, cy + 94, cx + 92, cy + 134), "경보신호 전달", WHITE, (187, 205, 235), NAVY, 20)


def pic_alert(d, cx, cy):
    box(d, (cx - 104, cy - 50, cx - 42, cy + 38), WHITE, 12, NAVY, 3)
    d.rectangle((cx - 88, cy - 20, cx - 58, cy + 18), fill=BLUE)
    d.ellipse((cx - 86, cy - 76, cx - 58, cy - 48), fill=RED)
    center(d, (cx - 108, cy + 50, cx - 38, cy + 82), "경비실", ft(True, 18), NAVY)

    box(d, (cx - 20, cy - 68, cx + 36, cy + 50), NAVY, 12)
    box(d, (cx - 12, cy - 54, cx + 28, cy + 22), BLUE_LT, 6)
    d.ellipse((cx + 16, cy - 46, cx + 42, cy - 20), fill=RED)
    center(d, (cx - 34, cy + 58, cx + 52, cy + 90), "휴대폰", ft(True, 18), NAVY)

    box(d, (cx + 66, cy - 48, cx + 118, cy + 38), WHITE, 12, NAVY, 3)
    d.polygon([(cx + 60, cy - 48), (cx + 92, cy - 78), (cx + 124, cy - 48)], fill=BLUE)
    d.ellipse((cx + 90, cy - 66, cx + 110, cy - 46), fill=RED)
    center(d, (cx + 48, cy + 50, cx + 138, cy + 88), "인접세대", ft(True, 18), NAVY)


PICS = [pic_visit, pic_scream, pic_wallpad, pic_server, pic_alert]


def main():
    build_desktop()
    build_mobile()


if __name__ == "__main__":
    main()
