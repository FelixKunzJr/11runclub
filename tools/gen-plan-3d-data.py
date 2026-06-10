#!/usr/bin/env python3
"""Exportiert die v5-Geometrie (gen_plan5.py) als 3D-Daten fuer Three.js.

Gleiche Modellwelt wie das SVG (x: Ost->West, y: Sued->Nord, z: hoch),
aber unprojiziert: Polylinien-Gruppen + Route + Labels als kompaktes JSON.
"""
import math, json

def ease(t):
    return t * t * (3 - 2 * t)

L, W = 15.0, 13.0
Z1, Z2, Z3 = 1.35, 2.65, 3.95
RAIL = 0.3

groups = {'main': [], 'grid': [], 'faint': [], 'hidden': [], 'ramp': [], 'deck': []}

def add(g, *pts):
    groups[g].append([[round(v, 2) for v in p] for p in pts])

def addline(g, pts):
    groups[g].append([[round(v, 2) for v in p] for p in pts])

# ---------- Silhouette / Kanten ----------
add('main', (0, W, 0), (0, W, Z3))
add('main', (L, W, 0), (L, W, Z3))
add('main', (L, 0, 0), (L, 0, Z3))
add('main', (0, 0, 0), (0, 0, Z3))
addline('main', [(0, W, 0), (L, W, 0), (L, 0, 0)])
addline('main', [(0, W, Z3), (L, W, Z3), (L, 0, Z3), (0, 0, Z3), (0, W, Z3)])
addline('hidden', [(0, 0, 0), (L, 0, 0)])
addline('hidden', [(0, 0, 0), (0, W, 0)])
for z in (Z1, Z2):
    addline('hidden', [(0, W, z), (0, 0, z), (L, 0, z)])

# ---------- Fascia-Baender ----------
for z in (Z1, Z2, Z3):
    for dz in (0.0, -0.22):
        addline('grid', [(0, W + 0.02, z + dz), (L + 0.02, W + 0.02, z + dz), (L + 0.02, 0, z + dz)])

# ---------- Stuetzen ----------
for x in range(0, 16, 2):
    add('grid', (x, W + 0.02, 0), (x, W + 0.02, Z3))
for y in range(1, 13, 2):
    add('grid', (L + 0.02, y, 0), (L + 0.02, y, Z3))
# Rueckseiten-Stuetzen dezent (in 3D sichtbar beim Drehen)
for x in range(0, 16, 2):
    add('faint', (x, -0.02, 0), (x, -0.02, Z3))
for y in range(1, 13, 2):
    add('faint', (-0.02, y, 0), (-0.02, y, Z3))

# ---------- EG Saeulengang Nord ----------
add('faint', (0, W - 1.8, 0), (L, W - 1.8, 0))
add('faint', (0, W - 1.8, Z1 - 0.22), (L, W - 1.8, Z1 - 0.22))
for x in range(1, 16, 2):
    add('faint', (x, W - 1.8, 0), (x, W - 1.8, Z1 - 0.22))

# ---------- Wellblech ----------
def clad_n(x0, x1, z0, z1, step=0.34):
    x = x0 + step
    while x < x1 - 0.05:
        add('faint', (x, W - 0.3, z0 + 0.08), (x, W - 0.3, z1 - 0.26))
        x += step
def clad_w(y0, y1, z0, z1, step=0.34):
    y = y0 + step
    while y < y1 - 0.05:
        add('faint', (L - 0.3, y, z0 + 0.08), (L - 0.3, y, z1 - 0.26))
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

# ---------- Gelaender (alle 4 Kanten — in 3D drehbar) ----------
addline('faint', [(0, W, Z3 + RAIL), (L, W, Z3 + RAIL), (L, 0, Z3 + RAIL), (0, 0, Z3 + RAIL), (0, W, Z3 + RAIL)])
for x in range(0, 16):
    add('faint', (x, W, Z3), (x, W, Z3 + RAIL))
    add('faint', (x, 0, Z3), (x, 0, Z3 + RAIL))
for y in range(0, 13):
    add('faint', (L, y, Z3), (L, y, Z3 + RAIL))
    add('faint', (0, y, Z3), (0, y, Z3 + RAIL))

# ---------- Route ----------
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

