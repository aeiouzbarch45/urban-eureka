#!/usr/bin/env python3
"""Generate schematic 2D elevation diagrams (SVG) for every facade style in the
Grand Commercial Facade Library, plus a browsable HTML gallery.

Pure standard library. Deterministic: each style's seed is derived from its id,
so re-running reproduces identical diagrams.
"""
import json
import os
import random
import hashlib
import html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source.json")
SVG_DIR = os.path.join(HERE, "svgs")
os.makedirs(SVG_DIR, exist_ok=True)

W, H = 600, 820
MARGIN = 60

ACCENT = {
    "Solar Shading & Louver Systems": "#2c6e8f",
    "Structural Exoskeletons & Grids": "#8a5a2b",
    "Massing & Volumetric Transformations": "#556b7a",
    "Modular & Pixelated Skins": "#6b5b95",
    "Perforated, Cultural & Biophilic Screens": "#4a7c59",
    "Double-Skin & Kinetic Envelopes": "#b5651d",
    "Sculptural & Parametric Signatures": "#9b3b6a",
    "Contemporary Material & Cladding Systems": "#5a6470",
    "Parametric & Computational Geometry": "#8454a8",
    "Organic & Biomimetic Façades": "#2e8b6f",
    "Adaptive & Intelligent Façades": "#1f7a8c",
    "Sustainable & Energy-Generating Façades": "#3a9d4e",
    "Traditional & Cultural Architectural Façades": "#a8632d",
    "High-Rise Architectural Expression": "#3d4a5c",
    "Minimalist & Contemporary Façades": "#6f7d8c",
    "Advanced Glazing Systems": "#3f7fae",
    "Experimental & Futuristic Façades": "#c0397b",
}

CATEGORY_PATTERN = {
    "Solar Shading & Louver Systems": "louvers",
    "Structural Exoskeletons & Grids": "exoskeleton",
    "Massing & Volumetric Transformations": "massing",
    "Modular & Pixelated Skins": "pixel",
    "Perforated, Cultural & Biophilic Screens": "perforated",
    "Double-Skin & Kinetic Envelopes": "doubleskin",
    "Sculptural & Parametric Signatures": "sculptural",
    "Contemporary Material & Cladding Systems": "cladding",
    "Parametric & Computational Geometry": "parametric",
    "Organic & Biomimetic Façades": "organic",
    "Adaptive & Intelligent Façades": "adaptive",
    "Sustainable & Energy-Generating Façades": "sustainable",
    "Traditional & Cultural Architectural Façades": "cultural",
    "High-Rise Architectural Expression": "highrise",
    "Minimalist & Contemporary Façades": "minimalist",
    "Advanced Glazing Systems": "glazing",
    "Experimental & Futuristic Façades": "futuristic",
}


def rng_for(style):
    h = hashlib.md5(style["id"].encode("utf-8")).hexdigest()
    return random.Random(int(h, 16))


def num(params, key, default, rng):
    v = params.get(key)
    if isinstance(v, list):
        if not v:
            return default
        x = v[rng.randint(0, len(v) - 1)]
        try:
            return float(x)
        except (TypeError, ValueError):
            return default
    if isinstance(v, (int, float)):
        return float(v)
    return default


def base_glass(el, x0, y0, bw, bh, accent, rng, floors, bays, op=0.55):
    """Glass body + mullion grid + floor lines."""
    el.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
              f'fill="url(#glass)" stroke="#9fb0bd" stroke-width="1.5"/>')
    sw = bh / floors
    bw_b = bw / bays
    for i in range(1, floors):
        yy = y0 + i * sw
        el.append(f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x0+bw:.1f}" y2="{yy:.1f}" '
                  f'stroke="{accent}" stroke-width="0.8" stroke-opacity="0.30"/>')
    for j in range(1, bays):
        xx = x0 + j * bw_b
        el.append(f'<line x1="{xx:.1f}" y1="{y0:.1f}" x2="{xx:.1f}" y2="{y0+bh:.1f}" '
                  f'stroke="{accent}" stroke-width="0.8" stroke-opacity="0.30"/>')


