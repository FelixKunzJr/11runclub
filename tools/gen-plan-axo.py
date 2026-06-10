#!/usr/bin/env python3
"""Generator v3: ENTER Technikwelt nach Beschreibung des Clubs (Juni 2026).

- Rampe liegt auf der NORDSEITE (= Front der Zeichnung) als Kehren-Rampe:
  Einstieg Nordseite links, 2 Rechtskurven (Kehren an den Gebaeudeenden),
  Ankunft auf dem Dach am ANDEREN Ende, wieder Nordseite.
- Gebaeudeecken OHNE Radius.
- Dach: Wohnblock (Quader) an der SUEDseite, Treppenzylinder noerdlich-mittig,
  Parkfelder dazwischen, ENTER-Schriftzug an der Nordkante.
- Route: rauf -> eine Runde auf dem Dach -> gestrichelt dieselbe Rampe runter
  -> zurueck zur Wechselzone (Puls dort).
"""
import math, re, json

COS = math.cos(math.radians(30))
SIN = 0.5
S = 40.0
EXZ = 1.45

def P(x, y, z):
    return ((x - y) * COS * S, (x + y) * SIN * S - z * S * EXZ)

def fmt(p):
    return f"{p[0]:.1f},{p[1]:.1f}"

def path(pts3, closed=False):
    d = "M" + " L".join(fmt(P(*p)) for p in pts3)
    return d + (" Z" if closed else "")

def seg(a, b):
    return path([a, b])

def plen(pts3):
    pts = [P(*p) for p in pts3]
    return sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1))

def ease(t):
    return t * t * (3 - 2 * t)

L, W = 16.0, 13.0
Z1, Z2, Z3 = 1.35, 2.65, 3.95   # Podesthoehen der drei Rampenlaeufe
RAIL = 0.3

bld_main, bld_grid, bld_hidden = [], [], []
ramp, deck, ground, railing, clad, pav, sign, arcade = [], [], [], [], [], [], [], []
extra_svg = []

# ---------- Silhouette (scharfe Ecken) ----------
bld_main += [
    seg((0, W, 0), (0, W, Z3)),
    seg((L, W, 0), (L, W, Z3)),
    seg((L, 0, 0), (L, 0, Z3)),
    path([(0, W, 0), (L, W, 0), (L, 0, 0)]),
    path([(0, W, Z3), (L, W, Z3), (L, 0, Z3), (0, 0, Z3)], closed=True),
]
bld_hidden += [
    seg((0, 0, 0), (0, 0, Z3)),
    seg((0, 0, 0), (L, 0, 0)),
    seg((0, 0, 0), (0, W, 0)),
]
for z in (Z1, Z2):
    bld_hidden.append(path([(0, W, z), (0, 0, z), (L, 0, z)]))

# ---------- Slab-Fascia-Baender ----------
for z in (Z1, Z2, Z3):
    for dz in (0.0, -0.22):
        bld_grid.append(path([(0, W + 0.02, z + dz), (L + 0.02, W + 0.02, z + dz), (L + 0.02, 0, z + dz)]))

# ---------- Stuetzen ----------
for x in range(0, 17, 2):
    bld_grid.append(seg((x, W + 0.02, 0), (x, W + 0.02, Z3)))
for y in range(1, 13, 2):
    bld_grid.append(seg((L + 0.02, y, 0), (L + 0.02, y, Z3)))

# ---------- EG: offener Saeulengang Nordseite ----------
arcade.append(seg((0, W - 1.8, 0), (L, W - 1.8, 0)))
arcade.append(seg((0, W - 1.8, Z1 - 0.22), (L, W - 1.8, Z1 - 0.22)))
for x in range(1, 16, 2):
    arcade.append(seg((x, W - 1.8, 0), (x, W - 1.8, Z1 - 0.22)))

# ---------- Wellblech-Bays ----------
def clad_front(x0, x1, z0, z1, step=0.3):
    x = x0 + step
    while x < x1 - 0.05:
        clad.append(seg((x, W - 0.35, z0 + 0.08), (x, W - 0.35, z1 - 0.26)))
        x += step
def clad_right(y0, y1, z0, z1, step=0.3):
    y = y0 + step
    while y < y1 - 0.05:
        clad.append(seg((L - 0.35, y, z0 + 0.08), (L - 0.35, y, z1 - 0.26)))
        y += step
for (a, b) in ((0, 4), (6, 10), (12, 16)):
    clad_front(a, b, Z1, Z2)
for (a, b) in ((2, 6), (10, 14)):
    clad_front(a, b, Z2, Z3)
for (a, b) in ((1, 5), (7, 12)):
    clad_right(a, b, 0.2, Z1)