def run_east(off, y0, y1, z0, z1, n=22):
    return [(-off, y0 + (y1 - y0) * (i / n), z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_south(off, x0, x1, z0, z1, n=22):
    return [(x0 + (x1 - x0) * (i / n), -off, z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]
def run_west(off, y0, y1, z0, z1, n=26):
    return [(L + off, y0 + (y1 - y0) * (i / n), z0 + (z1 - z0) * ease(i / n)) for i in range(n + 1)]

RO = 0.30
def route_up(off):
    pts = [(1.8, W + 3.4, 0), (0.9, W + 1.3, 0), (0.7, W + off, 0.02)]
    pts += corner((0.7, W + off), (-off, W - 0.8), 0.02, 0.12)
    pts += run_east(off, W - 0.9, 0.9, 0.12, Z1)
    pts += corner((-off, 0.8), (0.8, -off), Z1, Z1 + 0.14)
    pts += run_south(off, 0.9, L - 0.9, Z1 + 0.14, Z2)
    pts += corner((L - 0.8, -off), (L + off, 0.8), Z2, Z2 + 0.14)
    pts += run_west(off, 0.9, W - 0.9, Z2 + 0.14, Z3)
    pts += corner((L + off, W - 0.8), (L - 0.6, W - 0.8), Z3, Z3)
    return pts

up = route_up(RO)
arrive = up[-1]
lap = [arrive,
       (L - 0.8, W - 1.8, Z3 + 0.02), (L - 0.8, 4.4, Z3 + 0.02), (L - 1.8, 3.5, Z3 + 0.02),
       (3.0, 3.4, Z3 + 0.02), (2.1, 4.3, Z3 + 0.02), (2.1, W - 1.6, Z3 + 0.02),
       (3.2, W - 0.9, Z3 + 0.02), (7.0, W - 0.9, Z3 + 0.02), (11.0, W - 1.0, Z3 + 0.02),
       (L - 1.6, W - 0.9, Z3 + 0.02), arrive]
down = list(reversed(route_up(RO - 0.14)))
down += [(0.95, W + 1.35, 0), (1.85, W + 3.35, 0)]
route = up + lap[1:] + down
n_up, n_lap = len(up), len(lap) - 1

# ---------- Dach ----------
BX0, BX1, BY0, BY1, BH = 2.0, 13.0, 0.7, 2.9, 1.05
addline('deck', [(BX0, BY0, Z3 + BH), (BX1, BY0, Z3 + BH), (BX1, BY1, Z3 + BH), (BX0, BY1, Z3 + BH), (BX0, BY0, Z3 + BH)])
addline('deck', [(BX0, BY0, Z3), (BX1, BY0, Z3), (BX1, BY1, Z3), (BX0, BY1, Z3), (BX0, BY0, Z3)])
for (xx, yy) in ((BX0, BY0), (BX1, BY0), (BX1, BY1), (BX0, BY1)):
    add('deck', (xx, yy, Z3), (xx, yy, Z3 + BH))
x = BX0 + 0.5
while x < BX1 - 0.2:
    add('faint', (x, BY1, Z3 + 0.06), (x, BY1, Z3 + BH - 0.06))
    x += 0.55

DRUM = {'c': [7.5, W - 2.8], 'r': 1.1, 'z0': Z3, 'z1': Z3 + 0.9}
n = 28
for zz in (DRUM['z0'], DRUM['z1']):
    addline('deck', [(DRUM['c'][0] + DRUM['r'] * math.cos(2 * math.pi * i / n),
                      DRUM['c'][1] + DRUM['r'] * math.sin(2 * math.pi * i / n), zz) for i in range(n + 1)])

# (Parkfelder, Auto und Schildrahmen entfernt — Club-Feedback Juni 2026)

# Rampe als durchgehendes Band um Ost-, Sued- und Westfassade:
# wird im Frontend als Ribbon-Mesh mit hellen Kanten gebaut,
# damit die Rampe im Drahtmodell wirklich sichtbar ist.
BOFF = 0.14
band_path = corner((1.2, W + BOFF), (-BOFF, W - 1.0), 0.04, 0.12)
band_path += run_east(BOFF, W - 1.1, 0.9, 0.12, Z1)
band_path += corner((-BOFF, 0.8), (0.8, -BOFF), Z1, Z1 + 0.14)
band_path += run_south(BOFF, 0.9, L - 0.9, Z1 + 0.14, Z2)
band_path += corner((L - 0.8, -BOFF), (L + BOFF, 0.8), Z2, Z2 + 0.14)
band_path += run_west(BOFF, 0.9, W - 0.6, Z2 + 0.14, Z3)

# ---------- Vorplatz ----------
for i in range(4):
    g = 1.2 + i * 1.1
    add('faint', (0.0, W + g, 0), (L * 0.55, W + g, 0))
for i in range(4):
    gx = 0.8 + i * 2.4
    add('faint', (gx, W + 1.2, 0), (gx, W + 4.5, 0))

# ---------- Labels ----------
labels = [
    {'p': [1.8, W + 3.4, 0.05], 'at': 0.03, 't': 'START / WECHSELZONE'},
    {'p': [0.5, W + 0.5, 0.3], 'at': 0.07, 't': 'EINSTIEG — LINKS'},
    {'p': [-0.5, 6.5, 1.1], 'at': 0.18, 't': 'OSTSEITE'},
    {'p': [8.0, -0.5, Z1 + 0.9], 'at': 0.32, 't': 'RECHTS — SÜDSEITE'},
    {'p': [L + 0.5, 4.0, Z2 + 0.6], 'at': 0.45, 't': 'RECHTS — WESTSEITE'},
    {'p': [L - 0.7, W - 0.8, Z3 + 0.3], 'at': 0.56, 't': 'AUSSTIEG — DACH'},
    {'p': [4.0, 5.5, Z3 + 0.3], 'at': 0.68, 't': 'EINE RUNDE OBEN'},
    {'p': [L + 0.4, 10.5, Z2 + 0.2], 'at': 0.84, 't': 'RUNTER — GLEICHE STRECKE'},
]

data = {
    'L': L, 'W': W, 'H': Z3, 'BH': BH,
    'block': [BX0, BY0, BX1, BY1, BH],
    'drum': DRUM,
    'groups': groups,
    'route': [[round(v, 2) for v in p] for p in route],
    'band': [[round(v, 2) for v in p] for p in band_path],
    'fracUp': round(n_up / len(route), 3),
    'fracLap': round((n_up + n_lap) / len(route), 3),
    'labels': labels,
}
js = json.dumps(data, separators=(',', ':'))
with open('plan3d_data.json', 'w') as f:
    f.write(js)
print('Punkte Route:', len(route), '· JSON kB:', round(len(js) / 1024, 1))
