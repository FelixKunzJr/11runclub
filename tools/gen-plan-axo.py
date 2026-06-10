#!/usr/bin/env python3
"""Generator v5: ENTER Technikwelt — Ansicht von NORDWESTEN.

Man schaut wie von der Strasse auf die Nordfassade (vorne links) und die
Westfassade (vorne rechts):
  +y = NORD (Fassade y=W, vorne links) · +x = WEST (Fassade x=L, vorne rechts)
  y=0 = SUED (verdeckt) · x=0 = OST (verdeckt)

Route (Club-Beschreibung): Einstieg Nordseite am OST-Ende (= im Bild LINKS)
-> Ostfassade hoch (verdeckt) -> rechts Suedseite (verdeckt) -> rechts
Westfassade (sichtbarer Anstieg vorne rechts) -> AUSSTIEG auf dem Dach an
der WESTseite (vordere Ecke) -> eine Runde auf dem Deck -> gestrichelt
dieselbe Strecke runter zur Wechselzone.

Dach: Wohnblock an der Suedkante, Treppenzylinder noerdlich-mittig
(saubere Silhouette: Tangenten bei 135/315 Grad), Parkfelder mittig.
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

L, W = 15.0, 13.0            # x: Ost->West (Nordfassade 15 lang), y: Sued->Nord (13)
Z1, Z2, Z3 = 1.35, 2.65, 3.95
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
for x in range(0, 16, 2):
    bld_grid.append(seg((x, W + 0.02, 0), (x, W + 0.02, Z3)))
for y in range(1, 13, 2):
    bld_grid.append(seg((L + 0.02, y, 0), (L + 0.02, y, Z3)))

# ---------- EG: offener Saeulengang an der Nordfassade (Eingang) ----------
arcade.append(seg((0, W - 1.8, 0), (L, W - 1.8, 0)))
arcade.append(seg((0, W - 1.8, Z1 - 0.22), (L, W - 1.8, Z1 - 0.22)))
for x in range(1, 16, 2):
    arcade.append(seg((x, W - 1.8, 0), (x, W - 1.8, Z1 - 0.22)))

# ---------- Wellblech-Bays ----------
def clad_n(x0, x1, z0, z1, step=0.3):
    x = x0 + step
    while x < x1 - 0.05:
        clad.append(seg((x, W - 0.35, z0 + 0.08), (x, W - 0.35, z1 - 0.26)))
        x += step
def clad_w(y0, y1, z0, z1, step=0.3):
    y = y0 + step
    while y < y1 - 0.05:
        clad.append(seg((L - 0.35, y, z0 + 0.08), (L - 0.35, y, z1 - 0.26)))
        y += step
for (a, b) in ((2, 6), (8, 12), (13, 15)):
    clad_n(a, b, Z1, Z2)
for (a, b) in ((0, 5), (9, 13)):
    clad_n(a, b, Z2, Z3)
for (a, b) in ((1, 5), (7, 11)):
    clad_w(a, b, 0.2, Z1)
for (a, b) in ((2, 7), (9, 12)):
    clad_w(a, b, Z1, Z2)
for (a, b) in ((4, 10),):
    clad_w(a, b, Z2, Z3)

# ---------- Gelaender Dachrand ----------
railing.append(path([(0, W, Z3 + RAIL), (L, W, Z3 + RAIL), (L, 0, Z3 + RAIL)]))
for x in range(0, 16):
    railing.append(seg((x, W, Z3), (x, W, Z3 + RAIL)))
for y in range(0, 13):
    railing.append(seg((L, y, Z3), (L, y, Z3 + RAIL)))

# ---------- Routen-Bausteine ----------
def corner(p_from, p_to, z0, z1, n=8):
    (x0, y0), (x1, y1) = p_from, p_to
    cx, cy = (x1, y0) if abs(x1 - x0) < abs(y1 - y0) else (x0, y1)
    pts = []
    for i in range(n + 1):
        t = i / n
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
        pts.append((bx, by, z0 + (z1 - z0) * t))
    return pts

def run_east(off, y0, y1, z0, z1, n=22):    # Ostfassade x=-off, laeuft Nord->Sued
    return [(-off, y0 + (y1 - y0) * (i / n), z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_south(off, x0, x1, z0, z1, n=22):   # Suedfassade y=-off, laeuft Ost->West
    return [(x0 + (x1 - x0) * (i / n), -off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_west(off, y0, y1, z0, z1, n=26):    # Westfassade x=L+off, laeuft Sued->Nord
    return [(L + off, y0 + (y1 - y0) * (i / n), z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]

RO = 0.45
def route_pieces(off):
    """[(pts, hidden), ...] — Einstieg links, Ost+Sued verdeckt, West sichtbar."""
    entry = [(1.8, W + 3.4, 0), (0.9, W + 1.3, 0), (0.7, W + off, 0.02)]
    entry += corner((0.7, W + off), (-off, W - 0.8), 0.02, 0.12)
    east = run_east(off, W - 0.9, 0.9, 0.12, Z1)
    east += corner((-off, 0.8), (0.8, -off), Z1, Z1 + 0.14)
    south = run_south(off, 0.9, L - 0.9, Z1 + 0.14, Z2)
    south += corner((L - 0.8, -off), (L + off, 0.8), Z2, Z2 + 0.14)
    west = run_west(off, 0.9, W - 0.9, Z2 + 0.14, Z3)
    west += corner((L + off, W - 0.8), (L - 0.6, W - 0.8), Z3, Z3)
    return [(entry, False), (east, True), (south, True), (west, False)]

pieces = route_pieces(RO)
seg_up = [p for pts, _ in pieces for p in pts]
hidden_up = [p for pts, h in pieces if h for p in pts]
arrive = seg_up[-1]

# Runde auf dem Deck (rechts herum), zurueck zur Westecke
lap = [arrive,
       (L - 0.8, W - 1.8, Z3), (L - 0.8, 2.0, Z3), (L - 1.6, 3.3, Z3),
       (3.0, 3.4, Z3), (2.1, 4.3, Z3), (2.1, W - 1.6, Z3),
       (3.2, W - 0.9, Z3), (7.0, W - 0.9, Z3), (11.0, W - 1.0, Z3),
       (L - 1.6, W - 0.9, Z3), arrive]

# runter: gleiche Strecke, gestrichelt
dn_pieces = route_pieces(RO - 0.18)
seg_dn = [arrive] + [p for pts, _ in reversed(dn_pieces) for p in reversed(pts)]
seg_dn += [(0.95, W + 1.35, 0), (1.85, W + 3.35, 0)]

segs = [(seg_up, False), (lap, False), (seg_dn, True)]
lens = [plen(s) for s, _ in segs]
start_pt = P(*seg_up[0])
finish_pt = P(1.85, W + 3.35, 0)

# ---------- Rampenband: sichtbarer West-Abschnitt + Einstiegs-Stummel ----------
band_w = run_west(0.06, 0.0, W, Z2 + 0.1, Z3 + 0.02)
ramp.append(path(band_w))
ramp.append(path([(x, y, z - 0.2) for (x, y, z) in band_w]))
stub = [(2.2, W + 0.06, 0.02)] + corner((1.0, W + 0.06), (-0.06, W - 1.0), 0.04, 0.14) + run_east(0.06, W - 1.1, W - 3.0, 0.14, 0.4)
ramp.append(path(stub))
ramp.append(path([(x, y, z - 0.18) for (x, y, z) in stub]))

# ---------- Dach-Layout ----------
# Wohnblock an der SUEDkante (y klein), quer ueber die Breite
BX0, BX1, BY0, BY1, BH = 2.0, 13.0, 0.7, 2.9, 1.05
pav.append(path([(BX0, BY0, Z3 + BH), (BX1, BY0, Z3 + BH), (BX1, BY1, Z3 + BH), (BX0, BY1, Z3 + BH)], closed=True))
pav.append(path([(BX0, BY1, Z3), (BX1, BY1, Z3), (BX1, BY0, Z3)]))
for (xx, yy) in ((BX0, BY1), (BX1, BY1), (BX1, BY0)):
    pav.append(seg((xx, yy, Z3), (xx, yy, Z3 + BH)))
x = BX0 + 0.5
while x < BX1 - 0.2:
    pav.append(seg((x, BY1, Z3 + 0.06), (x, BY1, Z3 + BH - 0.06)))
    x += 0.55

# Treppenzylinder noerdlich-mittig — saubere Silhouette:
# Tangenten der projizierten Ellipse liegen bei 135 und 315 Grad
def drum(cx0, cy0, r, z0, z1, n=28):
    circ = lambda a, z: (cx0 + r * math.cos(a), cy0 + r * math.sin(a), z)
    top = [circ(2 * math.pi * i / n, z1) for i in range(n + 1)]
    deck.append(path(top))
    a1, a2 = math.radians(135), math.radians(315)
    for a in (a1, a2):
        x, y, _ = circ(a, z0)
        deck.append(seg((x, y, z0), (x, y, z1)))
    base = [circ(math.radians(-45 + 180 * i / n), z0) for i in range(n + 1)]
    deck.append(path(base))
drum(7.5, W - 2.8, 1.1, Z3, Z3 + 0.9)

# Parkfelder mittig
for i in range(7):
    x = 4.0 + i * 1.3
    deck.append(seg((x, 4.4, Z3), (x, 7.2, Z3)))
deck.append(seg((4.0, 4.4, Z3), (4.0 + 6 * 1.3, 4.4, Z3)))
deck.append(seg((4.0, 7.2, Z3), (4.0 + 6 * 1.3, 7.2, Z3)))
def box_top(x0, y0, x1, y1, z):
    return path([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], closed=True)
deck.append(box_top(6.7, 4.7, 7.6, 6.6, Z3 + 0.16))
deck.append(box_top(6.9, 5.1, 7.4, 6.2, Z3 + 0.34))

# ENTER-Schriftzug an der Nord-Dachkante
sx, sy = P(4.6, W - 0.25, Z3 + 1.18)
sign.append(seg((4.3, W - 0.25, Z3 + RAIL), (4.3, W - 0.25, Z3 + 1.0)))
sign.append(seg((10.8, W - 0.25, Z3 + RAIL), (10.8, W - 0.25, Z3 + 1.0)))
sign.append(seg((4.3, W - 0.25, Z3 + 1.0), (10.8, W - 0.25, Z3 + 1.0)))
extra_svg.append(
    f'<text x="{sx:.1f}" y="{sy:.1f}" class="pl-sign" transform="rotate(30 {sx:.1f} {sy:.1f})">ENTER TECHNIKWELT</text>')

# ---------- Vorplatz Nordseite (Wechselzone, im Bild unten links) ----------
for i in range(4):
    g = 1.2 + i * 1.1
    ground.append(seg((0.0, W + g, 0), (L * 0.55, W + g, 0)))
for i in range(4):
    gx = 0.8 + i * 2.4
    ground.append(seg((gx, W + 1.2, 0), (gx, W + 4.5, 0)))

# ---------- Labels ----------
def lbl(p3, dx, dy, at, text, anchor='start'):
    x, y = P(*p3)
    return (x, y, x + dx, y + dy, at, text, anchor)

labels = [
    lbl(seg_up[0], 18, 40, 0.03, 'START / WECHSELZONE'),
    lbl((0.6, W + RO, 0.1), -36, 36, 0.07, 'EINSTIEG — LINKS', anchor='end'),
    lbl((-RO, 6.5, 0.95), -50, -34, 0.18, 'OSTSEITE — VERDECKT', anchor='end'),
    lbl((8.0, -RO, Z1 + 0.75), 26, -48, 0.34, 'RECHTS — SÜDSEITE'),
    lbl((L + RO, 2.6, Z2 + 0.3), 46, 26, 0.48, 'RECHTS — WESTSEITE'),
    lbl((L - 0.7, W - 0.8, Z3), 34, -42, 0.58, 'AUSSTIEG WESTSEITE — DACH'),
    lbl((4.0, 5.8, Z3), -20, -46, 0.72, 'EINE RUNDE AUF DEM DECK', anchor='middle'),
    lbl((L + RO - 0.18, 10.2, Z2 + 0.4), 44, 38, 0.88, 'RUNTER — GLEICHE STRECKE'),
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
dashmask_svg.append(f'<path class="route-mask" d="{path(hidden_up)}"/>')

label_svg = []
for (x, y, lx, ly, at, text, anchor) in labels:
    label_svg.append(f'''<g class="plan-label" data-at="{at}">
  <line x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" class="pl-lead"/>
  <circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" class="pl-dot"/>
  <text x="{lx:.1f}" y="{ly + (15 if ly > y else -7):.1f}" text-anchor="{anchor}" class="pl-txt">{text}</text>
</g>''')

svg = f'''<svg id="planSvg" viewBox="0 0 {vw:.0f} {vh:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="'IBM Plex Mono', monospace" aria-label="Isometrische Zeichnung der ENTER Technikwelt: Rampeneinstieg Nordseite links, um Ost- und Südseite auf die Westfassade, Ausstieg auf dem Parkdeck, Runde oben, gleiche Strecke zurück" role="img">
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

with open('plan5.svg', 'w') as f:
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

with open('plan5_embed.svg', 'w') as f:
    f.write(svg)

print(f"viewBox 0 0 {vw:.0f} {vh:.0f}")
print("Segmentlaengen px:", json.dumps([round(l) for l in lens]))
