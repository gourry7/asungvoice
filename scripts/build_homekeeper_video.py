#!/usr/bin/env python3
"""마이안심이 시스템 구성도 → 단계별 설명 동영상 생성"""
from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/images/diagrams/homekeeper-system.png"
OUT = ROOT / "assets/videos/homekeeper-system.mp4"
FONT_BOLD = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
FONT_REG = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
W, H = 1920, 1080
FPS = 30

STEPS = [
    {
        "num": "1",
        "title": "현관 문 열림",
        "desc": "문이 열리면 마이안심이가 바로 감시를 시작합니다",
        "box": (25, 130, 315, 850),
    },
    {
        "num": "2",
        "title": "자석감지기 감지",
        "desc": "BLE 무선 센서가 문 열림을 즉시 본체에 알립니다",
        "box": (320, 130, 610, 850),
    },
    {
        "num": "3",
        "title": "마이안심이 대기",
        "desc": "AI 비명인식 대기모드 — \"강도야! 사람살려!\" 즉시 분석",
        "box": (615, 130, 905, 850),
    },
    {
        "num": "4",
        "title": "즉시 경보",
        "desc": "110dB 이상 강력 사이렌으로 범인을 퇴치합니다",
        "box": (910, 130, 1200, 850),
    },
    {
        "num": "5",
        "title": "보호자에게 알림",
        "desc": "앱 푸시 · 비상 문자 · 112 긴급 신고까지 한 번에",
        "box": (1205, 130, 1510, 850),
    },
]


def load_fonts():
    return {
        "title": ImageFont.truetype(FONT_BOLD, 56),
        "sub": ImageFont.truetype(FONT_REG, 34),
        "step": ImageFont.truetype(FONT_BOLD, 44),
        "desc": ImageFont.truetype(FONT_REG, 32),
        "badge": ImageFont.truetype(FONT_BOLD, 72),
        "brand": ImageFont.truetype(FONT_BOLD, 48),
    }


def bg_canvas() -> Image.Image:
    img = Image.new("RGB", (W, H), "#E8ECF0")
    return img


def paste_cover(canvas: Image.Image, src: Image.Image, pad: int = 48) -> None:
    area = (pad, pad, W - pad, H - pad - 120)
    aw, ah = area[2] - area[0], area[3] - area[1]
    ratio = min(aw / src.width, ah / src.height)
    nw, nh = int(src.width * ratio), int(src.height * ratio)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x = area[0] + (aw - nw) // 2
    y = area[1] + (ah - nh) // 2
    canvas.paste(resized, (x, y))


def draw_footer(draw: ImageDraw.ImageDraw, fonts, title: str, desc: str, accent: str = "#E8919F"):
    bar_y = H - 118
    draw.rounded_rectangle((60, bar_y, W - 60, H - 40), radius=24, fill="#FFFFFF", outline="#D8DEE8", width=2)
    draw.text((100, bar_y + 18), title, font=fonts["step"], fill="#1B2D5C")
    draw.text((100, bar_y + 64), desc, font=fonts["desc"], fill="#5A6478")
    draw.rounded_rectangle((W - 200, bar_y + 24, W - 80, bar_y + 94), radius=18, fill=accent)
    draw.text((W - 190, bar_y + 38), "마이안심이", font=fonts["sub"], fill="#FFFFFF")


def frame_intro(fonts, full: Image.Image, t: float, duration: float) -> Image.Image:
    canvas = bg_canvas()
    draw = ImageDraw.Draw(canvas)
    alpha = min(1.0, t / 0.6)
    paste_cover(canvas, full, pad=80)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((120, 80, W - 120, 220), radius=20, fill=(255, 255, 255, int(230 * alpha)))
    canvas = canvas.convert("RGBA")
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)
    draw.text((160, 118), "마이안심이 시스템 구성", font=fonts["brand"], fill="#1B2D5C")
    draw.text((160, 176), "이렇게 나를 지켜요 — 5단계로 쉽게 이해하기", font=fonts["sub"], fill="#5A6478")
    draw_footer(draw, fonts, "1인 가구 맞춤 스마트 방범", "지금부터 동작 순서를 하나씩 보여드립니다")
    return canvas.convert("RGB")