def frame(el, x0, y0, bw, bh, accent):
    el.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
              f'fill="none" stroke="{accent}" stroke-width="2.5"/>')


# --------------------------------------------------------------------------
# Pattern renderers. Each appends SVG to `el`, drawn over the glass body.
# --------------------------------------------------------------------------

def p_louvers(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 46))
    sw = bh / floors
    bid = s["id"].lower()
    if "horizontal" in bid or "brise" in bid or "veil" in bid or "stacked" in bid:
        # horizontal ledges / brise-soleil
        bays = max(3, int(bw / 70))
        bw_b = bw / bays
        for i in range(floors):
            yy = y0 + i * sw + sw * 0.15
            depth = 10 + rng.uniform(0, 8)
            for j in range(bays):
                xx = x0 + j * bw_b
                el.append(f'<rect x="{xx+3:.1f}" y="{yy:.1f}" width="{bw_b-6:.1f}" '
                          f'height="{sw*0.5:.1f}" fill="{accent}" fill-opacity="0.9"/>')
                el.append(f'<rect x="{xx+3:.1f}" y="{yy+sw*0.5:.1f}" width="{bw_b-6:.1f}" '
                          f'height="{depth:.1f}" fill="{accent}" fill-opacity="0.35"/>')
    elif "sawtooth" in bid:
        bays = max(4, int(bw / 55))
        bw_b = bw / bays
        for j in range(bays):
            xx = x0 + j * bw_b
            for i in range(floors):
                yy = y0 + i * sw
                d = 14
                el.append(f'<path d="M{xx:.1f} {yy+sw:.1f} L{xx+d:.1f} {yy+sw:.1f} '
                          f'L{xx:.1f} {yy:.1f} Z" fill="{accent}" fill-opacity="0.85"/>')
    elif "density" in bid:
        x = x0 + 6
        gap = 60
        while x < x0 + bw - 6:
            w = 6 + rng.uniform(0, 6)
            el.append(f'<rect x="{x:.1f}" y="{y0+4:.1f}" width="{w:.1f}" height="{bh-8:.1f}" '
                      f'fill="{accent}" fill-opacity="0.8"/>')
            gap = max(10, gap - rng.uniform(2, 6))
            x += w + gap
    else:  # vertical fins
        bays = max(4, int(bw / 60))
        bw_b = bw / bays
        for j in range(bays):
            xx = x0 + j * bw_b + bw_b * 0.5
            depth = 12 + rng.uniform(0, 10)
            el.append(f'<rect x="{xx-3:.1f}" y="{y0+4:.1f}" width="6" height="{bh-8:.1f}" '
                      f'fill="{accent}" fill-opacity="0.9"/>')
            el.append(f'<rect x="{xx+3:.1f}" y="{y0+4:.1f}" width="{depth:.1f}" height="{bh-8:.1f}" '
                      f'fill="{accent}" fill-opacity="0.25"/>')


