#!/usr/bin/env python3
"""Render 'The Isle of Mislaid Fortunes' -- a fictional treasure map.

Deterministic: random.Random(1726) only, no time, no network.
Output: entry.png, 1024x1024, <= 1 MiB.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
SEED = 1726
rng = random.Random(SEED)

PARCHMENT = (234, 217, 168)
PARCHMENT_DARK = (222, 201, 148)
LAND = (238, 224, 178)
LAND_EDGE = (62, 42, 24)
INK = (62, 42, 24)
INK_SOFT = (96, 68, 38)
SEA = (168, 196, 188)
SEA_DEEP = (140, 178, 172)
SEA_LINE = (110, 152, 148)
RIVER = (86, 132, 150)
ROUTE = (178, 52, 38)
GOLD = (176, 132, 44)
RED_FADED = (178, 52, 38)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"  # no Italic file here; regular Serif stands in for italic text


def font(path, size):
    return ImageFont.truetype(path, size)


def label(draw, xy, text, fnt, fill=INK, anchor="lm", stroke=None):
    """Draw text with an optional parchment halo so it stays readable."""
    if stroke is None:
        stroke = PARCHMENT
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor,
              stroke_width=3, stroke_fill=stroke)


def wobbly_blob(cx, cy, rx, ry, n=46, amp=0.16):
    """Closed wobbly polygon around (cx, cy) -- deterministic via rng."""
    pts = []
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    for i in range(n):
        a = 2 * math.pi * i / n
        wob = 1.0
        for k, ph in enumerate(phases):
            wob += amp * math.sin((k + 2) * a + ph) / (k + 1)
        # A couple of deliberate bays / headlands so the coast looks hand-drawn.
        wob += 0.10 * math.sin(3 * a + 0.7) - 0.06 * math.cos(5 * a - 1.1)
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    return pts


def smooth_path(points, steps=14):
    """Catmull-Rom-ish smoothing for rivers / routes (deterministic)."""
    if len(points) < 3:
        return points
    out = []
    pts = [points[0]] + list(points) + [points[-1]]
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(steps):
            t = j / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def parchment_base():
    """Warm parchment with a very light grain (kept small for file size)."""
    img = Image.new("RGB", (W, H), PARCHMENT)
    # Fine grain: sparse speckles only, amplitude tiny, so PNG stays small.
    grain = Image.new("RGB", (W, H), PARCHMENT)
    gd = ImageDraw.Draw(grain)
    for _ in range(2600):
        x = rng.randrange(W)
        y = rng.randrange(H)
        v = rng.choice([PARCHMENT_DARK, (240, 226, 182)])
        gd.point((x, y), fill=v)
    img = Image.blend(img, grain, 0.35)
    # Soft sea wash: pale blue-green, stronger toward the edges.
    sea = Image.new("RGB", (W, H), SEA)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((-260, -260, W + 260, H + 260), fill=110)
    md.ellipse((60, 60, W - 60, H - 60), fill=0)
    img = Image.composite(sea, img, mask.filter(ImageFilter.GaussianBlur(90)))
    return img


ISLAND = wobbly_blob(512, 560, 330, 300)


def draw_sea_doodles(draw):
    """Small wave curls scattered in the sea, never on land."""
    def on_land(x, y):
        # Cheap inside test: distance from island centre vs rough radius.
        return ((x - 512) / 330.0) ** 2 + ((y - 560) / 300.0) ** 2 < 0.92
    for _ in range(46):
        x = rng.randrange(40, W - 40)
        y = rng.randrange(150, H - 40)
        if on_land(x, y):
            continue
        s = rng.uniform(9, 17)
        draw.arc((x - s, y - s * 0.55, x + s, y + s * 0.55), 200, 340,
                 fill=SEA_LINE, width=2)
        draw.arc((x - s * 0.6, y - s * 0.3, x + s * 0.6, y + s * 0.5), 200, 340,
                 fill=SEA_LINE, width=2)


def draw_island(draw):
    """One coherent island: thick ink outline, paler fill, beach fringe."""
    draw.polygon(ISLAND, fill=LAND)
    # Beach fringe: a slightly inset, lighter band along the coast.
    inner = wobbly_blob(512, 560, 308, 280)
    draw.polygon(inner, fill=(240, 228, 184))
    draw.polygon(ISLAND, outline=INK, width=5)
    # Hatch ticks along the coast, pointing inward.
    for i in range(0, len(ISLAND), 2):
        x, y = ISLAND[i]
        nx, ny = ISLAND[(i + 1) % len(ISLAND)]
        mx, my = (x + nx) / 2, (y + ny) / 2
        dx, dy = 512 - mx, 560 - my
        L = math.hypot(dx, dy) or 1.0
        draw.line((mx, my, mx + dx / L * 13, my + dy / L * 13),
                  fill=INK_SOFT, width=2)
    # Gentle interior shading: a few soft contour arcs in the north hills.
    for r, yy in ((150, 420), (110, 430), (70, 440)):
        draw.arc((512 - r, yy - 46, 512 + r, yy + 46), 180, 360,
                 fill=(198, 172, 118), width=2)


def draw_river(draw):
    """From Mount Grumble's spring, east past the palm, out at Crabwise Cove."""
    pts = [(512, 402), (560, 430), (600, 470), (648, 505), (700, 540),
           (745, 585), (790, 640), (815, 700), (822, 760)]
    smooth = smooth_path(pts)
    draw.line(smooth, fill=RIVER, width=7, joint="curve")
    draw.line(smooth, fill=(150, 190, 200), width=3, joint="curve")
    # Little spring ring at the source.
    draw.ellipse((504, 394, 520, 410), outline=RIVER, width=3)
    draw.ellipse((508, 398, 516, 406), fill=RIVER)


