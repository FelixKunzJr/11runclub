#!/usr/bin/env python3
"""Generator v4: ENTER Technikwelt, Route nach Club-Beschreibung (Juni 2026).

Kompass der Zeichnung:  +x = NORD (Fassade vorne rechts, x=L),
                        +y = WEST (Fassade vorne links, y=W),
                        y=0 = OST (verdeckt), x=0 = SUED (verdeckt).

Route: Einstieg an der NORDseite (Ost-Ende) -> Ostfassade hoch (verdeckt)
-> rechts auf die SUEDseite (verdeckt) -> rechts auf die WESTseite
(sichtbarer Swoosh) -> Ankunft auf dem Dach an der NORDseite (vordere Ecke)
-> eine Runde auf dem Deck -> gestrichelt dieselbe Strecke runter.

Dach: Wohnblock an der SUEDseite (x klein), Treppenzylinder noerdlich-mittig.
Ecken ohne Radius. Vorplatz/Wechselzone auf der Nordseite.
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

L, W = 14.0, 15.0            # x: Sued->Nord (14), y: Ost->West (15)
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
for x in range(0, 15, 2):
    bld_grid.append(seg((x, W + 0.02, 0), (x, W + 0.02, Z3)))
for y in range(1, 15, 2):
    bld_grid.append(seg((L + 0.02, y, 0), (L + 0.02, y, Z3)))

# ---------- EG: offener Saeulengang an der NORDseite (Eingang) ----------
arcade.append(seg((L - 1.8, 0, 0), (L - 1.8, W, 0)))
arcade.append(seg((L - 1.8, 0, Z1 - 0.22), (L - 1.8, W, Z1 - 0.22)))
for y in range(1, 15, 2):
    arcade.append(seg((L - 1.8, y, 0), (L - 1.8, y, Z1 - 0.22)))

# ---------- Wellblech-Bays (beide sichtbaren Fassaden) ----------
def clad_w(x0, x1, z0, z1, step=0.3):
    x = x0 + step
    while x < x1 - 0.05:
        clad.append(seg((x, W - 0.35, z0 + 0.08), (x, W - 0.35, z1 - 0.26)))
        x += step
def clad_n(y0, y1, z0, z1, step=0.3):
    y = y0 + step
    while y < y1 - 0.05:
        clad.append(seg((L - 0.35, y, z0 + 0.08), (L - 0.35, y, z1 - 0.26)))
        y += step
for (a, b) in ((0, 4), (6, 10), (12, 14)):
    clad_w(a, b, 0.2, Z1)
for (a, b) in ((2, 6), (8, 14)):
    clad_w(a, b, Z1, Z2)
for (a, b) in ((0, 5), (9, 13)):
    clad_w(a, b, Z2, Z3)
for (a, b) in ((1, 5), (7, 11), (13, 15)):
    clad_n(a, b, Z1, Z2)
for (a, b) in ((3, 8), (10, 14)):
    clad_n(a, b, Z2, Z3)

# ---------- Gelaender Dachrand ----------
railing.append(path([(0, W, Z3 + RAIL), (L, W, Z3 + RAIL), (L, 0, Z3 + RAIL)]))
for x in range(0, 15):
    railing.append(seg((x, W, Z3), (x, W, Z3 + RAIL)))
for y in range(0, 16):
    railing.append(seg((L, y, Z3), (L, y, Z3 + RAIL)))

# ---------- Rampe: um drei Seiten (Ost -> Sued -> West) ----------
RO = 0.45    # Abstand der Rampe von der Fassade
def run_east(off, x0, x1, z0, z1, n=22):    # y = -off, laeuft in -x
    return [(x0 + (x1 - x0) * ease(i / n) ** 0 * (i / n), -off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_south(off, y0, y1, z0, z1, n=22):   # x = -off, laeuft in +y
    return [(-off, y0 + (y1 - y0) * (i / n), z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_west(off, x0, x1, z0, z1, n=26):    # y = W+off, laeuft in +x
    return [(x0 + (x1 - x0) * (i / n), W + off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def corner(p_from, p_to, z0, z1, n=8):
    """kleine Eckkurve (Viertelbogen, plan) zwischen zwei Punkten."""
    (x0, y0), (x1, y1) = p_from, p_to
    cx, cy = (x1, y0) if abs(x1 - x0) < abs(y1 - y0) else (x0, y1)
    pts = []
    for i in range(n + 1):
        t = i / n
        # quadratische Bezier-Naeherung
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
        pts.append((bx, by, z0 + (z1 - z0) * t))
    return pts

def route3(off):
    """Einstieg Nord (Ost-Ende) -> Ost -> Sued -> West -> Dach Nordecke."""
    pts = [(L + off, 1.6, 0.02)]                                   # an der Nordfassade, Ost-Ende
    pts += corner((L + off, 0.9), (L - 0.9, -off), 0.02, 0.1)      # um die NO-Ecke
    pts += run_east(off, L - 1.0, 0.9, 0.1, Z1)                    # Ostfassade (verdeckt)
    pts += corner((0.9, -off), (-off, 0.9), Z1, Z1 + 0.14)         # SO-Ecke, rechts
    pts += run_south(off, 1.0, W - 1.0, Z1 + 0.14, Z2)             # Suedfassade (verdeckt)
    pts += corner((-off, W - 0.9), (0.9, W + off), Z2, Z2 + 0.14)  # SW-Ecke, rechts
    pts += run_west(off, 1.0, L - 1.0, Z2 + 0.14, Z3)              # Westfassade (sichtbar!)
    pts += corner((L - 0.9, W + off), (L - 0.4, W - 0.7), Z3, Z3)  # auf das Deck (NW-Ecke)
    return pts

# Rampenband nur am sichtbaren West-Abschnitt + Einstiegs-Stummel Nord
band_w = run_west(0.06, 0.0, L, Z2 + 0.1, Z3 + 0.02)
ramp.append(path(band_w))
ramp.append(path([(x, y, z - 0.2) for (x, y, z) in band_w]))
stub = [(L + 0.06, 2.2, 0.02)] + corner((L + 0.06, 1.0), (L - 1.0, -0.06), 0.02, 0.12) + run_east(0.06, L - 1.1, L - 3.0, 0.12, 0.35)
ramp.append(path(stub))
ramp.append(path([(x, y, z - 0.18) for (x, y, z) in stub]))

# ---------- Dach-Layout ----------
# Wohnblock an der SUEDseite (x klein), quer
BX0, BX1, BY0, BY1, BH = 0.7, 2.9, 2.0, 13.0, 1.05
pav.append(path([(BX0, BY0, Z3 + BH), (BX1, BY0, Z3 + BH), (BX1, BY1, Z3 + BH), (BX0, BY1, Z3 + BH)], closed=True))
pav.append(path([(BX0, BY1, Z3), (BX1, BY1, Z3), (BX1, BY0, Z3)]))
for (xx, yy) in ((BX0, BY1), (BX1, BY1), (BX1, BY0)):
    pav.append(seg((xx, yy, Z3), (xx, yy, Z3 + BH)))
y = BY0 + 0.5
while y < BY1 - 0.2:
    pav.append(seg((BX1, y, Z3 + 0.06), (BX1, y, Z3 + BH - 0.06)))
    y += 0.55

# Treppenzylinder noerdlich, mittig
def drum(cx0, cy0, r, z0, z1, n=22):
    top = [(cx0 + r * math.cos(2 * math.pi * i / n), cy0 + r * math.sin(2 * math.pi * i / n), z1) for i in range(n + 1)]
    deck.append(path(top))
    deck.append(seg((cx0 - r, cy0, z0), (cx0 - r, cy0, z1)))
    deck.append(seg((cx0 + r, cy0, z0), (cx0 + r, cy0, z1)))
    front = [(cx0 + r * math.cos(math.pi + math.pi * i / n), cy0 + r * math.sin(math.pi + math.pi * i / n), z0) for i in range(n + 1)]
    deck.append(path(front))
drum(L - 3.0, 7.5, 1.1, Z3, Z3 + 0.9)

# Parkfelder (mittig, Reihe quer)
for i in range(7):
    y = 3.2 + i * 1.3
    deck.append(seg((5.4, y, Z3), (8.0, y, Z3)))
deck.append(seg((5.4, 3.2, Z3), (5.4, 3.2 + 6 * 1.3, Z3)))
deck.append(seg((8.0, 3.2, Z3), (8.0, 3.2 + 6 * 1.3, Z3)))
def box_top(x0, y0, x1, y1, z):
    return path([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], closed=True)
deck.append(box_top(5.7, 5.6, 7.7, 6.5, Z3 + 0.16))
deck.append(box_top(6.2, 5.8, 7.2, 6.3, Z3 + 0.34))

# ENTER-Schriftzug an der Nord-Dachkante
sx, sy = P(L + 0.1, 11.6, Z3 + 0.62)
sign.append(seg((L + 0.05, 11.8, Z3 + RAIL), (L + 0.05, 11.8, Z3 + 1.0)))
sign.append(seg((L + 0.05, 5.4, Z3 + RAIL), (L + 0.05, 5.4, Z3 + 1.0)))
sign.append(seg((L + 0.05, 11.8, Z3 + 1.0), (L + 0.05, 5.4, Z3 + 1.0)))
extra_svg.append(
    f'<text x="{sx:.1f}" y="{sy:.1f}" class="pl-sign" transform="rotate(-30 {sx:.1f} {sy:.1f})">ENTER TECHNIKWELT</text>')

# ---------- Vorplatz NORDseite (Wechselzone) ----------
for i in range(4):
    g = 1.2 + i * 1.1
    ground.append(seg((L + g, 0.5, 0), (L + g, W * 0.7, 0)))
for i in range(5):
    gy = 1.0 + i * 2.2
    ground.append(seg((L + 1.2, gy, 0), (L + 4.5, gy, 0)))

# ---------- Route ----------
start3 = (L + 3.4, 4.2, 0)
seg_up = [start3, (L + 1.6, 2.6, 0)] + route3(RO)
arrive = seg_up[-1]
# Runde auf dem Deck (rechts herum), zurueck zur NW-Ecke
lap = [arrive,
       (L - 0.8, W - 1.6, Z3), (L - 0.8, 1.2, Z3),
       (L - 2.2, 0.9, Z3), (4.2, 0.9, Z3), (3.4, 1.6, Z3),
       (3.4, W - 1.2, Z3), (4.4, W - 0.8, Z3),
       (9.0, W - 0.8, Z3), (L - 1.5, W - 0.9, Z3), arrive]
# runter: gleiche Strecke, gestrichelt, zurueck zur Wechselzone
seg_dn = [arrive] + list(reversed(route3(RO - 0.18)))[1:]
seg_dn += [(L + 1.7, 2.75, 0), (L + 3.35, 4.1, 0)]

segs = [(seg_up, False), (lap, False), (seg_dn, True)]
lens = [plen(s) for s, _ in segs]
start_pt = P(*start3)
finish_pt = P(L + 3.4, 4.2, 0)

# ---------- Labels ----------
def lbl(p3, dx, dy, at, text, anchor='start'):
    x, y = P(*p3)
    return (x, y, x + dx, y + dy, at, text, anchor)

labels = [
    lbl(start3, 16, 40, 0.03, 'START / WECHSELZONE'),
    lbl((L + RO, 1.0, 0.05), 52, 30, 0.08, 'EINSTIEG NORDSEITE'),
    lbl((7.0, -RO, 0.8), 64, -26, 0.18, 'OSTSEITE — VERDECKT'),
    lbl((-RO, 7.5, Z1 + 0.7), -46, -18, 0.32, 'RECHTS — SÜDSEITE', anchor='end'),
    lbl((2.6, W + RO, Z2 + 0.3), -4, -42, 0.46, 'RECHTS — WESTSEITE', anchor='end'),
    lbl((L - 0.5, W - 0.8, Z3), 30, -44, 0.56, 'ANKUNFT DACH — NORD'),
    lbl((4.5, 7.0, Z3), -16, -48, 0.7, 'EINE RUNDE AUF DEM DECK', anchor='middle'),
    lbl((9.5, W + RO - 0.18, Z1 + 0.75), 26, 62, 0.88, 'RUNTER — GLEICHE STRECKE'),
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
# Verdeckte Teile des Aufstiegs (Ost+Sued) nachtraeglich maskieren:
# eigene Maske ueber dem Up-Segment nur im verdeckten Bereich
hidden_up = route3(RO)[4:75]   # NO-Ecke bis Ende SW-Ecke (Ost+Sued verdeckt)
dashmask_svg.append(f'<path class="route-mask" d="{path(hidden_up)}"/>')

label_svg = []
for (x, y, lx, ly, at, text, anchor) in labels:
    label_svg.append(f'''<g class="plan-label" data-at="{at}">
  <line x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" class="pl-lead"/>
  <circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" class="pl-dot"/>
  <text x="{lx:.1f}" y="{ly + (15 if ly > y else -7):.1f}" text-anchor="{anchor}" class="pl-txt">{text}</text>
</g>''')

svg = f'''<svg id="planSvg" viewBox="0 0 {vw:.0f} {vh:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="'IBM Plex Mono', monospace" aria-label="Isometrische Zeichnung der ENTER Technikwelt: Rampe um Ost-, Süd- und Westseite aufs Parkdeck, Runde auf dem Dach, gleiche Strecke zurück" role="img">
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
{label_svg and "".join(label_svg)}
</g>
</svg>'''

with open('plan4.svg', 'w') as f:
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

with open('plan4_embed.svg', 'w') as f:
    f.write(svg)

print(f"viewBox 0 0 {vw:.0f} {vh:.0f}")
print("Segmentlaengen px:", json.dumps([round(l) for l in lens]))