def p_exoskeleton(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 50))
    bays = max(3, int(bw / 70))
    sw = bh / floors
    bw_b = bw / bays
    frame(el, x0, y0, bw, bh, accent)
    bid = s["id"].lower()
    if "diagrid" in bid:
        for i in range(floors):
            for j in range(bays):
                xa, ya = x0 + j * bw_b, y0 + i * sw
                xb, yb = xa + bw_b, ya + sw
                xc, yc = xa + bw_b, ya
                xd, yd = xa, ya + sw
                el.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" '
                          f'stroke="{accent}" stroke-width="2.2"/>')
                el.append(f'<line x1="{xc:.1f}" y1="{yc:.1f}" x2="{xd:.1f}" y2="{yd:.1f}" '
                          f'stroke="{accent}" stroke-width="2.2"/>')
    elif "truss" in bid:
        for i in range(floors):
            ya = y0 + i * sw
            pts = []
            x = x0
            up = True
            while x < x0 + bw:
                nx = min(x + bw_b, x0 + bw)
                yy = ya if up else ya + sw
                pts.append((nx, yy))
                up = not up
                x = nx
            d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in [(x0, ya + sw * 0.5)] + pts)
            el.append(f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="2"/>')
    elif "voronoi" in bid or "web" in bid:
        for _ in range(int(bays * floors * 1.6)):
            cx = x0 + rng.uniform(0, bw)
            cy = y0 + rng.uniform(0, bh)
            r = rng.uniform(8, 26)
            el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
                      f'stroke="{accent}" stroke-width="1.4" stroke-opacity="0.8"/>')
    elif "megacolumn" in bid or "outrigger" in bid:
        # perimeter megacolumns + belt trusses
        cols = max(2, bays // 2)
        for j in range(cols + 1):
            xx = x0 + (bw * j / cols)
            el.append(f'<rect x="{xx-7:.1f}" y="{y0:.1f}" width="14" height="{bh:.1f}" '
                      f'fill="{accent}" fill-opacity="0.9"/>')
        for i in (0.33, 0.66):
            yy = y0 + bh * i
            el.append(f'<rect x="{x0:.1f}" y="{yy-6:.1f}" width="{bw:.1f}" height="12" '
                      f'fill="{accent}" fill-opacity="0.7"/>')
    else:  # vierendeel / rectangular grid
        for i in range(floors + 1):
            yy = y0 + i * sw
            el.append(f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x0+bw:.1f}" y2="{yy:.1f}" '
                      f'stroke="{accent}" stroke-width="2"/>')
        for j in range(bays + 1):
            xx = x0 + j * bw_b
            el.append(f'<line x1="{xx:.1f}" y1="{y0:.1f}" x2="{xx:.1f}" y2="{y0+bh:.1f}" '
                      f'stroke="{accent}" stroke-width="2"/>')


def p_massing(el, s, rng, x0, y0, bw, bh, accent):
    tiers = rng.randint(2, 3)
    cur_w = bw
    cur_x = x0
    cur_y = y0
    tier_h = bh / tiers
    for t in range(tiers):
        el.append(f'<rect x="{cur_x:.1f}" y="{cur_y:.1f}" width="{cur_w:.1f}" height="{tier_h:.1f}" '
                  f'fill="url(#glass)" stroke="{accent}" stroke-width="2"/>')
        # window grid on the tier
        nf = max(3, int(tier_h / 40))
        nb = max(3, int(cur_w / 55))
        for i in range(1, nf):
            yy = cur_y + i * (tier_h / nf)
            el.append(f'<line x1="{cur_x:.1f}" y1="{yy:.1f}" x2="{cur_x+cur_w:.1f}" y2="{yy:.1f}" '
                      f'stroke="{accent}" stroke-width="0.7" stroke-opacity="0.4"/>')
        for j in range(1, nb):
            xx = cur_x + j * (cur_w / nb)
            el.append(f'<line x1="{xx:.1f}" y1="{cur_y:.1f}" x2="{xx:.1f}" y2="{cur_y+tier_h:.1f}" '
                      f'stroke="{accent}" stroke-width="0.7" stroke-opacity="0.4"/>')
        # setback
        shrink = cur_w * rng.uniform(0.15, 0.3)
        cur_w -= shrink
        cur_x += shrink / 2
        cur_y += tier_h


def p_pixel(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 38))
    bays = max(4, int(bw / 52))
    sw = bh / floors
    bw_b = bw / bays
    palette = [accent, "#ffffff", "#d9e2ea", accent]
    for i in range(floors):
        for j in range(bays):
            if rng.random() < 0.18:
                continue
            inset = rng.uniform(0, 4)
            c = palette[rng.randint(0, len(palette) - 1)]
            op = rng.uniform(0.45, 0.95)
            el.append(f'<rect x="{x0+j*bw_b+inset:.1f}" y="{y0+i*sw+inset:.1f}" '
                      f'width="{bw_b-2*inset:.1f}" height="{sw-2*inset:.1f}" '
                      f'fill="{c}" fill-opacity="{op:.2f}" stroke="{accent}" stroke-width="0.6"/>')


