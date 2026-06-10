#!/usr/bin/env python3
"""Generator v2: originalgetreuere Heist-Axonometrie der ENTER Technikwelt.

Korrekturen ggü. v1 (aus Waldrap-Grundrissen EG/1.OG/2.OG/DG, Schnitt, Fotos):
- fast quadratischer Grundriss, abgerundete Ecke(n)
- Rampe als geschwungener Swoosh (Ease-in/out an den Podesten),
  laeuft HINTER den aussenstehenden Betonstuetzen
- offener Saeulengang im EG, Slab-Fascia-Baender an jedem Geschoss
- Dach: verglastes DG-Band an der Vorderkante, Parkfelder,
  runder Wendeltreppen-Drum, ENTER-Schriftzug
- Route: 1 Umrundung gegen den Uhrzeigersinn, Ankunft hinten links,
  sichtbarer Schlusslauf uebers Deck zur Wende
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

L, W = 16.0, 13.0          # Grundriss fast quadratisch
Z1, Z2, Z3 = 1.55, 2.75, 3.95
RC = 1.6                   # Eckradius vordere Ecke (L,W)
RAIL = 0.3

# ---------- Hilfen: Kanten mit gerundeter vorderer Ecke ----------
def corner_arc(off, z0, z1=None, n=10):
    """Viertelbogen um die vordere Ecke (L,W), off = Abstand nach aussen."""
    z1 = z0 if z1 is None else z1
    cx, cy, r = L - RC, W - RC, RC + off
    pts = []
    for i in range(n + 1):
        a = math.radians(90 * i / n)
        pts.append((cx + r * math.sin(a), cy + r * math.cos(a), z0 + (z1 - z0) * i / n))
    return pts

def front_right_edge(off, z):
    """Kante von (0,W) ueber die runde Ecke nach (L,0) auf Hoehe z."""
    return [(0, W + off, z)] + corner_arc(off, z) + [(L + off, 0, z)]

bld_main, bld_grid, bld_hidden = [], [], []
ramp, deck, ground, railing, clad, pav, sign = [], [], [], [], [], [], []
extra_svg = []

# ---------- Silhouette ----------
bld_main += [
    seg((0, W, 0), (0, W, Z3)),
    seg((L, 0, 0), (L, 0, Z3)),
    path(front_right_edge(0, 0)),                  # Bodenkante
]
# Dach-Aussenkante: alle 4 Ecken gerundet (vorne staerker)
def rounded_roof(z):
    def arc(cx, cy, a0, a1, r, n=8):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), z) for i in range(n + 1)]
    r2 = 0.7
    pts = []
    pts += arc(L - RC, W - RC, 0, 90, RC)      # vorne (L,W)... winkel: 0=+x,90=+y
    pts += arc(r2, W - r2, 90, 180, r2)        # (0,W)
    pts += arc(r2, r2, 180, 270, r2)           # (0,0)
    pts += arc(L - r2, r2, 270, 360, r2)       # (L,0)
    return pts + [pts[0]]
bld_main.append(path(rounded_roof(Z3)))

bld_hidden += [
    seg((0, 0, 0), (0, 0, Z3)),
    seg((0, 0, 0), (L, 0, 0)),
    seg((0, 0, 0), (0, W, 0)),
]
for z in (Z1, Z2):
    bld_hidden.append(path([(0, W, z), (0, 0, z), (L, 0, z)]))  # innere Decke (Roentgen)

# ---------- Slab-Fascia-Baender an jedem Geschoss (wrappen um die Ecke) ----------
for z in (Z1, Z2, Z3):
    bld_grid.append(path(front_right_edge(0.02, z)))
    bld_grid.append(path(front_right_edge(0.02, z - 0.22)))

# ---------- Stuetzenraster (vor der Fassade) ----------
for x in range(0, 15, 2):
    bld_grid.append(seg((x, W + 0.02, 0), (x, W + 0.02, Z3)))
for y in range(2, 12, 2):
    bld_grid.append(seg((L + 0.02, y, 0), (L + 0.02, y, Z3)))

# ---------- EG: offener Saeulengang (innere Wand + innere Stuetzen) ----------
arcade = []
arcade.append(seg((0, W - 1.8, 0), (L - 1.8, W - 1.8, 0)))          # innere Wandlinie am Boden
arcade.append(seg((0, W - 1.8, Z1 - 0.22), (L - 1.8, W - 1.8, Z1 - 0.22)))
for x in range(1, 15, 2):
    arcade.append(seg((x, W - 1.8, 0), (x, W - 1.8, Z1 - 0.22)))

# ---------- Wellblech in den Obergeschossen ----------
def clad_bay_front(x0, x1, z0, z1, step=0.3):
    x = x0 + step
    while x < x1 - 0.05:
        clad.append(seg((x, W - 0.35, z0 + 0.08), (x, W - 0.35, z1 - 0.26)))
        x += step
def clad_bay_right(y0, y1, z0, z1, step=0.3):
    y = y0 + step
    while y < y1 - 0.05:
        clad.append(seg((L - 0.35, y, z0 + 0.08), (L - 0.35, y, z1 - 0.26)))
        y += step
for (a, b) in ((0, 4), (6, 10), (12, 14.4)):
    clad_bay_front(a, b, Z1, Z2)
for (a, b) in ((2, 6), (8, 14.4)):
    clad_bay_front(a, b, Z2, Z3)
for (a, b) in ((1, 5), (7, 11)):
    clad_bay_right(a, b, Z1, Z2)
for (a, b) in ((3, 9),):
    clad_bay_right(a, b, Z2, Z3)

# ---------- Gelaender Dachrand (vorne + rechts, um die Ecke) ----------
railing.append(path(front_right_edge(0, Z3 + RAIL)))
u = 0.5
while u < L + W - 1:                       # Posten entlang der abgewickelten Kante
    if u <= L - RC:
        p3 = (u, W, Z3)
    elif u <= L - RC + RC * math.pi / 2:
        a = (u - (L - RC)) / RC
        p3 = (L - RC + RC * math.sin(a), W - RC + RC * math.cos(a), Z3)
    else:
        v = u - (L - RC) - RC * math.pi / 2
        if W - RC - v < 0.3: break
        p3 = (L, W - RC - v, Z3)
    railing.append(seg(p3, (p3[0], p3[1], Z3 + RAIL)))
    u += 1.0

# ---------- Rampe: Swoosh-Pfad (Route + Band) ----------
def run_front(off, u0, u1, z0, z1, n=26):
    return [(u0 + (u1 - u0) * i / n, W + off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_right(off, v0, v1, z0, z1, n=26):
    return [(L + off, v0 + (v1 - v0) * i / n, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_back(off, u0, u1, z0, z1, n=20):
    return [(u0 + (u1 - u0) * i / n, -off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_left(off, v0, v1, z0, z1, n=20):
    return [(-off, v0 + (v1 - v0) * i / n, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]

ROFF = 0.5   # Route: knapp vor der Fassade (zwischen Stuetzen und Wand)
# sichtbar: Vorplatz -> Front (0 -> Z1) -> runde Ecke -> rechte Seite (-> Z2)
seg1 = [(3.2, 17.2, 0), (1.4, 15.4, 0), (0.4, W + ROFF, 0.04)]
seg1 += run_front(ROFF, 0.5, L - RC, 0.05, Z1)
seg1 += corner_arc(ROFF, Z1, Z1 + 0.12)
seg1 += run_right(ROFF, W - RC, 0.4, Z1 + 0.12, Z2)
# verdeckt: Rueckseite (-> Z3-0.5) + linke Seite (-> Z3), Ankunft hinten links
seg2 = [seg1[-1], (L + 0.2, -0.4, Z2 + 0.04)]
seg2 += run_back(0.4, L - 0.6, 0.6, Z2 + 0.04, Z3 - 0.5)
seg2 += [(-0.35, 0.5, Z3 - 0.45)]
seg2 += run_left(0.35, 0.8, 3.6, Z3 - 0.45, Z3 - 0.12)
seg2 += [(0.3, 4.2, Z3)]
# sichtbar: Schlusslauf uebers Deck zur Wende
seg3 = [seg2[-1], (1.6, 4.5, Z3), (3.8, 4.9, Z3), (6.4, 5.4, Z3), (8.6, 6.2, Z3), (10.2, 7.2, Z3)]

segs = [(seg1, False), (seg2, True), (seg3, False)]
lens = [plen(s) for s, _ in segs]
start_pt = P(*seg1[0])
finish_pt = P(*seg3[-1])

# Rampenband (sichtbare Abschnitte): Doppellinie + Gelaenderlinie, BOFF hinter Stuetzen
BOFF = 0.06
band_pts = run_front(BOFF, 0.0, L - RC, 0.05, Z1) + corner_arc(BOFF, Z1, Z1 + 0.12) \
         + run_right(BOFF, W - RC, 0.2, Z1 + 0.12, Z2)
ramp.append(path(band_pts))
ramp.append(path([(x, y, z - 0.2) for (x, y, z) in band_pts]))
ramp.append(path([(x, y, z + 0.34) for (x, y, z) in band_pts]))   # Gelaender auf der Rampe

# ---------- Dach ----------
# DG-Band (verglast) an der Vorderkante + Terrasse
PV_Y0, PV_Y1, PH = W - 2.8, W - 0.9, 1.0
pav.append(path([(1.0, PV_Y0, Z3), (14.6, PV_Y0, Z3), (14.6, PV_Y1, Z3), (1.0, PV_Y1, Z3)], closed=True))
pav.append(path([(1.0, PV_Y0, Z3 + PH), (14.6, PV_Y0, Z3 + PH), (14.6, PV_Y1, Z3 + PH), (1.0, PV_Y1, Z3 + PH)], closed=True))
for (xx, yy) in ((1.0, PV_Y0), (14.6, PV_Y0), (14.6, PV_Y1), (1.0, PV_Y1)):
    pav.append(seg((xx, yy, Z3), (xx, yy, Z3 + PH)))
x = 1.5
while x < 14.3:
    pav.append(seg((x, PV_Y0, Z3 + 0.06), (x, PV_Y0, Z3 + PH - 0.06)))
    x += 0.55

# Parkfelder (zwei Reihen hinter dem DG-Band)
for i in range(8):
    x = 3.0 + i * 1.3
    deck.append(seg((x, 0.8, Z3), (x, 3.1, Z3)))
deck.append(seg((3.0, 0.8, Z3), (3.0 + 7 * 1.3, 0.8, Z3)))
deck.append(seg((3.0, 3.1, Z3), (3.0 + 7 * 1.3, 3.1, Z3)))
def box_top(x0, y0, x1, y1, z):
    return path([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], closed=True)
deck.append(box_top(5.7, 1.15, 6.6, 2.8, Z3 + 0.16))   # ein Wireframe-Auto
deck.append(box_top(5.9, 1.6, 6.4, 2.4, Z3 + 0.34))

# Wendeltreppen-Drum (rund, ragt ueber das Deck)
def drum(cx0, cy0, r, z0, z1, n=20):
    for zz in (z1,):
        pts = [(cx0 + r * math.cos(2 * math.pi * i / n), cy0 + r * math.sin(2 * math.pi * i / n), zz) for i in range(n + 1)]
        deck.append(path(pts))
    # Seitenkanten links/rechts (Tangenten)
    deck.append(seg((cx0 - r, cy0, z0), (cx0 - r, cy0, z1)))
    deck.append(seg((cx0 + r, cy0, z0), (cx0 + r, cy0, z1)))
    pts0 = [(cx0 + r * math.cos(math.pi * i / n), cy0 + r * math.sin(math.pi * i / n), z0) for i in range(n + 1)]
    deck.append(path(pts0))
drum(12.6, 4.0, 1.1, Z3, Z3 + 0.85)

# ---------- ENTER-Schriftzug auf dem Dach (vorderkante links) ----------
sx, sy = P(9.0, W - 0.9, Z3 + PH + 0.7)
sign.append(seg((8.7, W - 0.9, Z3 + PH), (8.7, W - 0.9, Z3 + PH + 0.55)))
sign.append(seg((15.0, W - 0.9, Z3 + PH), (15.0, W - 0.9, Z3 + PH + 0.55)))
sign.append(seg((8.7, W - 0.9, Z3 + PH + 0.55), (15.0, W - 0.9, Z3 + PH + 0.55)))
extra_svg.append(
    f'<text x="{sx:.1f}" y="{sy:.1f}" class="pl-sign" transform="rotate(30 {sx:.1f} {sy:.1f})">ENTER TECHNIKWELT</text>')

# ---------- Vorplatz-Raster ----------
for i in range(4):
    g = 1.2 + i * 1.1
    ground.append(seg((0.0, W + g, 0), (L * 0.75, W + g, 0)))
for i in range(5):
    gx = 1.0 + i * 2.6
    ground.append(seg((gx, W + 1.2, 0), (gx, W + 4.5, 0)))

# ---------- Labels ----------
def lbl(p3, dx, dy, at, text, anchor='start'):
    x, y = P(*p3)
    return (x, y, x + dx, y + dy, at, text, anchor)

labels = [
    lbl(seg1[0], 14, 44, 0.04, 'START / WECHSELZONE'),
    lbl((8.5, W + ROFF, 0.75), 46, 64, 0.16, 'RAMPE — AUSSEN UMLAUFEND'),
    lbl((L - RC + RC, W - RC, Z1 + 0.12), 56, 22, 0.32, '+1'),
    lbl((L + 0.4, 3.0, Z2 - 0.2), 54, -6, 0.42, '+2'),
    lbl((8.0, -0.4, Z3 - 0.9), 10, -54, 0.55, 'RÜCKSEITE — VERDECKT', anchor='middle'),
    lbl((-0.35, 2.2, Z3 - 0.3), -50, -8, 0.68, 'ANKUNFT DECK', anchor='end'),
    lbl(seg3[-1], 14, -44, 0.9, 'PARKDECK — WENDE', anchor='middle'),
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

svg = f'''<svg id="planSvg" viewBox="0 0 {vw:.0f} {vh:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="'IBM Plex Mono', monospace" aria-label="Isometrische Zeichnung der ENTER Technikwelt mit der Hillclimb-Route über die Aussenrampe aufs Parkdeck" role="img">
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

with open('plan2.svg', 'w') as f:
    preview = svg.replace('<svg ', '<svg style="background:#0D0C0B" ', 1)
    preview = re.sub(r'stroke-dashoffset="\d+"', 'stroke-dashoffset="0"', preview)
    style = '''<style>
.pg path, .pg ellipse {stroke:#F4F1EB; stroke-width:1; fill:none; opacity:.42}
.pg-main path {stroke-width:1.8; opacity:.95}
.pg-faint path {stroke-width:.6; opacity:.22}
.pg-hidden path {stroke-dasharray:4 5; opacity:.16}
.pg-ramp path {stroke-width:1.2; opacity:.6}
.route {stroke:#EE3829; stroke-width:4; fill:none; stroke-linejoin:round; stroke-linecap:round}
.route--hidden {stroke-width:2.2; opacity:.45}
.route-mask {stroke:#0D0C0B; stroke-width:3.5; fill:none; stroke-dasharray:5 7}
.pm-c,.pm-pulse {stroke:#EE3829; fill:none; stroke-width:1.5}
.pm-d {fill:#EE3829}
.pl-lead {stroke:#8A857C; stroke-width:1}
.pl-dot {fill:#F4F1EB}
.pl-txt {fill:#F4F1EB; font-size:15px; letter-spacing:2.5px}
.pl-sign {fill:#F4F1EB; font-size:13px; letter-spacing:3px; opacity:.8}
</style>'''
    f.write(preview.replace('</svg>', style + '</svg>'))

with open('plan2_embed.svg', 'w') as f:
    f.write(svg)

print(f"viewBox 0 0 {vw:.0f} {vh:.0f}")
print("Segmentlaengen px:", json.dumps([round(l) for l in lens]))