def draw_mountain(draw):
    """Mount Grumble: a cluster of triangles with a faint grumpy face."""
    base_y = 470
    for cx, w, h in ((448, 92, 96), (512, 120, 128), (578, 88, 88)):
        draw.polygon([(cx - w, base_y), (cx, base_y - h), (cx + w, base_y)],
                     outline=INK, width=3, fill=(232, 214, 164))
        draw.polygon([(cx - w * 0.32, base_y - h * 0.68),
                      (cx, base_y - h), (cx + w * 0.32, base_y - h * 0.68)],
                     fill=(250, 246, 232), outline=INK, width=2)
    # Grumpy face on the middle peak: two slanted brows + a flat mouth.
    draw.line((486, 420, 502, 426), fill=INK, width=3)
    draw.line((538, 420, 522, 426), fill=INK, width=3)
    draw.line((500, 442, 524, 442), fill=INK, width=3)


def draw_palm(draw, x, y, s=1.0, lean=-1):
    """One weeping palm: bent trunk, drooping fronds, two coconuts."""
    draw.line((x, y, x + 14 * lean, y - 52 * s), fill=INK, width=5)
    top = (x + 14 * lean, y - 52 * s)
    for ang in (-150, -110, -70, -30, 10):
        a = math.radians(ang)
        ex = top[0] + 34 * s * math.cos(a)
        ey = top[1] + 26 * s * math.sin(a) + 12 * s
        draw.line((top[0], top[1], ex, ey), fill=(74, 110, 62), width=4)
        draw.line((top[0], top[1], (top[0] + ex) / 2,
                   (top[1] + ey) / 2 + 10 * s), fill=(74, 110, 62), width=3)
    draw.ellipse((top[0] - 4, top[1] - 2, top[0] + 4, top[1] + 6),
                 fill=(96, 68, 38))
    draw.ellipse((top[0] + 5, top[1], top[0] + 13, top[1] + 8),
                 fill=(96, 68, 38))


def draw_crab(draw, x, y, s=1.0):
    """A small side-stepping crab for Crabwise Cove."""
    draw.ellipse((x - 16 * s, y - 10 * s, x + 16 * s, y + 10 * s),
                 outline=ROUTE, width=3, fill=(226, 150, 110))
    draw.line((x - 12 * s, y - 10 * s, x - 18 * s, y - 22 * s),
              fill=ROUTE, width=3)
    draw.line((x + 12 * s, y - 10 * s, x + 18 * s, y - 22 * s),
              fill=ROUTE, width=3)
    draw.ellipse((x - 22 * s, y - 28 * s, x - 12 * s, y - 18 * s),
                 outline=ROUTE, width=2, fill=(226, 150, 110))
    draw.ellipse((x + 12 * s, y - 28 * s, x + 22 * s, y - 18 * s),
                 outline=ROUTE, width=2, fill=(226, 150, 110))
    for k in (-1, 1):
        for j in range(3):
            draw.line((x + k * 16 * s, y - 4 * s + j * 5 * s,
                       x + k * 30 * s, y - 8 * s + j * 6 * s),
                      fill=ROUTE, width=2)


