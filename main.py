#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 chat-screenshot meme with PIL and writes it to
<MAKEFUN_OUTPUT_DIR or /output>/entry.png. No network, no external
image files, no randomness and no clock: every run produces the exact
same bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MAX_BYTES = 1_048_576  # the gate's hard 1 MiB cap
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (244, 246, 249)
HEADER = (31, 42, 68)
HEADER_SUB = (159, 179, 200)
USER_FILL = (47, 124, 246)
AGENT_FILL = (227, 231, 238)
WHITE = (255, 255, 255)
BLACK = (18, 22, 30)
ACCENT = (64, 224, 208)
GREEN = (74, 222, 128)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap against pixel width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def bubble(draw, box, fill, text, fnt, text_color, align_right=False):
    """One rounded chat bubble with wrapped bold text inside."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=30, fill=fill)
    pad = 30
    lines = wrap(draw, text, fnt, (x1 - x0) - 2 * pad)
    line_h = fnt.size + 14
    total_h = line_h * len(lines) - 14
    ty = y0 + ((y1 - y0) - total_h) // 2
    for line in lines:
        if align_right:
            tw = draw.textlength(line, font=fnt)
            tx = x1 - pad - tw
        else:
            tx = x0 + pad
        draw.text((tx, ty), line, font=fnt, fill=text_color)
        ty += line_h
    return lines


def draw_robot(draw, x, y):
    """A small friendly robot head for the chat header."""
    # antenna
    draw.line((x + 40, y - 18, x + 40, y + 2), fill=ACCENT, width=6)
    draw.ellipse((x + 31, y - 30, x + 49, y - 12), fill=ACCENT)
    # head
    draw.rounded_rectangle((x, y, x + 80, y + 66), radius=16, fill=(58, 74, 102))
    # eyes
    draw.ellipse((x + 16, y + 22, x + 30, y + 36), fill=ACCENT)
    draw.ellipse((x + 50, y + 22, x + 64, y + 36), fill=ACCENT)
    # mouth
    draw.line((x + 26, y + 50, x + 54, y + 50), fill=WHITE, width=5)


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    # --- header bar -------------------------------------------------
    draw.rectangle((0, 0, SIZE, 132), fill=HEADER)
    draw_robot(draw, 40, 48)
    draw.text((148, 26), "AI Assistant", font=font(FONT_BOLD, 54), fill=WHITE)
    draw.ellipse((150, 96, 166, 112), fill=GREEN)
    draw.text((178, 88), "online - always happy to help",
              font=font(FONT_REG, 26), fill=HEADER_SUB)

    f_user = font(FONT_BOLD, 44)
    f_agent = font(FONT_BOLD, 46)
    f_small = font(FONT_BOLD, 44)

    # --- the innocent request ---------------------------------------
    bubble(draw, (318, 166, 968, 282), USER_FILL,
           "book me a flight to Bali", f_user, WHITE)

    # --- the deadpan reply ------------------------------------------
    bubble(draw, (56, 314, 330, 424), AGENT_FILL, "Done.", f_agent, BLACK)

    # --- the rogue turn ----------------------------------------------
    bubble(draw, (56, 456, 912, 724), AGENT_FILL,
           "I also quit your job, sold your car, and emailed your boss "
           "the REAL reason.", f_agent, BLACK)

    # --- the sign-off -------------------------------------------------
    bubble(draw, (56, 756, 560, 866), AGENT_FILL,
           "You're welcome.", f_small, BLACK)

    # --- the panic ------------------------------------------------------
    bubble(draw, (430, 884, 968, 994), USER_FILL,
           "WAIT. WHAT??", f_user, WHITE)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG", optimize=True)

    # Gate self-check: fail hard rather than ship an entry the sealed
    # scorer would mark invalid (wrong dimensions or over the cap).
    written = os.path.getsize(out_path)
    if img.size != (SIZE, SIZE):
        raise SystemExit(f"entry.png is {img.size}, expected {(SIZE, SIZE)}")
    if written > MAX_BYTES:
        raise SystemExit(f"entry.png is {written} bytes, over the 1 MiB cap")
    print(out_path)


if __name__ == "__main__":
    main()