def frame_step(fonts, full: Image.Image, step: dict, t: float, duration: float) -> Image.Image:
    canvas = bg_canvas()
    draw = ImageDraw.Draw(canvas)
    x1, y1, x2, y2 = step["box"]
    crop = full.crop((x1, y1, x2, y2))

    zoom = 1.0 + 0.06 * (1 - math.cos(min(1.0, t / duration) * math.pi)) / 2
    cw, ch = crop.size
    nw, nh = int(cw * zoom), int(ch * zoom)
    enlarged = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - cw) // 2)
    top = max(0, (nh - ch) // 2)
    crop_zoom = enlarged.crop((left, top, left + cw, top + ch))

    area_top, area_bottom = 250, H - 150
    aw, ah = W - 160, area_bottom - area_top
    ratio = min(aw / crop_zoom.width, ah / crop_zoom.height)
    rw, rh = int(crop_zoom.width * ratio), int(crop_zoom.height * ratio)
    panel = crop_zoom.resize((rw, rh), Image.Resampling.LANCZOS)
    px = 80 + (aw - rw) // 2
    py = area_top + (ah - rh) // 2

    card = Image.new("RGBA", (rw + 40, rh + 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, rw + 39, rh + 39), radius=28, fill="#FFFFFF", outline="#D8DEE8", width=3)
    card.paste(panel, (20, 20))
    canvas.paste(card, (px - 20, py - 20), card)

    fade = min(1.0, t / 0.4) * min(1.0, (duration - t) / 0.4) if duration > 0.8 else 1.0
    badge_alpha = int(255 * fade)
    badge = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse((0, 0, 119, 119), fill=(232, 145, 159, badge_alpha))
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(badge, (90, 90), badge)
    draw = ImageDraw.Draw(canvas_rgba)
    draw.text((118, 108), step["num"], font=fonts["badge"], fill=(255, 255, 255, badge_alpha))
    draw.text((240, 108), f"STEP {step['num']}", font=fonts["sub"], fill="#E8919F")
    draw.text((240, 150), step["title"], font=fonts["title"], fill="#1B2D5C")

    draw_footer(draw, fonts, f"{step['num']}. {step['title']}", step["desc"])
    return canvas_rgba.convert("RGB")


def frame_outro(fonts, full: Image.Image, t: float, duration: float) -> Image.Image:
    canvas = bg_canvas()
    paste_cover(canvas, full, pad=60)
    draw = ImageDraw.Draw(canvas)
    draw_footer(draw, fonts, "마이안심이", "나를 지켜주는 스마트한 안심 파트너 · 아성보이스")
    return canvas


def write_frames(frames_dir: Path) -> int:
    fonts = load_fonts()
    full = Image.open(SRC).convert("RGB")
    idx = 0

    def save(img: Image.Image):
        nonlocal idx
        img.save(frames_dir / f"frame_{idx:05d}.png")
        idx += 1

    intro_sec = 2.5
    step_sec = 3.2
    outro_sec = 3.0

    for f in range(int(intro_sec * FPS)):
        save(frame_intro(fonts, full, f / FPS, intro_sec))

    for step in STEPS:
        for f in range(int(step_sec * FPS)):
            save(frame_step(fonts, full, step, f / FPS, step_sec))

    for f in range(int(outro_sec * FPS)):
        save(frame_outro(fonts, full, f / FPS, outro_sec))

    return idx


def encode_video(frames_dir: Path, count: int) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-frames:v", str(count),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        "-movflags", "+faststart",
        str(OUT),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    if not SRC.exists():
        raise SystemExit(f"Source image not found: {SRC}")
    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp)
        count = write_frames(frames_dir)
        encode_video(frames_dir, count)
    print(f"Created {OUT} ({count / FPS:.1f}s)")


if __name__ == "__main__":
    main()
