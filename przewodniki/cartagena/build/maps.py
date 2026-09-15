# -*- coding: utf-8 -*-
"""Generator schematycznych map wektorowych (SVG) do przewodnika."""
import math
from geo import (POIS, WALLED_CITY, GETSEMANI, LA_MATUNA, SEA_NW, BAY_S,
                 LAGUNA_CABRERO, ROUTES)

C = dict(
    paper="#FBF7EF", land="#F2EADA", land2="#E9DFCB", water="#CFE0DF",
    water2="#B9D2D2", wall="#8A4A2E", wallf="#D9BFA6", ink="#23201C",
    muted="#8A8175", accent="#B4593A", teal="#1F4E5A", gold="#A98430",
    grid="#E3D8C3",
)
CAT = dict(hist="#B4593A", plaza="#A98430", fort="#7A3E22",
           view="#1F4E5A", life="#3F7A5E", gate="#6B4E9E")

P = {p[0]: p for p in POIS}


class Proj:
    def __init__(self, bbox, w, h, pad=14):
        (la0, lo0, la1, lo1) = bbox
        self.la0, self.lo0, self.la1, self.lo1 = la0, lo0, la1, lo1
        k = math.cos(math.radians((la0 + la1) / 2))
        dw, dh = (lo1 - lo0) * k, (la1 - la0)
        s = min((w - 2 * pad) / dw, (h - 2 * pad) / dh)
        self.s, self.k = s, k
        self.ox = pad + ((w - 2 * pad) - dw * s) / 2
        self.oy = pad + ((h - 2 * pad) - dh * s) / 2
        self.w, self.h = w, h

    def __call__(self, lat, lon):
        return (self.ox + (lon - self.lo0) * self.k * self.s,
                self.oy + (self.la1 - lat) * self.s)

    def metres(self, m):          # długość m metrów w jednostkach SVG
        return (m / 111320.0) * self.s


def path(pr, pts, close=True):
    d = "".join(("M" if i == 0 else "L") + f"{pr(*p)[0]:.1f},{pr(*p)[1]:.1f}"
                for i, p in enumerate(pts))
    return d + ("Z" if close else "")


def smooth(pr, pts):
    """Łagodna polilinia (Catmull-Rom → Bézier) dla tras spacerowych."""
    q = [pr(*p) for p in pts]
    if len(q) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in q)
    d = f"M{q[0][0]:.1f},{q[0][1]:.1f}"
    for i in range(len(q) - 1):
        p0 = q[i - 1] if i else q[0]
        p1, p2 = q[i], q[i + 1]
        p3 = q[i + 2] if i + 2 < len(q) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
              f"{p2[0]:.1f},{p2[1]:.1f}")
    return d


def marker(x, y, label, cat, r=8.2):
    col = CAT.get(cat, C["accent"])
    fs = 8.0 if len(label) <= 2 else 6.9
    return (f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" '
            f'stroke="{col}" stroke-width="1.9"/>'
            f'<text x="{x:.1f}" y="{y + fs*0.36:.1f}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="{fs}" '
            f'font-weight="600" fill="{col}">{label}</text></g>')


