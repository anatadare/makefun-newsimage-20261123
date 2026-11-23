#!/usr/bin/env python3
"""The World Today: Monday 23 November 2026.

A one-page newspaper front page drawn procedurally with the Python
standard library only. No network, no files read, fully deterministic:
running it twice writes byte-identical PNGs.

Stories (all verified from news reports of 23 Nov 2026):
  1. COP31 climate talks collapse in Antalya with no deal.
  2. Nepal PM Balendra Shah holds talks with PM Modi in Delhi.
  3. Indonesia candy-factory fire: 24 body bags found, search resumes.
  4. South Korea education minister resigns over AI exam cheating.
  5. India post a record 720/9 in the Wellington Test.
  6. UN talks on lethal autonomous weapons to continue.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
DARKBLUE = (18, 52, 96)
GREEN = (34, 120, 62)
ORANGE = (224, 110, 20)
GOLD = (212, 160, 23)
GREY = (110, 110, 110)
LIGHTGREY = (210, 205, 192)
SAFFRON = (255, 153, 51)
CREAM2 = (238, 231, 214)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, drawn by hand for this entry. 7 rows of 5 chars each.
FONT = {
    'A': (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    'B': ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    'C': (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    'D': ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    'E': ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    'F': ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    'G': (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    'H': ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    'I': ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    'J': ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    'K': ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    'L': ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    'M': ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    'N': ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    'O': (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    'P': ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    'Q': (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    'R': ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    'S': (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    'T': ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    'U': ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    'V': ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    'W': ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    'X': ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    'Y': ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    'Z': ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    '0': (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    '1': ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    '2': (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    '3': ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    '4': ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    '5': ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    '6': (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    '7': ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    '8': (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    '9': (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    ' ': ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    '.': ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ',': ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ':': ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ';': ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    '!': ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    '?': (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    '-': ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", "     ", "     ", "     ", "     ", "     "),
    '(': ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ')': ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    '%': ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    '&': (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    '$': ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    '+': ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    '=': ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    '/': ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
}

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)
for i in range(0, W * H * 3, 3):
    buf[i], buf[i + 1], buf[i + 2] = PAPER


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o], buf[o + 1], buf[o + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        for xx in range(x0, x1):
            buf[o], buf[o + 1], buf[o + 2] = c
            o += 3


def rect(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x0, x1, y, c, t=1):
    fill_rect(x0, y, x1 - x0, t, c)


def vline(x, y0, y1, c, t=1):
    fill_rect(x, y0, t, y1 - y0, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    if fill:
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                px(xx, yy, c)
    else:
        for a in range(360):
            import math
            px(int(cx + r * math.cos(math.radians(a))),
               int(cy + r * math.sin(math.radians(a))), c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    fill_rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_center(x0, x1, y, s, scale, c):
    w = text_width(s, scale)
    draw_text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    words = s.upper().split(' ')
    lines, cur = [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if text_width(t, scale) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, max_w, scale, c, lh=None):
    lh = lh or 9 * scale
    for ln in wrap(s, max_w, scale):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y

# ---------------------------------------------------------------- masthead
MX = 28
draw_text_center(MX, W - MX, 34, "THE WORLD TODAY", 8, INK)
hline(MX, W - MX, 128, INK, 4)
draw_text_center(MX, W - MX, 140, "MONDAY 23 NOVEMBER 2026", 3, RED)
draw_text(MX, 140, "NO. 327", 2, INK)
draw_text(W - MX - text_width("PRICE: ONE DAY", 2), 140, "PRICE: ONE DAY", 2, INK)
hline(MX, W - MX, 168, INK, 2)

# ================================================================ LEAD: COP31
LY = 182
# kicker
draw_text(MX, LY, "CLIMATE - ANTALYA, TURKIYE", 2, RED)
draw_text_center(MX, W - MX, LY + 22, "COP31 COLLAPSES", 5, INK)
draw_text_center(MX, W - MX, LY + 62, "NO DEAL IN ANTALYA", 4, RED)
# lead illustration: globe with crack + smokestacks, right side
GX, GY = 700, LY + 96
# smokestacks behind globe
fill_rect(GX - 150, GY + 30, 26, 100, GREY)
fill_rect(GX - 112, GY + 48, 26, 84, GREY)
fill_rect(GX - 150, GY + 22, 26, 10, INK)
fill_rect(GX - 112, GY + 40, 26, 10, INK)
# smoke puffs (kept low so they never touch the subhead)
for (sx, sy, sr) in [(GX - 137, GY + 8, 16), (GX - 99, GY + 26, 14)]:
    circle(sx, sy, sr, LIGHTGREY)
# globe
circle(GX, GY + 88, 46, BLUE)
# land blobs (green)
for (lx, ly, lr) in [(GX - 20, GY + 64, 14), (GX + 16, GY + 58, 11),
                     (GX - 6, GY + 110, 13), (GX + 24, GY + 104, 8),
                     (GX - 30, GY + 100, 7)]:
    circle(lx, ly, lr, GREEN)
# crack across the globe
line(GX - 42, GY + 58, GX - 14, GY + 82, INK, 3)
line(GX - 14, GY + 82, GX + 6, GY + 70, INK, 3)
line(GX + 6, GY + 70, GX + 34, GY + 100, INK, 3)
line(GX + 34, GY + 100, GX + 44, GY + 90, INK, 3)
# sun, dimmed
circle(GX + 118, GY + 30, 20, GOLD)
# deck text, left of illustration
para(MX, LY + 104, "EU and UK reject a pact silent on fossil fuels. The longest climate summit ever ends with no agreement after two weeks of talks.", 500, 2, INK)
para(MX, LY + 190, "Murat Kurum: No consensus. Australia: Very disappointing.", 500, 2, GREY)
hline(MX, W - MX, LY + 232, INK, 2)

# ================================================================ ROW 2
RY = LY + 246
COLW = (W - 2 * MX - 24) // 2
# ---- Nepal / Modi (left)
draw_text(MX, RY, "INDIA - NEW DELHI", 2, RED)
draw_text(MX, RY + 24, "SHAH MEETS MODI", 3, INK)
# two flags on poles (poles stop above the labels)
FX, FY = MX + 40, RY + 62
vline(FX, FY, FY + 68, INK, 3)
vline(FX + 210, FY, FY + 68, INK, 3)
# Nepal flag: crimson double pennant
fill_rect(FX + 3, FY + 2, 78, 34, RED)
fill_rect(FX + 3, FY + 38, 56, 30, RED)
draw_text(FX + 3, FY + 72, "NEPAL", 2, INK)
# India flag: saffron / white / green
fill_rect(FX + 213, FY + 2, 90, 20, SAFFRON)
fill_rect(FX + 213, FY + 22, 90, 20, PAPER)
fill_rect(FX + 213, FY + 42, 90, 20, GREEN)
rect(FX + 213, FY + 2, 90, 60, INK, 1)
circle(FX + 258, FY + 32, 9, BLUE)
draw_text(FX + 213, FY + 72, "INDIA", 2, INK)
para(MX, RY + 176, "Nepal PM Balendra Shah holds talks in Delhi on his first trip abroad as PM. Deals on energy, trade and roads.", COLW, 2, INK)
# ---- Indonesia fire (right)
RX = MX + COLW + 24
draw_text(RX, RY, "INDONESIA - BANTEN", 2, RED)
draw_text(RX, RY + 24, "24 BODIES FOUND", 3, INK)
# factory + flames (no smoke: it would cross the headline)
BX, BY = RX + 20, RY + 62
fill_rect(BX, BY + 46, 150, 62, GREY)
fill_rect(BX + 150, BY + 66, 60, 42, GREY)
rect(BX, BY + 46, 150, 62, INK, 2)
for wx in range(BX + 14, BX + 140, 34):
    fill_rect(wx, BY + 60, 18, 16, GOLD)
# flames
for (fx, fy, fh) in [(BX + 30, BY + 46, 44), (BX + 70, BY + 46, 58),
                     (BX + 110, BY + 46, 46), (BX + 165, BY + 66, 34)]:
    for k in range(fh):
        wdt = int(10 * (1 - k / fh)) + 2
        fill_rect(fx - wdt, fy - k, 2 * wdt, 2, ORANGE if k < fh // 2 else RED)
para(RX, RY + 176, "Search resumes today at the Banten candy factory after Saturday's blaze. About 30 workers still missing.", COLW, 2, INK)
hline(MX, W - MX, RY + 236, INK, 2)

# ================================================================ ROW 3
R3Y = RY + 250
# ---- Korea minister (left)
draw_text(MX, R3Y, "SOUTH KOREA - SEOUL", 2, RED)
draw_text(MX, R3Y + 24, "MINISTER QUITS", 3, INK)
# exam desk: paper + pencil + AI robot head
EX, EY = MX + 30, R3Y + 62
fill_rect(EX, EY + 30, 130, 84, PAPER)
rect(EX, EY + 30, 130, 84, INK, 2)
hline(EX + 12, EX + 118, EY + 52, INK, 2)
hline(EX + 12, EX + 100, EY + 70, GREY, 2)
hline(EX + 12, EX + 110, EY + 88, GREY, 2)
draw_text(EX + 12, EY + 96, "X", 2, RED)
# robot head
fill_rect(EX + 165, EY + 18, 74, 62, BLUE)
rect(EX + 165, EY + 18, 74, 62, INK, 2)
vline(EX + 202, EY + 2, EY + 18, INK, 3)
circle(EX + 202, EY, 5, RED)
fill_rect(EX + 180, EY + 36, 14, 14, PAPER)
fill_rect(EX + 210, EY + 36, 14, 14, PAPER)
draw_text(EX + 165, EY + 86, "AI", 3, RED)
para(MX, R3Y + 176, "Education chief Choi Kyo-jin resigns over AI cheating chaos at Korea's college exam. 111 cases caught.", COLW, 2, INK)
# ---- Cricket (right)
draw_text(RX, R3Y, "SPORT - WELLINGTON", 2, RED)
draw_text(RX, R3Y + 24, "INDIA 720/9", 3, INK)
# stumps + bat + ball
CX, CY = RX + 40, R3Y + 66
for sx in (CX, CX + 16, CX + 32):
    fill_rect(sx, CY + 30, 6, 62, GOLD)
fill_rect(CX - 4, CY + 24, 46, 6, GOLD)
# bat, angled
line(CX + 90, CY + 92, CX + 150, CY + 10, INK, 10)
line(CX + 150, CY + 10, CX + 168, CY - 8, INK, 6)
# red ball
circle(CX + 185, CY + 78, 16, RED)
circle(CX + 185, CY + 78, 16, INK, fill=False)
draw_text(RX + 215, CY + 8, "720/9", 4, RED)
para(RX, R3Y + 176, "Record total in Wellington: the highest Test score ever in New Zealand. Rahul 136, Pant 128.", COLW, 2, INK)
hline(MX, W - MX, R3Y + 236, INK, 2)

# ================================================================ FOOTER
FY = R3Y + 250
fill_rect(MX, FY, W - 2 * MX, 34, INK)
draw_text_center(MX, W - MX, FY + 8, "ALSO: UN TO KEEP TALKING ON KILLER ROBOTS", 2, PAPER)
draw_text_center(MX, W - MX, FY + 44,
                 "SIX STORIES THAT DEFINED MONDAY 23 NOVEMBER 2026", 2, INK)
draw_text_center(MX, W - MX, FY + 64,
                 "COP31 - NEPAL - INDONESIA - KOREA - CRICKET - UNITED NATIONS", 2, GREY)

# ---------------------------------------------------------------- save PNG
def save_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack(
            '>I', zlib.crc32(c) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


if __name__ == '__main__':
    out = os.path.join(os.environ.get('OUTPUT_DIR', '/output'), 'entry.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n = save_png(out)
    print('wrote %s (%d bytes)' % (out, n))