def p_perforated(el, s, rng, x0, y0, bw, bh, accent):
    bid = s["id"].lower()
    if "cultural" in bid or "biophilic" in bid:
        # lattice of diamonds
        step = 34
        for yy in range(int(y0), int(y0 + bh), step):
            for xx in range(int(x0), int(x0 + bw), step):
                cx = xx + step / 2
                cy = yy + step / 2
                el.append(f'<path d="M{cx:.1f} {cy-step/2:.1f} L{cx+step/2:.1f} {cy:.1f} '
                          f'L{cx:.1f} {cy+step/2:.1f} L{cx-step/2:.1f} {cy:.1f} Z" '
                          f'fill="none" stroke="{accent}" stroke-width="1.6"/>')
    else:
        # dot screen
        step = 22
        r = 5
        for yy in range(int(y0 + step), int(y0 + bh), step):
            for xx in range(int(x0 + step), int(x0 + bw), step):
                el.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{r}" '
                          f'fill="{accent}" fill-opacity="0.7"/>')


def p_doubleskin(el, s, rng, x0, y0, bw, bh, accent):
    gap = 18
    # inner skin
    base_glass(el, x0, y0, bw, bh, accent, rng, max(8, int(bh / 42)), max(4, int(bw / 60)), op=0.4)
    # outer skin (lighter)
    el.append(f'<rect x="{x0-gap:.1f}" y="{y0-gap:.1f}" width="{bw+2*gap:.1f}" height="{bh+2*gap:.1f}" '
              f'fill="#cfe0ec" fill-opacity="0.25" stroke="{accent}" stroke-width="1.4" stroke-opacity="0.7"/>')
    # kinetic fins on outer skin
    floors = max(8, int(bh / 44))
    sw = (bh + 2 * gap) / floors
    for i in range(floors):
        yy = y0 - gap + i * sw + sw * 0.5
        ang = rng.uniform(-25, 25)
        el.append(f'<line x1="{x0-gap:.1f}" y1="{yy:.1f}" x2="{x0-gap+ang:.1f}" y2="{yy-10:.1f}" '
                  f'stroke="{accent}" stroke-width="2.2"/>')
        el.append(f'<line x1="{x0+bw+gap:.1f}" y1="{yy:.1f}" x2="{x0+bw+gap+ang:.1f}" y2="{yy-10:.1f}" '
                  f'stroke="{accent}" stroke-width="2.2"/>')