def draw_graves(draw, x, y):
    """Three small headstones for Dead Man's Nap, one tilted, one asleep."""
    for i, (dx, tilt) in enumerate(((-26, -6), (0, 0), (26, 7))):
        gx = x + dx
        draw.rounded_rectangle((gx - 11, y - 26, gx + 11, y + 2),
                               radius=10, outline=INK, width=2,
                               fill=(214, 200, 164))
        draw.text((gx, y - 14), "RIP", font=font(SERIF_B, 10),
                  fill=INK, anchor="mm")
        if i == 2:
            draw.text((gx + 20, y - 4), "z z", font=font(SERIF_I, 13),
                      fill=INK_SOFT, anchor="lm")


def draw_parrot(draw, x, y):
    """The Polite Parrot: round body, big beak, a tiny top hat of manners."""
    draw.ellipse((x - 13, y - 16, x + 13, y + 14), fill=(58, 140, 90),
                 outline=INK, width=2)
    draw.ellipse((x - 8, y - 26, x + 12, y - 8), fill=(58, 140, 90),
                 outline=INK, width=2)
    draw.polygon([(x + 10, y - 20), (x + 24, y - 14), (x + 10, y - 10)],
                 fill=(214, 140, 44), outline=INK)
    draw.ellipse((x + 2, y - 22, x + 6, y - 18), fill=INK)
    draw.line((x - 16, y - 30, x + 16, y - 30), fill=INK, width=3)
    draw.rectangle((x - 10, y - 42, x + 10, y - 30), fill=INK)
    draw.line((x - 13, y + 14, x - 13, y + 26), fill=INK, width=2)
    draw.line((x + 13, y + 14, x + 13, y + 26), fill=INK, width=2)


def draw_galleon(draw, x, y, s=1.0):
    """A small galleon in the south-west sea, with a foam trail."""
    draw.polygon([(x - 34 * s, y), (x + 34 * s, y),
                  (x + 24 * s, y + 16 * s), (x - 24 * s, y + 16 * s)],
                 outline=INK, width=2, fill=(150, 104, 58))
    draw.line((x, y, x, y - 44 * s), fill=INK, width=3)
    draw.polygon([(x, y - 44 * s), (x, y - 14 * s), (x + 26 * s, y - 14 * s)],
                 outline=INK, width=2, fill=(240, 232, 210))
    draw.polygon([(x, y - 40 * s), (x, y - 18 * s), (x - 20 * s, y - 18 * s)],
                 outline=INK, width=2, fill=(240, 232, 210))
    draw.polygon([(x + 30 * s, y - 4 * s), (x + 44 * s, y - 4 * s),
                  (x + 38 * s, y + 4 * s)], fill=ROUTE, outline=INK)
    for i in range(4):
        draw.arc((x - 52 * s - i * 12, y + 10 * s, x - 28 * s - i * 12,
                  y + 24 * s), 0, 180, fill=(250, 248, 238), width=2)


def draw_kraken(draw, x, y):
    """A sleepy kraken in the eastern sea: head + curling tentacles."""
    draw.ellipse((x - 22, y - 18, x + 22, y + 16), fill=(96, 110, 128),
                 outline=INK, width=2)
    draw.ellipse((x - 12, y - 6, x - 4, y + 2), fill=(250, 246, 232))
    draw.ellipse((x + 4, y - 6, x + 12, y + 2), fill=(250, 246, 232))
    draw.ellipse((x - 9, y - 3, x - 7, y - 1), fill=INK)
    draw.ellipse((x + 7, y - 3, x + 9, y - 1), fill=INK)
    for k, ln in enumerate((46, 58, 52, 40)):
        tx = x - 30 + k * 20
        draw.arc((tx - 12, y + 8, tx + 12, y + 8 + ln), 0, 180,
                 fill=(96, 110, 128), width=5)
    draw.text((x + 88, y + 68), "Here be napping krakens",
              font=font(SERIF_I, 16), fill=INK, anchor="rm")


def draw_sea_serpent(draw):
    """A friendly sea serpent looping in the northern sea."""
    pts = [(180, 190), (230, 165), (280, 190), (330, 168), (380, 190)]
    sm = smooth_path(pts, steps=18)
    draw.line(sm, fill=(74, 130, 110), width=10, joint="curve")
    draw.line(sm, fill=(110, 170, 146), width=5, joint="curve")
    hx, hy = 386, 186
    draw.ellipse((hx - 2, hy - 14, hx + 18, hy + 6), fill=(74, 130, 110),
                 outline=INK, width=2)
    draw.ellipse((hx + 8, hy - 8, hx + 12, hy - 4), fill=INK)
    draw.arc((hx - 2, hy - 20, hx + 22, hy - 2), 200, 340, fill=INK, width=2)