def area_label(x, y, t, size=10, col=None, ls=2.2, op=1.0, anchor="middle"):
    """Rozstrzelenie robimy WŁASNYMI spacjami, nie letter-spacing: renderery
    SVG liczą szerokość tekstu bez letter-spacing i psują wyśrodkowanie."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="Archivo, sans-serif" font-size="{size}" '
            f'font-weight="600" letter-spacing="{ls}" fill-opacity="{op}" '
            f'fill="{col or C["muted"]}">{t}</text>')


def scalebar(pr, x, y, metres=200):
    L = pr.metres(metres)
    return (f'<g stroke="{C["ink"]}" stroke-width="1.1">'
            f'<line x1="{x}" y1="{y}" x2="{x+L:.1f}" y2="{y}"/>'
            f'<line x1="{x}" y1="{y-3}" x2="{x}" y2="{y+3}"/>'
            f'<line x1="{x+L:.1f}" y1="{y-3}" x2="{x+L:.1f}" y2="{y+3}"/></g>'
            f'<text x="{x+L/2:.1f}" y="{y-6}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="7.5" '
            f'fill="{C["muted"]}">{metres} m</text>')


def north(x, y):
    return (f'<g><path d="M{x},{y-13} L{x-4.5},{y+5} L{x},{y+1.6} '
            f'L{x+4.5},{y+5} Z" fill="{C["ink"]}"/>'
            f'<text x="{x}" y="{y+15}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="8" '
            f'font-weight="600" fill="{C["ink"]}">N</text></g>')


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">'
            f'<defs><pattern id="hatch" width="5" height="5" '
            f'patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
            f'<line x1="0" y1="0" x2="0" y2="5" stroke="{C["wall"]}" '
            f'stroke-width="1.5" opacity=".30"/></pattern>'
            f'<pattern id="wave" width="14" height="10" '
            f'patternUnits="userSpaceOnUse">'
            f'<path d="M0,5 q3.5,-3.4 7,0 t7,0" fill="none" '
            f'stroke="{C["water2"]}" stroke-width="1.05"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')


def routes_svg(pr, keys, dash=True):
    cols = {"I": "#B4593A", "II": "#1F4E5A", "III": "#A98430",
            "IV": "#3F7A5E", "V": "#6B4E9E"}
    out = []
    for k in keys:
        pts = [(P[i][2], P[i][3]) for i in ROUTES[k] if i in P]
        if len(pts) < 2:
            continue
        d = smooth(pr, pts)
        out.append(f'<path d="{d}" fill="none" stroke="#fff" '
                   f'stroke-width="5.4" stroke-linecap="round" opacity=".75"/>')
        da = ' stroke-dasharray="7 4.5"' if dash else ''
        out.append(f'<path d="{d}" fill="none" stroke="{cols[k]}" '
                   f'stroke-width="2.4" stroke-linecap="round"{da}/>')
    return "".join(out)


def decluster(pts, rmin=19.0, iters=140):
    """Rozsuwa nachodzące znaczniki, zachowując pozycję zbliżoną do oryginału."""
    cur = [list(p) for p in pts]
    for _ in range(iters):
        moved = False
        for i in range(len(cur)):
            for j in range(i + 1, len(cur)):
                dx = cur[j][0] - cur[i][0]
                dy = cur[j][1] - cur[i][1]
                d = math.hypot(dx, dy) or 0.01
                if d < rmin:
                    push = (rmin - d) / 2 * 0.62
                    ux, uy = dx / d, dy / d
                    cur[i][0] -= ux * push; cur[i][1] -= uy * push
                    cur[j][0] += ux * push; cur[j][1] += uy * push
                    moved = True
        for k, (ox, oy) in enumerate(pts):        # lekkie przyciąganie do źródła
            cur[k][0] += (ox - cur[k][0]) * 0.05
            cur[k][1] += (oy - cur[k][1]) * 0.05
        if not moved:
            break
    return [tuple(p) for p in cur]


def markers_block(pr, prefix):
    sel = [p for p in POIS if p[0].startswith(prefix)]
    orig = [pr(p[2], p[3]) for p in sel]
    new = decluster(orig)
    out = []
    for (ox, oy), (nx, ny) in zip(orig, new):
        if math.hypot(nx - ox, ny - oy) > 3.5:
            out.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{nx:.1f}" '
                       f'y2="{ny:.1f}" stroke="{C["muted"]}" '
                       f'stroke-width="0.7" opacity=".7"/>')
            out.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="1.5" '
                       f'fill="{C["muted"]}"/>')
    for (p, (nx, ny)) in zip(sel, new):
        out.append(marker(nx, ny, p[0].split(".")[1], p[4]))
    return "".join(out)



# ===================== MAPA 1 — obrona zatoki =====================
MAINLAND1 = [(10.4500,-75.5250),(10.4400,-75.5310),(10.4330,-75.5385),
             (10.4300,-75.5445),(10.4230,-75.5470),(10.4150,-75.5425),
             (10.4050,-75.5400),(10.3900,-75.5335),(10.3750,-75.5255),
             (10.3600,-75.5185),(10.3400,-75.5135),(10.3200,-75.5120),
             (10.2900,-75.5150),(10.2900,-75.4880),(10.4500,-75.4880)]
BOCAGRANDE1 = [(10.4230,-75.5470),(10.4248,-75.5548),(10.4150,-75.5578),
               (10.4050,-75.5648),(10.3960,-75.5712),(10.3905,-75.5742),
               (10.3878,-75.5712),(10.3975,-75.5648),(10.4080,-75.5578),
               (10.4180,-75.5508),(10.4215,-75.5478)]
TIERRABOMBA = [(10.4000,-75.5618),(10.3900,-75.5578),(10.3750,-75.5558),
               (10.3600,-75.5578),(10.3450,-75.5618),(10.3330,-75.5680),
               (10.3370,-75.5792),(10.3600,-75.5832),(10.3850,-75.5778),
               (10.3990,-75.5698)]
BARU1 = [(10.3245,-75.5700),(10.3020,-75.5702),(10.2880,-75.5900),
         (10.2880,-75.6120),(10.3110,-75.6055),(10.3232,-75.5822)]
OLDTOWN1 = [(10.4228,-75.5478),(10.4225,-75.5518),(10.4260,-75.5524),
            (10.4289,-75.5489),(10.4276,-75.5479),(10.4248,-75.5476)]


def map1(w=560, h=660):
    pr = Proj((10.2860, -75.6180, 10.4520, -75.4900), w, h, pad=16)
    s = [head(w, h)]
    s.append(f'<rect width="{w}" height="{h}" fill="{C["water"]}"/>')
    s.append(f'<rect width="{w}" height="{h}" fill="url(#wave)" opacity=".5"/>')
    for poly in (MAINLAND1, BOCAGRANDE1, TIERRABOMBA, BARU1):
        s.append(f'<path d="{path(pr, poly)}" fill="{C["land"]}" '
                 f'stroke="{C["muted"]}" stroke-width="0.85"/>')
    s.append(f'<path d="{path(pr, OLDTOWN1)}" fill="{C["wallf"]}" '
             f'stroke="{C["wall"]}" stroke-width="1.8"/>')

    # Escollera de Bocagrande (podwodna tama, 1771–1778)
    a, b = pr(10.3902, -75.5735), pr(10.3998, -75.5628)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
             f'y2="{b[1]:.1f}" stroke="{C["accent"]}" stroke-width="3.2" '
             f'stroke-dasharray="2 3.2"/>')
    # łańcuch w Bocachica
    a, b = pr(10.3332, -75.5682), pr(10.3243, -75.5700)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
             f'y2="{b[1]:.1f}" stroke="{C["accent"]}" stroke-width="2.4" '
             f'stroke-dasharray="1.6 2.4"/>')

    def arrow(pts, col, lab, lx, ly, anchor="start"):
        d = smooth(pr, pts)
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.1" '
                 f'stroke-dasharray="9 5" opacity=".9"/>')
        x, y = pr(*pts[-1])
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>')
        px, py = pr(lx, ly)
        s.append(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" '
                 f'font-family="Archivo, sans-serif" font-size="7.8" '
                 f'font-weight="600" fill="{col}">{lab}</text>')
    arrow([(10.4180,-75.6100),(10.4080,-75.5900),(10.3985,-75.5760),
           (10.3980,-75.5680),(10.4060,-75.5600),(10.4180,-75.5530)],
          C["teal"], "DRAKE 1586 → przez Bocagrande", 10.4330, -75.6120)
    arrow([(10.3000,-75.6000),(10.3180,-75.5790),(10.3290,-75.5692),
           (10.3500,-75.5520),(10.3800,-75.5470),(10.4080,-75.5455),
           (10.4180,-75.5470)],
          "#7A3E22", "VERNON 1741 · POINTIS 1697 → przez Bocachica", 10.4265, -75.6120)

    ids = ["1.1","1.2","1.3","1.4","1.5","1.6","1.7"]
    extra = [("A",10.4226,-75.5390,"fort"),("B",10.4172,-75.5322,"view"),
             ("C",10.4130,-75.5420,"fort")]
    pts, labs = [], []
    for pid in ids:
        if pid not in P:
            continue
        _, _, la, lo, cat, _ = P[pid]
        if not (pr.la0 <= la <= pr.la1 and pr.lo0 <= lo <= pr.lo1):
            continue
        pts.append(pr(la, lo)); labs.append((pid.split(".")[1], cat))
    for lab, la, lo, cat in extra:
        pts.append(pr(la, lo)); labs.append((lab, cat))
    new = decluster(pts, rmin=20)
    for (ox, oy), (nx, ny), (lab, cat) in zip(pts, new, labs):
        if math.hypot(nx-ox, ny-oy) > 3.5:
            s.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{nx:.1f}" '
                     f'y2="{ny:.1f}" stroke="{C["muted"]}" stroke-width="0.7"/>')
        s.append(marker(nx, ny, lab, cat))

    s.append(area_label(*pr(10.4380,-75.5900), "MORZE KARAIBSKIE", 9.4, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.3720,-75.5430), "BAHÍA DE", 9, C["teal"], 2.2, .8))
    s.append(area_label(*pr(10.3660,-75.5430), "CARTAGENA", 9, C["teal"], 2.2, .8))
    s.append(area_label(*pr(10.3660,-75.5700), "TIERRABOMBA", 7.8, C["muted"], 1.8))
    s.append(area_label(*pr(10.2960,-75.5960), "BARÚ", 7.8, C["muted"], 1.8))
    s.append(area_label(*pr(10.4105,-75.5600), "Bocagrande", 7, C["muted"], .8))
    s.append(area_label(*pr(10.4330,-75.5540), "Stare Miasto", 7.4, C["wall"], .8))
    s.append(area_label(*pr(10.4180,-75.5120), "LĄD STAŁY", 8.4, C["muted"], 2.4))
    s.append(area_label(*pr(10.2930,-75.5560), "↓ Islas del Rosario · Playa Blanca", 7, C["teal"], .6, .9))
    s.append(scalebar(pr, 30, 150, 5000))
    s.append(north(w - 32, 40))
    s.append('</svg>')
    return "".join(s)


# ===================== MAPA 2 — plan miasta =====================
SEA2 = [(10.4620,-75.5790),(10.4620,-75.5210),(10.4480,-75.5290),
        (10.4390,-75.5362),(10.4324,-75.5432),(10.4302,-75.5468),
        (10.42892,-75.54888),(10.42800,-75.55050),(10.42690,-75.55178),
        (10.42605,-75.55238),(10.42498,-75.55302),(10.42400,-75.55258),
        (10.42310,-75.55192),(10.4180,-75.5528),(10.4100,-75.5568),
        (10.4020,-75.5628),(10.3950,-75.5690),(10.3900,-75.5732),
        (10.3850,-75.5790)]
BAY2 = [(10.3866,-75.5722),(10.3975,-75.5650),(10.4080,-75.5580),
        (10.4180,-75.5510),(10.4215,-75.5480),(10.42240,-75.54975),
        (10.42255,-75.54878),(10.42272,-75.54798),(10.42200,-75.54760),
        (10.42000,-75.54782),(10.41862,-75.54700),(10.41852,-75.54520),
        (10.4170,-75.5444),(10.4130,-75.5418),(10.4080,-75.5394),
        (10.4020,-75.5388),(10.3950,-75.5410),(10.3890,-75.5462),
        (10.3862,-75.5542)]
MANGA2 = [(10.4185,-75.5438),(10.4175,-75.5398),(10.4128,-75.5372),
          (10.4082,-75.5394),(10.4078,-75.5442),(10.4120,-75.5462),
          (10.4165,-75.5458)]
LAGUNAS2 = [(10.4302,-75.5468),(10.4318,-75.5420),(10.4292,-75.5378),
            (10.4238,-75.5392),(10.4232,-75.5442),(10.4268,-75.5474)]
CHAMBACU2 = [(10.4226,-75.5452),(10.4248,-75.5420),(10.4224,-75.5396),
             (10.4192,-75.5412),(10.4192,-75.5444)]


def map2(w=560, h=590):
    pr = Proj((10.3860, -75.5780, 10.4570, -75.5090), w, h, pad=16)
    s = [head(w, h)]
    s.append(f'<rect width="{w}" height="{h}" fill="{C["land"]}"/>')
    for poly in (SEA2, BAY2, LAGUNAS2, CHAMBACU2):
        s.append(f'<path d="{path(pr, poly)}" fill="{C["water"]}" '
                 f'stroke="{C["water2"]}" stroke-width="0.9"/>')
        s.append(f'<path d="{path(pr, poly)}" fill="url(#wave)" opacity=".5"/>')
    s.append(f'<path d="{path(pr, MANGA2)}" fill="{C["land"]}" '
             f'stroke="{C["muted"]}" stroke-width="0.9"/>')
    # wzgórze La Popa
    x, y = pr(10.4172, -75.5322)
    s.append(f'<path d="M{x-34},{y+16} Q{x},{y-26} {x+34},{y+16} Z" '
             f'fill="{C["land2"]}" stroke="{C["muted"]}" stroke-width="0.9"/>')
    s.append(f'<path d="{path(pr, GETSEMANI)}" fill="{C["land2"]}" '
             f'stroke="{C["wall"]}" stroke-width="1.1" stroke-dasharray="3.5 2.5"/>')
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="{C["wallf"]}" '
             f'stroke="{C["wall"]}" stroke-width="2.4"/>')
    s.append(routes_svg(pr, ["V"]))

    ids = ["2.1","2.2","2.3","2.4","2.5","2.6","2.7","2.8"]
    pts, labs = [], []
    for pid in ids:
        _, _, la, lo, cat, _ = P[pid]
        la = min(max(la, pr.la0 + 0.0035), pr.la1 - 0.0035)
        lo = min(max(lo, pr.lo0 + 0.0035), pr.lo1 - 0.0035)
        pts.append(pr(la, lo)); labs.append((pid.split(".")[1], cat))
    new_ = decluster(pts, rmin=20)
    for (ox, oy), (nx, ny), (lab, cat) in zip(pts, new_, labs):
        if math.hypot(nx-ox, ny-oy) > 3.5:
            s.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{nx:.1f}" '
                     f'y2="{ny:.1f}" stroke="{C["muted"]}" stroke-width="0.7"/>')
        s.append(marker(nx, ny, lab, cat))
    x, y = pr(10.4255, -75.5502)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{C["wall"]}"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" text-anchor="middle" '
             f'font-family="Archivo, sans-serif" font-size="8.6" '
             f'font-weight="600" fill="#fff">SM</text>')
    x, y = pr(10.4196, -75.5457)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.8" fill="{C["accent"]}"/>'
             f'<text x="{x:.1f}" y="{y+3.0:.1f}" text-anchor="middle" '
             f'font-family="Archivo, sans-serif" font-size="7.6" '
             f'font-weight="600" fill="#fff">GE</text>')

    s.append(area_label(*pr(10.4450,-75.5570), "MORZE", 9.2, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.4415,-75.5570), "KARAIBSKIE", 9.2, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.3990,-75.5508), "BAHÍA DE", 8.2, C["teal"], 2, .8))
    s.append(area_label(*pr(10.3955,-75.5508), "CARTAGENA", 8.2, C["teal"], 2, .8))
    s.append(area_label(*pr(10.4060,-75.5590), "BOCAGRANDE", 8, C["muted"], 2))
    s.append(area_label(*pr(10.3940,-75.5680), "EL LAGUITO", 6.6, C["muted"], 1))
    s.append(area_label(*pr(10.4122,-75.5412), "MANGA", 7.2, C["muted"], 1.4))
    s.append(area_label(*pr(10.4348,-75.5452), "EL CABRERO", 6.8, C["muted"], 1.2))
    s.append(area_label(*pr(10.4148,-75.5322), "LA POPA", 7, C["muted"], 1.4))
    s.append(area_label(*pr(10.4074,-75.5262), "PIE DE LA POPA", 6.6, C["muted"], 1.2))
    s.append(area_label(*pr(10.4520,-75.5120), "La Boquilla ↗", 7, C["teal"], .6, .9, "end"))
    s.append(area_label(*pr(10.3935,-75.5120), "Turbaco · Barranquilla ↘", 6.8, C["muted"], .6, .85, "end"))
    s.append(area_label(*pr(10.4148,-75.5228), "Bazurto", 6.6, C["muted"], .6))
    s.append(scalebar(pr, 30, h - 26, 1000))
    s.append(north(w - 32, 40))
    s.append('</svg>')
    return "".join(s)


PLAZAS = {"3.2":(16,11),"3.4":(24,15),"3.5":(20,13),"3.9":(23,16),
          "3.13":(18,13),"3.15":(14,10),"3.19":(16,12),"3.21":(15,11),
          "4.8":(17,13),"4.3":(26,17)}


def plaza_rects(pr, ids):
    out = []
    for pid in ids:
        if pid not in P:
            continue
        _, _, la, lo, _, _ = P[pid]
        x, y = pr(la, lo)
        w_, h_ = PLAZAS[pid]
        out.append(f'<rect x="{x-w_/2:.1f}" y="{y-h_/2:.1f}" width="{w_}" '
                   f'height="{h_}" rx="2.5" fill="{C["land2"]}" '
                   f'stroke="{C["muted"]}" stroke-width="0.6" opacity=".9"/>')
    return "".join(out)


def street_grid(pr, poly, cid, step=26, ang=(34, 124)):
    """Delikatna siatka sugerująca układ ulic, przycięta do obrysu."""
    out = [f'<clipPath id="{cid}"><path d="{path(pr, poly)}"/></clipPath>',
           f'<g clip-path="url(#{cid})" stroke="{C["muted"]}" '
           f'stroke-width="0.55" opacity=".33">']
    for a in ang:
        r = math.radians(a)
        dx, dy = math.cos(r), math.sin(r)
        for i in range(-60, 61):
            cx, cy = pr.w / 2 - dy * i * step, pr.h / 2 + dx * i * step
            out.append(f'<line x1="{cx-dx*900:.0f}" y1="{cy-dy*900:.0f}" '
                       f'x2="{cx+dx*900:.0f}" y2="{cy+dy*900:.0f}"/>')
    out.append('</g>')
    return "".join(out)


def map3(w=560, h=660):
    pr = Proj((10.4208, -75.5552, 10.4304, -75.5444), w, h, pad=16)
    s = [head(w, h)]
    s.append(f'<rect width="{w}" height="{h}" fill="{C["land"]}"/>')
    for poly in (SEA_NW, LAGUNA_CABRERO):
        s.append(f'<path d="{path(pr, poly)}" fill="{C["water"]}"/>')
        s.append(f'<path d="{path(pr, poly)}" fill="url(#wave)" opacity=".55"/>')
    s.append(f'<path d="{path(pr, LA_MATUNA)}" fill="{C["land2"]}" '
             f'stroke="{C["muted"]}" stroke-width="0.6" opacity=".8"/>')
    s.append(f'<path d="{path(pr, GETSEMANI)}" fill="{C["land2"]}" '
             f'stroke="{C["muted"]}" stroke-width="0.7" opacity=".75"/>')
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="{C["land"]}"/>')
    s.append(street_grid(pr, WALLED_CITY, "c3"))
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="none" '
             f'stroke="url(#hatch)" stroke-width="7" opacity="1"/>')
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="none" '
             f'stroke="{C["wall"]}" stroke-width="5" opacity=".55"/>')
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="none" '
             f'stroke="{C["wall"]}" stroke-width="1.2"/>')
    s.append(plaza_rects(pr, [k for k in PLAZAS if k.startswith("3.")]))
    s.append(routes_svg(pr, ["I", "II", "III"]))
    s.append(markers_block(pr, "3."))
    s.append(area_label(*pr(10.42760,-75.54950), "SAN DIEGO", 9, C["muted"], 3, .38))
    s.append(area_label(*pr(10.42360,-75.55230), "EL CENTRO", 9, C["muted"], 3, .38))
    s.append(area_label(*pr(10.42420,-75.54690), "LA MATUNA", 6.4, C["muted"], 1.4, .8))
    s.append(area_label(*pr(10.41960,-75.54620), "GETSEMANÍ", 7, C["muted"], 1.6, .8))
    s.append(area_label(*pr(10.42830,-75.55300), "MORZE", 8.4, C["teal"], 2.2, .85))
    s.append(area_label(*pr(10.42740,-75.55300), "KARAIBSKIE", 8.4, C["teal"], 2.2, .85))
    s.append(area_label(*pr(10.42050,-75.55000), "BAHÍA DE LAS ÁNIMAS", 7, C["teal"], 1.6, .8))
    s.append(area_label(*pr(10.42950,-75.54620), "Laguna del Cabrero", 6.2, C["teal"], .6, .8))
    s.append(scalebar(pr, 30, h - 26, 200))
    s.append(north(w - 32, 40))
    s.append('</svg>')
    return "".join(s)


def map4(w=560, h=500):
    pr = Proj((10.4174, -75.5496, 10.4236, -75.5418), w, h, pad=16)
    s = [head(w, h)]
    s.append(f'<rect width="{w}" height="{h}" fill="{C["land"]}"/>')
    for poly in (SEA_NW,):
        s.append(f'<path d="{path(pr, poly)}" fill="{C["water"]}"/>')
        s.append(f'<path d="{path(pr, poly)}" fill="url(#wave)" opacity=".55"/>')
    s.append(f'<path d="{path(pr, LA_MATUNA)}" fill="{C["land2"]}" '
             f'stroke="{C["muted"]}" stroke-width="0.6"/>')
    s.append(f'<path d="{path(pr, WALLED_CITY)}" fill="{C["land2"]}" '
             f'stroke="{C["wall"]}" stroke-width="4" opacity=".75"/>')
    s.append(f'<path d="{path(pr, GETSEMANI)}" fill="{C["land"]}"/>')
    s.append(street_grid(pr, GETSEMANI, "c4", step=20, ang=(28, 118)))
    s.append(f'<path d="{path(pr, GETSEMANI)}" fill="none" '
             f'stroke="{C["wall"]}" stroke-width="1.6" '
             f'stroke-dasharray="6 3"/>')
    s.append(plaza_rects(pr, [k for k in PLAZAS if k.startswith("4.")]))
    s.append(routes_svg(pr, ["IV"]))
    s.append(markers_block(pr, "4."))
    x, y = pr(10.4227, -75.5480)
    s.append(marker(x, y, "★", "gate", 9))
    s.append(area_label(*pr(10.4192,-75.5452), "GETSEMANÍ", 9, C["muted"], 2.6))
    s.append(area_label(*pr(10.42290,-75.54930), "STARE MIASTO", 7.4, C["wall"], 1.6, .9))
    s.append(area_label(*pr(10.4196,-75.54880), "BAHÍA DE LAS ÁNIMAS", 7, C["teal"], 1.4, .8))
    s.append(scalebar(pr, 30, h - 26, 150))
    s.append(north(w - 32, 38))
    s.append('</svg>')
    return "".join(s)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "maps"), exist_ok=True)
    for n, fn in ((1, map1), (2, map2), (3, map3), (4, map4)):
        open(os.path.join(here, f"maps/mapa{n}.svg"), "w").write(fn())
        print("mapa", n, "ok")
