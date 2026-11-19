#!/usr/bin/env python3
"""Schematy metod przedłużania rzęs (SVG). Naturalna rzęsa = szara, sztuczne = złote, punkt klejenia = kropka."""
import math, os, random
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'zdjecia', 'schematy')
NAT, GOLD, GOLD2, LID, GLUE = '#8F8576', '#E2C27E', '#F3DDA8', '#CFC4B1', '#FFF4D6'
W, H = 340, 190
CX, CY, R = 170, 300, 150
CY_LOW = -95
G = 11                     # punkt klejenia (odległość od powieki)
N = 9                      # naturalnych rzęs na schemacie
ANG = [62 + i * 7 for i in range(N)]   # stopnie

def pt(a, d=0, side=1):
    t = math.radians(a)
    if side == -1: return CX + (R + d) * math.cos(t), CY_LOW + (R + d) * math.sin(t)
    return CX + (R + d) * math.cos(t), CY - (R + d) * math.sin(t)

def lash(a, start, length, spread=0, curl=0.18, color=GOLD, w=1.6, side=1, op=1):
    """Rzęsa jako krzywa: od punktu `start` (odległość od powieki) w kierunku a+spread."""
    t = math.radians(a + spread)
    x0, y0 = pt(a, start, side)
    dx, dy = math.cos(t), -math.sin(t) * side
    x2, y2 = x0 + dx * length, y0 + dy * length
    # zakręt do góry (od oka)
    nx, ny = -dy * side, dx * side
    k = curl * length * (1 if math.cos(t) < 0 else -1) * 0
    cxp, cyp = x0 + dx * length * .55 + nx * 0, y0 + dy * length * .55 - curl * length * side
    return f'<path d="M{x0:.1f} {y0:.1f} Q{cxp:.1f} {cyp:.1f} {x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="{w}" fill="none" stroke-linecap="round" opacity="{op}"/>'

def lid(side=1):
    a0, a1 = 52, 128
    p = [pt(a, 0, side) for a in (a0, (a0 + a1) / 2, a1)]
    # łuk okręgu
    x0, y0 = pt(a0, 0, side); x1, y1 = pt(a1, 0, side)
    sweep = 0 if side == 1 else 1
    return f'<path d="M{x0:.1f} {y0:.1f} A{R} {R} 0 0 {sweep} {x1:.1f} {y1:.1f}" stroke="{LID}" stroke-width="3" fill="none" stroke-linecap="round"/>'

def glue(a, d=G, side=1):
    x, y = pt(a, d, side)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{GLUE}" stroke="#0E0C0A" stroke-width=".8"/>'

def natural(a, side=1, L=30):
    return lash(a, 0, L, curl=.06, color=NAT, w=2.6, side=side)

def svg(body, side=1, title=''):
    vb = '0 20 340 170' if side == 1 else '0 0 340 125'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}"><title>{title}</title>{body}</svg>'

def fan(a, n, spread, L, w):
    if n == 1: return lash(a, G, L, 0, w=w)
    return ''.join(lash(a, G, L * (1 - abs(i - (n - 1) / 2) / n * .12), -spread + 2 * spread * i / (n - 1), w=w) for i in range(n))

def classic(n_ext, spread, L=78, w=1.7, extra=None):
    b = lid()
    for a in ANG:
        b += fan(a, n_ext, spread, L, w)
        b += natural(a)
        b += glue(a)
    return b

def spike(a, L, n=7, w=1.1):
    """Zamknięty wachlarz – kępka zbiegająca się w szpic."""
    x0, y0 = pt(a, G); x2, y2 = pt(a, G + L)
    t = math.radians(a); dx, dy = math.cos(t), -math.sin(t); nx, ny = -dy, dx
    out = ''
    for i in range(n):
        s = (-1 + 2 * i / (n - 1)) * L * .10
        cx, cy = x0 + dx * L * .38 + nx * s, y0 + dy * L * .38 + ny * s
        out += f'<path d="M{x0:.1f} {y0:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" stroke="{GOLD}" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
    return out

S = {}
S['1-1'] = ('Metoda 1:1 – jedna sztuczna rzęsa na jedną naturalną', classic(1, 0, w=2.0))
S['2-1'] = ('Metoda 2:1 – dwie sztuczne rzęsy na jedną naturalną', classic(2, 5, w=1.7))
S['volume'] = ('Volume 5D–10D – wachlarz lekkich rzęs na jedną naturalną', classic(6, 12, w=.95))
S['hollywood'] = ('Hollywood 15D i Mega Volume 18D – gęsty wachlarz na jedną naturalną', classic(13, 15, L=82, w=.6))

b = lid()
for a in ANG: b += spike(a, 80) + natural(a) + glue(a)
S['wet'] = ('Wet Lashes – wachlarze zamknięte w „mokre” kępki', b)

b = lid()
for i, a in enumerate(ANG):
    b += spike(a, 98, n=5) if i % 2 else fan(a, 5, 11, 66, .95)
    b += natural(a) + glue(a)
S['wispy'] = ('Wispy – objętość z dłuższymi kępkami w rytmie', b)

b = lid(); lens = [70, 96, 78, 104, 74, 92, 80, 100, 72]
for a, L in zip(ANG, lens): b += spike(a, L, n=5) + natural(a) + glue(a)
S['medusa'] = ('Medusa – rozdzielone kępki o różnej długości', b)

S['mink'] = ('Mink/Silk – miękkie, matowe włókna 1:1–3:1', classic(2, 4, w=2.4))

b = lid()
for i, a in enumerate(ANG):
    b += spike(a, 94, n=6) if i % 2 else lash(a, G, 74, w=2.0)
    b += natural(a) + glue(a)
S['kim'] = ('Kim Kardashian – klasyka przeplatana dłuższymi kępkami', b)

# dolne rzęsy: powieka dolna (łuk w dół)
b = lid(-1)
for a in ANG: b += lash(a, 7, 40, curl=-.10, w=1.8, side=-1) + lash(a, 0, 20, curl=-.05, color=NAT, w=3, side=-1) + glue(a, 7, -1)
S['dolne'] = ('Dolne rzęsy – sztuczna rzęsa na każdej dolnej rzęsie', b, -1)

# konsultacja: same naturalne + lupa
b = lid()
for a in ANG: b += natural(a, L=40)
b += f'<circle cx="250" cy="72" r="26" stroke="{GOLD}" stroke-width="2.4" fill="none"/><path d="M269 91 L292 114" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>'
S['konsultacja'] = ('Konsultacja – ocena naturalnych rzęs przed doborem metody', b)

# laminacja: przed (proste, przerywane) i po (podkręcone)
b = lid()
for a in ANG:
    b += lash(a, 0, 50, spread=(a - 90) * 1.3, curl=-.05, color=NAT, w=2.2, op=.95).replace('/>', ' stroke-dasharray="3 4"/>')
    b += lash(a, 0, 52, spread=-(a - 90) * .35, curl=.30, color=GOLD, w=3)
S['laminacja'] = ('Lifting i laminacja – własne rzęsy podkręcone od nasady, bez doklejania', b)

os.makedirs(OUT, exist_ok=True)
for k, v in S.items():
    side = v[2] if len(v) > 2 else 1
    open(os.path.join(OUT, k + '.svg'), 'w').write(svg(v[1], side, v[0]))
print(len(S), 'schematów ->', OUT)