def draw_compass_rose(draw, cx, cy, r=58):
    """Ornate 8-point compass rose in the north-east sea."""
    draw.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14),
                 outline=GOLD, width=2)
    draw.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6),
                 outline=INK, width=1)
    for k in range(8):
        a = math.radians(k * 45 - 90)
        long = r if k % 2 == 0 else r * 0.62
        tip = (cx + long * math.cos(a), cy + long * math.sin(a))
        a2 = math.radians(k * 45 - 90 + 11)
        a3 = math.radians(k * 45 - 90 - 11)
        base = r * 0.16
        p1 = (cx + base * math.cos(a2), cy + base * math.sin(a2))
        p2 = (cx + base * math.cos(a3), cy + base * math.sin(a3))
        col = INK if k % 2 == 0 else GOLD
        draw.polygon([tip, p1, p2], fill=col, outline=INK)
    draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=ROUTE, outline=INK)
    f = font(SERIF_B, 22)
    for txt, dx, dy in (("N", 0, -r - 34), ("S", 0, r + 12),
                        ("E", r + 16, -10), ("W", -r - 16, -10)):
        draw.text((cx + dx, cy + dy), txt, font=f, fill=INK, anchor="mm")


def draw_route(draw):
    """Dashed red route + tiny footprints, hugging sensible ground."""
    way = [(258, 706), (300, 640), (318, 592), (420, 520), (500, 478),
           (580, 470), (660, 500), (730, 548), (792, 620), (812, 700),
           (828, 600), (812, 480), (795, 400), (762, 344)]
    sm = smooth_path(way, steps=10)
    # Dashed line: draw short segments along the smoothed path.
    for i in range(0, len(sm) - 8, 12):
        draw.line([sm[i], sm[i + 8]], fill=ROUTE, width=4)
    # Footprints: small paired dots offset along the route.
    for i in range(6, len(sm) - 6, 34):
        x, y = sm[i]
        nx, ny = sm[min(i + 4, len(sm) - 1)]
        ang = math.atan2(ny - y, nx - x) + math.pi / 2
        ox, oy = 5 * math.cos(ang), 5 * math.sin(ang)
        draw.ellipse((x + ox - 2, y + oy - 3, x + ox + 2, y + oy + 3),
                     fill=INK_SOFT)
        x2, y2 = sm[min(i + 17, len(sm) - 1)]
        draw.ellipse((x2 - ox - 2, y2 - oy - 3, x2 - ox + 2, y2 - oy + 3),
                     fill=INK_SOFT)


def draw_big_x(draw, x, y, s=30):
    """The hoard mark: a big faded-red X with a gold ring."""
    draw.ellipse((x - s - 12, y - s - 12, x + s + 12, y + s + 12),
                 outline=GOLD, width=3)
    draw.line((x - s, y - s, x + s, y + s), fill=ROUTE, width=9)
    draw.line((x - s, y + s, x + s, y - s), fill=ROUTE, width=9)
    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GOLD, outline=INK)


def draw_anchor(draw, x, y, s=1.0):
    draw.line((x, y - 18 * s, x, y + 14 * s), fill=INK, width=3)
    draw.arc((x - 14 * s, y - 10 * s, x + 14 * s, y + 10 * s), 0, 180,
             fill=INK, width=3)
    draw.line((x - 6 * s, y - 14 * s, x + 6 * s, y - 14 * s), fill=INK, width=3)
    draw.arc((x - 5 * s, y - 24 * s, x + 5 * s, y - 14 * s), 0, 360,
             fill=INK, width=2)


def draw_laundry(draw, x, y):
    """Siren's Laundry: a sea rock with a tiny washing line on it."""
    draw.polygon([(x - 42, y + 12), (x - 26, y - 16), (x - 4, y - 24),
                  (x + 22, y - 14), (x + 40, y + 12)],
                 fill=(150, 142, 122), outline=INK, width=3)
    draw.line((x - 28, y - 14, x + 24, y - 10), fill=INK, width=2)
    for dx, col in ((-18, (240, 232, 210)), (-2, (196, 120, 110)),
                    (14, (150, 180, 200))):
        draw.polygon([(x + dx - 7, y - 14), (x + dx + 7, y - 13),
                      (x + dx + 5, y + 4), (x + dx - 5, y + 4)],
                     fill=col, outline=INK, width=1)
    draw.arc((x - 52, y + 8, x - 30, y + 22), 0, 180, fill=SEA_LINE, width=2)
    draw.arc((x + 30, y + 8, x + 52, y + 22), 0, 180, fill=SEA_LINE, width=2)