for (a, b) in ((1, 6), (8, 12)):
    clad_right(a, b, Z1, Z2)
for (a, b) in ((3, 10),):
    clad_right(a, b, Z2, Z3)

# ---------- Gelaender Dachrand ----------
railing.append(path([(0, W, Z3 + RAIL), (L, W, Z3 + RAIL), (L, 0, Z3 + RAIL)]))
for x in range(0, 17):
    railing.append(seg((x, W, Z3), (x, W, Z3 + RAIL)))
for y in range(0, 13):
    railing.append(seg((L, y, Z3), (L, y, Z3 + RAIL)))

# ---------- Kehren-Rampe Nordseite ----------
# Drei Laeufe an der Nordfassade (leicht unterschiedliche Tiefe),
# Kehren buegeln als Halbkreis ueber die Gebaeudeenden hinaus.
YA, YB = 0.42, -0.55          # Tiefen-Offsets der Laeufe relativ zu W (aussen / innen)
def run_x(yoff, x0, x1, z0, z1, n=26):
    return [(x0 + (x1 - x0) * i / n, W + yoff, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def hairpin(end, yo_from, yo_to, z0, z1, n=14):
    """Halbkreis-Kehre ueber das Gebaeudeende hinaus (end: 'right'/'left')."""
    cy = W + (yo_from + yo_to) / 2
    r = abs(yo_from - yo_to) / 2
    cx = (L - 0.1) if end == 'right' else 0.1
    pts = []
    for i in range(n + 1):
        a = math.pi * i / n
        dx = math.sin(a) * 1.1 * r          # Bauch ueber das Ende hinaus
        x = cx + dx if end == 'right' else cx - dx
        y = cy + (yo_from - yo_to) / 2 * math.cos(a)
        pts.append((x, y, z0 + (z1 - z0) * i / n))
    return pts

def switchback(off):
    pts = []
    pts += run_x(YA + off, 0.6, L - 0.9, 0.05, Z1)
    pts += hairpin('right', YA + off, YB - off, Z1, Z1 + 0.22)
    pts += run_x(YB - off, L - 0.9, 0.9, Z1 + 0.22, Z2)
    pts += hairpin('left', YB - off, YA + off, Z2, Z2 + 0.22)
    pts += run_x(YA + off, 0.9, L - 0.6, Z2 + 0.22, Z3)
    return pts

band = switchback(0.0)
ramp.append(path(band))
ramp.append(path([(x, y, z - 0.2) for (x, y, z) in band]))

# ---------- Dach-Layout ----------
# Wohnblock (Quader) an der SUEDseite
BX0, BX1, BY0, BY1, BH = 2.0, 12.5, 0.7, 2.9, 1.05
pav.append(path([(BX0, BY0, Z3 + BH), (BX1, BY0, Z3 + BH), (BX1, BY1, Z3 + BH), (BX0, BY1, Z3 + BH)], closed=True))
pav.append(path([(BX0, BY1, Z3), (BX1, BY1, Z3), (BX1, BY0, Z3)]))
for (xx, yy) in ((BX0, BY1), (BX1, BY1), (BX1, BY0)):
    pav.append(seg((xx, yy, Z3), (xx, yy, Z3 + BH)))
x = BX0 + 0.5
while x < BX1 - 0.2:
    pav.append(seg((x, BY1, Z3 + 0.06), (x, BY1, Z3 + BH - 0.06)))
    x += 0.55

# Treppenzylinder noerdlich, mittig
def drum(cx0, cy0, r, z0, z1, n=22):
    top = [(cx0 + r * math.cos(2 * math.pi * i / n), cy0 + r * math.sin(2 * math.pi * i / n), z1) for i in range(n + 1)]
    deck.append(path(top))
    deck.append(seg((cx0 - r, cy0, z0), (cx0 - r, cy0, z1)))
    deck.append(seg((cx0 + r, cy0, z0), (cx0 + r, cy0, z1)))
    front = [(cx0 + r * math.cos(math.pi + math.pi * i / n), cy0 + r * math.sin(math.pi + math.pi * i / n), z0) for i in range(n + 1)]
    deck.append(path(front))
drum(8.0, W - 2.9, 1.1, Z3, Z3 + 0.9)

# Parkfelder mittig
for i in range(8):
    x = 2.6 + i * 1.3
    deck.append(seg((x, 4.0, Z3), (x, 6.6, Z3)))
deck.append(seg((2.6, 4.0, Z3), (2.6 + 7 * 1.3, 4.0, Z3)))
deck.append(seg((2.6, 6.6, Z3), (2.6 + 7 * 1.3, 6.6, Z3)))
def box_top(x0, y0, x1, y1, z):
    return path([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], closed=True)
deck.append(box_top(5.2, 4.3, 6.1, 6.2, Z3 + 0.16))
deck.append(box_top(5.4, 4.75, 5.9, 5.8, Z3 + 0.34))

# ENTER-Schriftzug Nordkante (links, ueber dem Gelaender)
sx, sy = P(5.8, W - 0.25, Z3 + 1.15)
sign.append(seg((5.5, W - 0.25, Z3 + RAIL), (5.5, W - 0.25, Z3 + 1.0)))
sign.append(seg((12.0, W - 0.25, Z3 + RAIL), (12.0, W - 0.25, Z3 + 1.0)))
sign.append(seg((5.5, W - 0.25, Z3 + 1.0), (12.0, W - 0.25, Z3 + 1.0)))
extra_svg.append(
    f'<text x="{sx:.1f}" y="{sy:.1f}" class="pl-sign" transform="rotate(30 {sx:.1f} {sy:.1f})">ENTER TECHNIKWELT</text>')

# ---------- Vorplatz ----------
for i in range(4):
    g = 1.4 + i * 1.1
    ground.append(seg((0.0, W + g, 0), (L * 0.7, W + g, 0)))
for i in range(5):
    gx = 1.0 + i * 2.5
    ground.append(seg((gx, W + 1.4, 0), (gx, W + 4.6, 0)))

# ---------- Route ----------
ROFF = 0.28   # leicht vor dem Rampenband
# rauf (sichtbar): Vorplatz -> Kehrenrampe -> Ankunft Dach rechts
seg_up = [(2.8, 17.4, 0), (1.0, 15.2, 0), (0.6, W + YA + ROFF, 0.04)]
seg_up += switchback(ROFF)
seg_up += [(L - 0.4, W - 0.6, Z3)]
# Runde auf dem Dach (sichtbar, im Uhrzeigersinn = weiter rechts rum)
lap = [seg_up[-1],
       (L - 0.8, W - 1.4, Z3), (L - 0.8, 2.4, Z3), (14.2, 3.4, Z3),
       (3.2, 3.4, Z3), (1.3, 4.3, Z3), (1.3, W - 1.6, Z3),
       (2.4, W - 0.9, Z3), (6.4, W - 0.9, Z3),
       (10.4, W - 1.1, Z3), (L - 1.6, W - 0.8, Z3), (L - 0.5, W - 0.7, Z3)]
# runter (gestrichelt): gleiche Rampe, parallel versetzt, zurueck zur Wechselzone
seg_dn = [lap[-1]]
seg_dn += list(reversed(switchback(-ROFF)))
seg_dn += [(0.5, W + YA + 0.1, 0.04), (1.0, 15.0, 0), (2.75, 17.15, 0)]

segs = [(seg_up, False), (lap, False), (seg_dn, True)]
lens = [plen(s) for s, _ in segs]
start_pt = P(*seg_up[0])
finish_pt = P(2.8, 17.4, 0)

# ---------- Labels ----------
def lbl(p3, dx, dy, at, text, anchor='start'):
    x, y = P(*p3)
    return (x, y, x + dx, y + dy, at, text, anchor)

labels = [
    lbl(seg_up[0], 14, 44, 0.03, 'START / WECHSELZONE'),
    lbl((5.0, W + YA, 0.5), 26, 70, 0.12, 'RAMPE — NORDSEITE'),
    lbl((L + 0.7, W - 0.2, Z1 + 0.12), 48, 16, 0.24, 'KEHRE 1 — RECHTS'),
    lbl((-0.9, W - 0.2, Z2 + 0.12), -42, -2, 0.40, 'KEHRE 2 — RECHTS', anchor='end'),
    lbl((L - 0.4, W - 0.6, Z3), 36, -40, 0.52, 'ANKUNFT — ANDERES ENDE'),
    lbl((7.5, 3.5, Z3), -6, -44, 0.66, 'EINE RUNDE AUF DEM DECK', anchor='middle'),
    lbl((11.5, W + YA - 0.3, Z1 + 0.55), 56, 54, 0.86, 'RUNTER — GLEICHE RAMPE'),
]

# ---------- Bounding box ----------
all_pts = []
def collect(dlist):
    for d in dlist:
        for m in re.finditer(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', d):
            all_pts.append((float(m.group(1)), float(m.group(2))))
for grp in (bld_main, bld_grid, bld_hidden, ramp, deck, ground, railing, clad, pav, sign, arcade):
    collect(grp)
collect([path(s) for s, _ in segs])
xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]
pad = 95
tx, ty = pad - min(xs), pad - min(ys)
vw = (max(xs) - min(xs)) + 2 * pad
vh = (max(ys) - min(ys)) + 2 * pad

def G(cls, dlist):
    return f'<g class="{cls}">\n' + "\n".join(f'<path d="{d}"/>' for d in dlist) + '\n</g>'

route_svg, dashmask_svg = [], []
for (pts, hidden), ln in zip(segs, lens):
    cls = 'route route--hidden' if hidden else 'route'
    route_svg.append(
        f'<path class="{cls}" data-len="{ln:.0f}" d="{path(pts)}" '
        f'stroke-dasharray="{ln:.0f}" stroke-dashoffset="{ln:.0f}"/>')
    if hidden:
        dashmask_svg.append(f'<path class="route-mask" d="{path(pts)}"/>')

label_svg = []
for (x, y, lx, ly, at, text, anchor) in labels:
    label_svg.append(f'''<g class="plan-label" data-at="{at}">
  <line x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" class="pl-lead"/>
  <circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" class="pl-dot"/>
  <text x="{lx:.1f}" y="{ly + (15 if ly > y else -7):.1f}" text-anchor="{anchor}" class="pl-txt">{text}</text>
</g>''')

svg = f'''<svg id="planSvg" viewBox="0 0 {vw:.0f} {vh:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="'IBM Plex Mono', monospace" aria-label="Isometrische Zeichnung der ENTER Technikwelt: Kehren-Rampe auf der Nordseite aufs Parkdeck, eine Runde oben, gleiche Rampe runter" role="img">
<g transform="translate({tx:.1f},{ty:.1f})">
{G('pg pg-hidden', bld_hidden)}
{G('pg pg-faint', clad)}
{G('pg pg-faint', arcade)}
{G('pg pg-faint', ground)}
{G('pg pg-ramp', ramp)}
{G('pg', bld_grid)}
{G('pg pg-faint', railing)}
{G('pg', deck)}
{G('pg', pav)}
{G('pg', sign)}
{"".join(extra_svg)}
{G('pg pg-main', bld_main)}
<g id="planRoute">
{chr(10).join(route_svg)}
{chr(10).join(dashmask_svg)}
</g>
<g class="plan-mark" id="planStartMark">
  <circle cx="{start_pt[0]:.1f}" cy="{start_pt[1]:.1f}" r="8" class="pm-c"/>
  <circle cx="{start_pt[0]:.1f}" cy="{start_pt[1]:.1f}" r="2.6" class="pm-d"/>
</g>
<g class="plan-mark" id="planFinishMark">
  <circle cx="{finish_pt[0]:.1f}" cy="{finish_pt[1]:.1f}" r="9" class="pm-pulse"/>
  <circle cx="{finish_pt[0]:.1f}" cy="{finish_pt[1]:.1f}" r="3.4" class="pm-d"/>
</g>
{"".join(label_svg)}
</g>
</svg>'''

with open('plan3.svg', 'w') as f:
    preview = svg.replace('<svg ', '<svg style="background:#0D0C0B" ', 1)
    preview = re.sub(r'stroke-dashoffset="\d+"', 'stroke-dashoffset="0"', preview)
    style = '''<style>
.pg path {stroke:#F4F1EB; stroke-width:1; fill:none; opacity:.42}
.pg-main path {stroke-width:1.8; opacity:.95}
.pg-faint path {stroke-width:.6; opacity:.22}
.pg-hidden path {stroke-dasharray:4 5; opacity:.16}
.pg-ramp path {stroke-width:1.2; opacity:.6}
.route {stroke:#EE3829; stroke-width:4; fill:none; stroke-linejoin:round; stroke-linecap:round}
.route--hidden {stroke-width:2.4; opacity:.5}
.route-mask {stroke:#0D0C0B; stroke-width:3.5; fill:none; stroke-dasharray:5 7}
.pm-c,.pm-pulse {stroke:#EE3829; fill:none; stroke-width:1.5}
.pm-d {fill:#EE3829}
.pl-lead {stroke:#8A857C; stroke-width:1}
.pl-dot {fill:#F4F1EB}
.pl-txt {fill:#F4F1EB; font-size:15px; letter-spacing:2.5px}
.pl-sign {fill:#F4F1EB; font-size:13px; letter-spacing:3px; opacity:.8}
</style>'''
    f.write(preview.replace('</svg>', style + '</svg>'))

with open('plan3_embed.svg', 'w') as f:
    f.write(svg)

print(f"viewBox 0 0 {vw:.0f} {vh:.0f}")
print("Segmentlaengen px:", json.dumps([round(l) for l in lens]))
