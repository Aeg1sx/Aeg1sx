#!/usr/bin/env python3
"""Render a quiet terminal GIF and a reduced-motion fallback. Requires Pillow >= 10.

Run: python3 scripts/render_banner.py
"""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1280, 400)
SCALE = 2
FRAMES = 64
FRAME_MS = 100
BG = (9, 15, 19)
PANEL = (12, 21, 25)
BORDER = (35, 54, 57)
MINT = (130, 227, 187)
WHITE = (226, 239, 233)
MUTED = (128, 153, 145)
FAINT = (66, 94, 87)


def find_font():
    for candidate in [
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ]:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError("Install a monospace font and add its path to find_font().")


FONT_PATH = find_font()


def font(size):
    return ImageFont.truetype(FONT_PATH, round(size * SCALE))


def frame(index):
    canvas = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BG)
    draw = ImageDraw.Draw(canvas)

    def rect(box, color, outline=None, radius=0, width=1):
        scaled = tuple(round(v * SCALE) for v in box)
        if radius:
            draw.rounded_rectangle(scaled, radius=radius * SCALE, fill=color,
                                   outline=outline, width=width * SCALE)
        else:
            draw.rectangle(scaled, fill=color, outline=outline, width=width * SCALE)

    def line(points, color, width=1):
        draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                  fill=color, width=width * SCALE)

    def text(x, y, value, size, color):
        draw.text((round(x * SCALE), round(y * SCALE)), value,
                  font=font(size), fill=color, anchor="lt")

    rect((1, 1, 1278, 398), BG, BORDER, radius=12)
    rect((2, 2, 1277, 48), PANEL, radius=10)
    rect((2, 36, 1277, 48), PANEL)
    line([(1, 49), (1278, 49)], BORDER)
    for x, color in [(27, FAINT), (45, FAINT), (63, (93, 148, 127))]:
        draw.ellipse((x * SCALE, 21 * SCALE, (x + 7) * SCALE, 28 * SCALE), fill=color)
    text(94, 19, "aeg1sx@research  ~", 14, MUTED)
    text(1084, 19, "RESEARCH LOG", 12, FAINT)

    text(51, 86, "$ whoami", 19, MINT)
    text(47, 128, "AEGIS", 88, WHITE)
    text(52, 240, "Security Researcher / Bug Hunter", 22, MUTED)

    line([(765, 88), (765, 278)], BORDER)
    text(808, 89, "RESEARCH FOCUS", 13, FAINT)
    for y, number, label in [
        (129, "01", "AI SAST / DAST"),
        (177, "02", "WEB / APP / FIRMWARE"),
        (225, "03", "REVERSING / CLOUD"),
    ]:
        text(808, y + 3, number, 12, FAINT)
        text(848, y, label, 20, WHITE)

    line([(51, 304), (1227, 304)], BORDER)
    text(52, 336, "CURRENT BUILD", 13, MUTED)
    text(229, 331, "AI Security Engineer", 23, MINT)
    if (index // 8) % 2 == 0:
        rect((519, 332, 530, 355), MINT)
    text(1127, 337, "ONGOING", 12, MUTED)

    # A low-contrast signal moves locally; the text and background stay still.
    phase = index / FRAMES
    alpha = math.sin(math.pi * phase) ** 2
    start = 51 + 1075 * phase
    for offset in range(100):
        strength = alpha * math.sin(math.pi * offset / 100) * 0.65
        color = tuple(round(BORDER[c] + (MINT[c] - BORDER[c]) * strength)
                      for c in range(3))
        x = round(start + offset)
        line([(x, 304), (x, 305)], color)

    return canvas.resize(SIZE, Image.Resampling.LANCZOS)


def main():
    ASSETS.mkdir(exist_ok=True)
    frames = [frame(i) for i in range(FRAMES)]
    frames[0].save(ASSETS / "research-banner.png", optimize=True)
    sample = Image.new("RGB", (SIZE[0], SIZE[1] * 3))
    for i, index in enumerate((0, FRAMES // 4, FRAMES // 2)):
        sample.paste(frames[index], (0, i * SIZE[1]))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    indexed[0].save(ASSETS / "research-banner.gif", save_all=True,
                    append_images=indexed[1:], duration=FRAME_MS, loop=0,
                    optimize=True, disposal=1)
    with Image.open(ASSETS / "research-banner.gif") as check:
        assert check.is_animated and check.n_frames == FRAMES
        assert check.info.get("loop") == 0 and check.size == SIZE
        duration = 0
        for i in range(check.n_frames):
            check.seek(i)
            check.load()
            duration += check.info["duration"]
        assert duration == FRAMES * FRAME_MS
    print(f"Rendered {FRAMES} frames; {duration / 1000:.1f}s loop; "
          f"{(ASSETS / 'research-banner.gif').stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