def p_sculptural(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 50))
    bays = max(4, int(bw / 60))
    sw = bh / floors
    bw_b = bw / bays
    for j in range(bays):
        xa = x0 + j * bw_b
        xb = xa + bw_b
        xm = (xa + xb) / 2
        amp = rng.uniform(6, 22)
        phase = rng.uniform(0, 3.14)
        d = f"M{xa:.1f} {y0+bh:.1f} "
        n = floors
        for i in range(n + 1):
            yy = y0 + bh - i * sw
            off = amp * (0.5 + 0.5 * __import__("math").sin(phase + i * 0.5))
            d += f"Q{xm+off:.1f} {yy+sw/2:.1f} {xb if i % 2 == 0 else xa:.1f} {yy:.1f} "
        el.append(f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="2.2"/>')
    frame(el, x0, y0, bw, bh, accent)


def p_cladding(el, s, rng, x0, y0, bw, bh, accent):
    base_glass(el, x0, y0, bw, bh, accent, rng, 1, 1, op=0.3)
    # large material panels
    nf = rng.randint(3, 5)
    nb = rng.randint(3, 6)
    sw = bh / nf
    bw_b = bw / nb
    for i in range(nf):
        for j in range(nb):
            c = accent if (i + j) % 2 == 0 else "#e7edf2"
            el.append(f'<rect x="{x0+j*bw_b+2:.1f}" y="{y0+i*sw+2:.1f}" '
                      f'width="{bw_b-4:.1f}" height="{sw-4:.1f}" fill="{c}" fill-opacity="0.55" '
                      f'stroke="#ffffff" stroke-width="1.2"/>')


def p_parametric(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 44))
    bays = max(4, int(bw / 56))
    sw = bh / floors
    bw_b = bw / bays
    for i in range(floors):
        for j in range(bays):
            xa, ya = x0 + j * bw_b, y0 + i * sw
            if (i + j) % 2 == 0:
                el.append(f'<path d="M{xa:.1f} {ya:.1f} L{xa+bw_b:.1f} {ya:.1f} L{xa:.1f} {ya+sw:.1f} Z" '
                          f'fill="{accent}" fill-opacity="0.5" stroke="{accent}" stroke-width="0.8"/>')
            else:
                el.append(f'<path d="M{xa+bw_b:.1f} {ya:.1f} L{xa+bw_b:.1f} {ya+sw:.1f} L{xa:.1f} {ya+sw:.1f} Z" '
                          f'fill="{accent}" fill-opacity="0.5" stroke="{accent}" stroke-width="0.8"/>')