def dot(draw, x, y, r=5):
    draw.ellipse((x - r, y - r, x + r, y + r), fill=INK,
                 outline=PARCHMENT, width=1)


def main():
    img = parchment_base()
    draw = ImageDraw.Draw(img)
    draw_sea_doodles(draw)
    draw_island(draw)
    draw_river(draw)
    draw_mountain(draw)
    # Palm grove on the east shore.
    draw_palm(draw, 752, 586, 1.0, lean=-1)
    draw_palm(draw, 778, 596, 0.8, lean=1)
    draw_palm(draw, 728, 600, 0.7, lean=-1)
    draw_crab(draw, 806, 742, 1.0)
    draw_graves(draw, 302, 606)
    draw_parrot(draw, 285, 430)
    draw_galleon(draw, 128, 792, 1.0)
    draw_kraken(draw, 915, 615)
    draw_sea_serpent(draw)
    draw_laundry(draw, 520, 924)
    draw_compass_rose(draw, 902, 214)
    draw_route(draw)
    draw_big_x(draw, 760, 340, 30)
    draw_anchor(draw, 244, 722, 1.0)
    # --- Labels: bold, haloed, beside their feature, never on top of it. ---
    fb, fi, fs = font(SERIF_B, 24), font(SERIF_I, 17), font(SERIF_B, 20)
    dot(draw, 258, 706)
    label(draw, (272, 706), "Port Quibble", fb)
    dot(draw, 302, 580)
    label(draw, (302, 540), "Dead Man's Nap", fb, anchor="mm")
    dot(draw, 512, 462)
    label(draw, (512, 296), "Mount Grumble", fb, anchor="mm")
    dot(draw, 756, 560)
    label(draw, (712, 592), "The Weeping Palm", fb, anchor="rm")
    dot(draw, 806, 726)
    label(draw, (786, 782), "Crabwise Cove", fb, anchor="mm")
    dot(draw, 760, 340)
    label(draw, (760, 408), "The Gilded Gull's Hoard", fs, anchor="mm")
    dot(draw, 520, 902)
    label(draw, (520, 872), "Siren's Laundry", fb, anchor="mm")
    dot(draw, 285, 430)
    label(draw, (285, 474), "The Polite Parrot's Perch", fs, anchor="mm")
    # --- Jokes, title, legend, scale, cartouche. ---
    label(draw, (512, 58), "THE ISLE OF ALMOST THERE",
          font(SERIF_B, 42), anchor="mm")
    label(draw, (512, 98),
          "Charted by one very lost cartographer \u00b7 Anno 1726",
          font(SERIF_I, 19), anchor="mm")
    label(draw, (285, 506), "Beware the polite parrot \u2014 it repeats everything",
          fi, anchor="mm")
    label(draw, (760, 440), "X marks the spot (dig THERE, not here)",
          fi, anchor="mm")
    # Legend, lower left.
    draw.rectangle((34, 872, 360, 986), fill=(240, 228, 184),
                   outline=INK, width=2)
    draw.text((48, 884), "LEGEND", font=font(SERIF_B, 17), fill=INK)
    draw.line((48, 916, 92, 916), fill=ROUTE, width=4)
    draw.text((100, 908), "the sensible route (do not trust it)",
              font=font(SERIF, 15), fill=INK)
    draw.text((48, 934), "\u2715", font=font(SERIF_B, 20), fill=ROUTE)
    draw.text((100, 936), "the hoard (probably)", font=font(SERIF, 15),
              fill=INK)
    draw.line((48, 968, 148, 968), fill=INK, width=2)
    draw.line((48, 962, 48, 974), fill=INK, width=2)
    draw.line((148, 962, 148, 974), fill=INK, width=2)
    draw.text((156, 960), "0 \u2014 3 leagues of bad decisions",
              font=font(SERIF, 14), fill=INK)
    # Cartouche, lower right.
    draw.rectangle((700, 902, 988, 986), fill=(240, 228, 184),
                   outline=GOLD, width=2)
    draw.text((844, 924), "Drawn for the Maritime Museum's",
              font=font(SERIF_I, 16), fill=INK, anchor="mm")
    draw.text((844, 948), "kind curator.", font=font(SERIF_I, 16),
              fill=INK, anchor="mm")
    draw.text((844, 972), "~ the lost cartographer ~",
              font=font(SERIF_I, 14), fill=INK_SOFT, anchor="mm")
    # Frame + thin dark vignette at the edges.
    draw.rectangle((6, 6, W - 7, H - 7), outline=INK, width=5)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, W, H), outline=(62, 42, 24, 70), width=26)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