def p_organic(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(6, int(bh / 50))
    sw = bh / floors
    bays = max(4, int(bw / 60))
    bw_b = bw / bays
    for j in range(bays):
        xa = x0 + j * bw_b
        xb = xa + bw_b
        xm = (xa + xb) / 2
        d = f"M{xa:.1f} {y0:.1f} "
        for i in range(floors + 1):
            yy = y0 + i * sw
            bulge = rng.uniform(4, 14) * (1 if i % 2 == 0 else -1)
            d += f"Q{xm+bulge:.1f} {yy-sw/2:.1f} {xb if i%2==0 else xa:.1f} {yy:.1f} "
        el.append(f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="2.4"/>')
        # leaf/bubble nodes
        for i in range(floors):
            yy = y0 + i * sw + sw / 2
            el.append(f'<circle cx="{xm:.1f}" cy="{yy:.1f}" r="4" fill="{accent}"/>')
    frame(el, x0, y0, bw, bh, accent)


def p_adaptive(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(8, int(bh / 40))
    bays = max(4, int(bw / 50))
    sw = bh / floors
    bw_b = bw / bays
    for i in range(floors):
        yy = y0 + i * sw
        ang = -35 + 70 * (i / max(1, floors - 1))  # gradient of angles
        for j in range(bays):
            xa = x0 + j * bw_b + 3
            w = bw_b - 6
            el.append(f'<rect x="{xa:.1f}" y="{yy+sw*0.2:.1f}" width="{w:.1f}" height="{sw*0.5:.1f}" '
                      f'fill="{accent}" fill-opacity="0.85" transform="rotate({ang:.1f} {xa+w/2:.1f} {yy+sw*0.45:.1f})"/>')


def p_sustainable(el, s, rng, x0, y0, bw, bh, accent):
    base_glass(el, x0, y0, bw, bh, accent, rng, max(8, int(bh / 42)), max(4, int(bw / 55)), op=0.4)
    # PV panels upper portion
    pv_y = y0
    pv_h = bh * 0.55
    nf = 4
    nb = max(4, int(bw / 45))
    sw = pv_h / nf
    bw_b = bw / nb
    for i in range(nf):
        for j in range(nb):
            el.append(f'<rect x="{x0+j*bw_b+2:.1f}" y="{pv_y+i*sw+2:.1f}" width="{bw_b-4:.1f}" '
                      f'height="{sw-4:.1f}" fill="#1b3a5b" fill-opacity="0.85" '
                      f'stroke="#0d2236" stroke-width="0.8"/>')
    # green planters lower portion
    gy = y0 + pv_h
    nb2 = max(3, int(bw / 70))
    bw_b2 = bw / nb2
    for j in range(nb2):
        el.append(f'<rect x="{x0+j*bw_b2+4:.1f}" y="{gy:.1f}" width="{bw_b2-8:.1f}" '
                  f'height="{bh-pv_h-6:.1f}" fill="#3a9d4e" fill-opacity="0.7" '
                  f'stroke="#2c7a3a" stroke-width="1"/>')


def p_cultural(el, s, rng, x0, y0, bw, bh, accent):
    step = 40
    for yy in range(int(y0), int(y0 + bh) - step, step):
        for xx in range(int(x0), int(x0 + bw) - step, step):
            el.append(f'<rect x="{xx+6:.1f}" y="{yy+6:.1f}" width="{step-12:.1f}" height="{step-12:.1f}" '
                      f'fill="none" stroke="{accent}" stroke-width="2" '
                      f'transform="rotate(45 {xx+step/2:.1f} {yy+step/2:.1f})"/>')
            el.append(f'<circle cx="{xx+step/2:.1f}" cy="{yy+step/2:.1f}" r="4" fill="{accent}"/>')
    frame(el, x0, y0, bw, bh, accent)


def p_highrise(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(14, int(bh / 30))
    bays = max(4, int(bw / 55))
    base_glass(el, x0, y0, bw, bh, accent, rng, floors, bays, op=0.5)
    frame(el, x0, y0, bw, bh, accent)
    # crown
    cx = x0 + bw / 2
    cy = y0
    el.append(f'<path d="M{x0:.1f} {cy:.1f} L{cx:.1f} {cy-60:.1f} L{x0+bw:.1f} {cy:.1f} Z" '
              f'fill="{accent}" fill-opacity="0.85"/>')
    el.append(f'<line x1="{cx:.1f}" y1="{cy-60:.1f}" x2="{cx:.1f}" y2="{cy-110:.1f}" '
              f'stroke="{accent}" stroke-width="2"/>')


def p_minimalist(el, s, rng, x0, y0, bw, bh, accent):
    el.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
              f'fill="url(#glass)" stroke="{accent}" stroke-width="1.5"/>')
    # very few thin mullions
    for j in range(1, 4):
        xx = x0 + bw * j / 4
        el.append(f'<line x1="{xx:.1f}" y1="{y0:.1f}" x2="{xx:.1f}" y2="{y0+bh:.1f}" '
                  f'stroke="{accent}" stroke-width="0.8" stroke-opacity="0.4"/>')
    # entrance
    ew = bw * 0.25
    ex = x0 + (bw - ew) / 2
    el.append(f'<rect x="{ex:.1f}" y="{y0+bh-50:.1f}" width="{ew:.1f}" height="50" '
              f'fill="{accent}" fill-opacity="0.6"/>')


def p_glazing(el, s, rng, x0, y0, bw, bh, accent):
    floors = max(10, int(bh / 34))
    bays = max(6, int(bw / 38))
    base_glass(el, x0, y0, bw, bh, accent, rng, floors, bays, op=0.6)
    frame(el, x0, y0, bw, bh, accent)


def p_futuristic(el, s, rng, x0, y0, bw, bh, accent):
    # curved / angled mass
    dirn = rng.choice([-1, 1])
    el.append(f'<path d="M{x0:.1f} {y0+bh:.1f} L{x0:.1f} {y0+40:.1f} '
              f'Q{x0+bw/2:.1f} {y0-30:.1f} {x0+bw:.1f} {y0+40:.1f} L{x0+bw:.1f} {y0+bh:.1f} Z" '
              f'fill="url(#glass)" stroke="{accent}" stroke-width="2"/>')
    # dynamic ribs
    for i in range(1, 10):
        t = i / 10
        yy = y0 + bh * t
        el.append(f'<path d="M{x0:.1f} {yy:.1f} Q{x0+bw/2+dirn*20:.1f} {yy-15:.1f} {x0+bw:.1f} {yy:.1f}" '
                  f'fill="none" stroke="{accent}" stroke-width="1.6" stroke-opacity="0.8"/>')


PATTERNS = {
    "louvers": p_louvers,
    "exoskeleton": p_exoskeleton,
    "massing": p_massing,
    "pixel": p_pixel,
    "perforated": p_perforated,
    "doubleskin": p_doubleskin,
    "sculptural": p_sculptural,
    "cladding": p_cladding,
    "parametric": p_parametric,
    "organic": p_organic,
    "adaptive": p_adaptive,
    "sustainable": p_sustainable,
    "cultural": p_cultural,
    "highrise": p_highrise,
    "minimalist": p_minimalist,
    "glazing": p_glazing,
    "futuristic": p_futuristic,
}


def render(style):
    rng = rng_for(style)
    accent = ACCENT.get(style["category"], "#54616e")
    el = []
    # sky
    el.append('<defs>'
              '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
              '<stop offset="0" stop-color="#f7fafc"/>'
              '<stop offset="1" stop-color="#e9eef3"/></linearGradient>'
              '<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">'
              f'<stop offset="0" stop-color="#dbe7f0"/>'
              f'<stop offset="1" stop-color="#c2d4e1"/></linearGradient>'
              '</defs>')
    el.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#sky)"/>')
    # determine mass geometry
    cat = style["category"]
    if cat == "High-Rise Architectural Expression":
        bw = W - 2 * MARGIN - rng.randint(40, 110)
        bh = H - 2 * MARGIN - 120  # leave crown room
    elif cat in ("Massing & Volumetric Transformations", "Experimental & Futuristic Façades"):
        bw = W - 2 * MARGIN - rng.randint(0, 60)
        bh = H - 2 * MARGIN - rng.randint(0, 40)
    else:
        bw = W - 2 * MARGIN
        bh = H - 2 * MARGIN
    x0 = (W - bw) / 2
    y0 = MARGIN
    ground_y = y0 + bh

    # ground
    el.append(f'<line x1="20" y1="{ground_y+2:.1f}" x2="{W-20}" y2="{ground_y+2:.1f}" '
              f'stroke="#9aa7b2" stroke-width="2"/>')
    el.append(f'<rect x="20" y="{ground_y+2:.1f}" width="{W-40}" height="6" fill="#cdd6de"/>')

    pat = CATEGORY_PATTERN.get(cat, "glazing")
    PATTERNS[pat](el, style, rng, x0, y0, bw, bh, accent)

    # caption
    name = html.escape(style["name"])
    catname = html.escape(style["category"])
    el.append(f'<text x="{W/2:.0f}" y="{H-34:.0f}" text-anchor="middle" '
              f'font-family="Helvetica,Arial,sans-serif" font-size="15" font-weight="700" '
              f'fill="#1d2a35">{name}</text>')
    el.append(f'<text x="{W/2:.0f}" y="{H-16:.0f}" text-anchor="middle" '
              f'font-family="Helvetica,Arial,sans-serif" font-size="11" fill="#5d6b78">{catname}</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-label="{name}">'
           + "".join(el) + '</svg>')
    return svg


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    styles = data["commercial_facade_styles"]
    cards = []
    for s in styles:
        svg = render(s)
        fn = f"svgs/{s['id']}.svg"
        with open(os.path.join(HERE, fn), "w", encoding="utf-8") as f:
            f.write(svg)
        params = s.get("parameters", {})
        cards.append({
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "intent": s.get("architectural_intent", ""),
            "elements": s.get("archicad_elements", []),
            "parameters": params,
            "build_logic": s.get("tapir_build_logic", ""),
            "svg": fn,
        })
    with open(os.path.join(HERE, "styles.json"), "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=1)
    print(f"Generated {len(cards)} SVG elevations -> {SVG_DIR}")
    # categories for filter
    cats = sorted({c["category"] for c in cards})
    print(f"Categories: {len(cats)}")


if __name__ == "__main__":
    main()
