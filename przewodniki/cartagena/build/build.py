# -*- coding: utf-8 -*-
import re, os, sys, html, datetime
import markdown
from weasyprint import HTML, CSS
from geo import APPROX, POIS, ROUTES
import prep

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "PRZEWODNIK-CARTAGENA.md")
BASE = HERE
OUT = os.path.join(HERE, "..", "Cartagena-przewodnik.pdf")

ROUTE_COL = {"I":"#B4593A","II":"#1F4E5A","III":"#A98430","IV":"#3F7A5E","V":"#6B4E9E"}
ROUTE_NAME = {"I":"Spacer I · Serce","II":"Spacer II · San Diego",
              "III":"Spacer III · Mury","IV":"Spacer IV · Getsemaní",
              "V":"Spacer V · Poza murami"}

MAPS = {
 "1": dict(title="Jak broniono zatoki",
           cap="Mapa 1 · system obronny Cartageny, XVI–XVIII w.",
           extra=[("A","Castillo San Felipe de Barajas","fort"),
                  ("B","Cerro de la Popa","view"),
                  ("C","Fuerte del Pastelillo (Manga)","fort")],
           note="Linia kropkowana między cyplem Bocagrande a Tierrabombą to "
                "<i>Escollera</i> — podwodna tama Antonia de Arévalo (1771–1778). "
                "Krótsza linia w Bocachica oznacza łańcuch rozpinany między "
                "fortami. Strzałki pokazują, którędy wchodziły floty napastników."),
 "2": dict(title="Cartagena — plan miasta",
           cap="Mapa 2 · orientacja: dzielnice i punkty poza murami",
           extra=[("SM","Stare Miasto w murach (Centro + San Diego)","fort"),
                  ("GE","Getsemaní","plaza")],
           note="Fioletowa linia przerywana to trasa Spaceru V. Punkt 9 (La Boquilla) leży poza kadrem — znacznik przyklejono do krawędzi mapy. "
                "Manga jest wyspą na zatoce; La Popa to wzgórze o wysokości 148 m."),
 "3": dict(title="Stare Miasto w murach",
           cap="Mapa 3 · El Centro i San Diego — spacery I, II, III",
           extra=[], note="Kreskowany pas to zachowany obwód murów (w OSM: "
                "<i>barrier=city_wall</i>). Szare linie to rzeczywista siatka "
                "ulic, jasne bryły — rzuty budynków. Trasy spacerów poprowadzono "
                "po ulicach. Kropka z cienką kreską przy numerze oznacza, że "
                "znacznik odsunięto, by nie nachodził na sąsiedni."),
 "4": dict(title="Getsemaní",
           cap="Mapa 4 · dzielnica poza murem — Spacer IV",
           extra=[("★","Torre del Reloj — wejście do Starego Miasta","gate")],
           note="Linia przerywana to dzisiejsza granica dzielnicy Getsemaní "
                "według OpenStreetMap — obejmuje także tereny portowe nad "
                "zatoką, na których dawniej nie było zabudowy."),
}
MAP_ROUTES = {"1": [], "2": ["V"], "3": ["I","II","III"], "4": ["IV"]}


def approx_note(num):
    """Które punkty na tej mapie nie mają odpowiednika w OpenStreetMap."""
    ids = sorted((p.split(".")[1] for p in APPROX if p.startswith(num + ".")),
                 key=int)
    if not ids:
        return ""
    if num == "1":            # cieśniny, wyspy i archipelag — etykiety obszarów
        return (f' Numery {", ".join(ids)} oznaczają obszary (cieśniny, wyspy, '
                f'archipelag), a nie punkty — ustawiono je tam, gdzie czytelnie '
                f'opisują to, co pokazują.')
    lead = "Punkt" if len(ids) == 1 else "Punkty"
    verb = "jest przybliżony" if len(ids) == 1 else "są przybliżone"
    obj = "tego obiektu" if len(ids) == 1 else "tych obiektów"
    return (f' {lead} {", ".join(ids)} {verb} — OpenStreetMap albo nie zna '
            f'{obj} pod nazwami używanymi w książce, albo umieszcza '
            f'{"go" if len(ids) == 1 else "je"} gdzie indziej.')


def map_figure(num):
    cfg = MAPS[num]
    rows = []
    for pid, nm, la, lo, cat, _ in POIS:
        if pid.split(".")[0] != num:
            continue
        rows.append(f'<div class="c-{cat}"><b>{pid.split(".")[1]}</b>{html.escape(nm)}</div>')
    for lab, nm, cat in cfg["extra"]:
        rows.append(f'<div class="c-{cat}"><b>{lab}</b>{html.escape(nm)}</div>')
    key = ""
    if MAP_ROUTES[num]:
        key = '<div class="routekey">' + "".join(
            f'<span><i style="background:{ROUTE_COL[r]}"></i>{ROUTE_NAME[r]}</span>'
            for r in MAP_ROUTES[num]) + "</div>"
    return (f'<figure class="mapfig" id="mapa{num}">'
            f'<h2>{cfg["title"]}</h2>'
            f'<div class="cap">{cfg["cap"]}</div>'
            f'<img src="maps/mapa{num}.svg" alt="{cfg["title"]}">'
            f'<div class="maplegend">{"".join(rows)}</div>{key}'
            f'<div class="mapnote"><b>Uwaga:</b> rysunek map opiera się na '
            f'danych <i>OpenStreetMap</i> (© OpenStreetMap contributors, ODbL): '
            f'linia brzegowa, mury, ulice, kwartały i place mają rzeczywisty '
            f'przebieg. Mapy są jednak mocno uproszczone — służą do orientacji '
            f'w terenie, nie do nawigacji. {cfg["note"]}{approx_note(num)}</div>'
            f'</figure>')


def headings(md):
    """Nagłówki H1: id + nadtytuł w data-num; zwraca (md, spis treści)."""
    PART_TITLE = {"PIERWSZA": ("Księga pierwsza", "Historia"),
                  "DRUGA": ("Księga druga", "Jak czytać miasto"),
                  "TRZECIA": ("Księga trzecia", "Spacery"),
                  "CZWARTA": ("Księga czwarta", "Żywa Kolumbia"),
                  "PIĄTA": ("Księga piąta", "Literatura i legendy"),
                  "SZÓSTA": ("Księga szósta", "Praktyka")}
    toc, out, np_, ns = [], [], 0, 0
    for ln in md.split("\n"):
        if not ln.startswith("# "):
            out.append(ln); continue
        t = ln[2:].strip()
        m = re.match(r"^(\d+)\.\s+(.+)$", t)
        if t.startswith("KSIĘGA"):
            np_ += 1; hid = f"part{np_}"
            word = t.replace("KSIĘGA ", "").split("—", 1)[0].strip()
            num, title = PART_TITLE[word]
            out.append(f'# {title} {{: #{hid} .part data-num="{num}" }}')
            toc.append(("part", hid, f"{num} · {title}"))
        elif m:
            hid = f"ch{m.group(1)}"
            title = m.group(2).strip().replace("SPACER ", "Spacer ")
            out.append(f'# {title} {{: #{hid} data-num="Rozdział {m.group(1)}" }}')
            toc.append(("ch", hid, f"{m.group(1)}. {title}"))
        elif t.startswith("DODATEK"):
            lab, rest = t.split(":", 1)
            letter = lab.split()[1]
            hid = "app" + letter
            nice = f"Dodatek {letter}"
            out.append(f'# {rest.strip()} {{: #{hid} data-num="{nice}" }}')
            toc.append(("ch", hid, f"{nice} · {rest.strip()}"))
        elif t.startswith("EPILOG"):
            rest = t.split(":", 1)[1].strip()
            out.append(f'# {rest} {{: #epilog data-num="Epilog" }}')
            toc.append(("ch", "epilog", f"Epilog · {rest}"))
        elif t == "DODATKI":
            out.append(f'# Dodatki {{: #dodatki .part data-num="Aparat" }}')
            toc.append(("part", "dodatki", "Dodatki"))
        else:
            ns += 1; hid = f"s{ns}"
            title = t.capitalize() if t.isupper() else t
            out.append(f'# {title} {{: #{hid} }}')
            toc.append(("plain", hid, title))
    return "\n".join(out), toc


def toc_html(toc):
    li = []
    for kind, hid, label in toc:
        cls = ' class="part"' if kind == "part" else ""
        li.append(f'<li{cls}><a href="#{hid}">{html.escape(label)}</a></li>')
    maps = "".join(
        f'<li><a href="#mapa{n}">Mapa {n} · {MAPS[n]["title"]}</a></li>'
        for n in ("1", "2", "3", "4"))
    return ('<section class="toc"><h2>Spis treści</h2><ul>' + "".join(li)
            + '<li class="part">Mapy</li>' + maps + '</ul></section>')


COVER = '''<section class="cover"><div class="frame"></div><div class="frame2"></div>
<div class="inner">
  <div class="kicker">Przewodnik po starym mieście</div>
  <h1>Cartagena<span class="de">de Indias</span></h1>
  <div class="rule"></div>
  <div class="sub">Historia · Fortyfikacje · Spacery<br>Kuchnia · Muzyka · Praktyka</div>
  <div class="art">%s</div>
  <div class="quote">„Kocham cię, moje miasto, tak jak kocha się starą parę butów.”
  <span>Luis Carlos López, 1908</span></div>
</div></section>'''

GARITA = '''<svg width="150" height="118" viewBox="0 0 150 118">
 <g fill="none" stroke="#C9A46A" stroke-width="1.5">
  <path d="M75 8 L75 18"/>
  <path d="M46 40 Q75 12 104 40" />
  <path d="M46 40 L46 46 L104 46 L104 40"/>
  <path d="M52 46 L52 96 M98 46 L98 96"/>
  <path d="M52 96 Q75 104 98 96"/>
  <path d="M63 58 Q75 50 87 58 L87 76 L63 76 Z" stroke-width="1.1"/>
  <path d="M30 104 L120 104" stroke-width="2.2"/>
  <path d="M22 112 L128 112" stroke-width="1"/>
 </g>
 <circle cx="75" cy="8" r="2.6" fill="#C9A46A"/>
</svg>'''

FRONT = '''<section class="front">
<h2>Cartagena de Indias</h2>
<p class="colophon lead"><b>Ultradokładny przewodnik po Starym Mieście.</b>
Sześć części, trzydzieści cztery rozdziały, sześć tras spacerowych, cztery mapy
i pięć dodatków — od cywilizacji Zenú i założenia miasta w 1533 roku po to,
gdzie dziś zjeść <i>arepa de huevo</i> i ile zapłacić za taksówkę.</p>
<div class="colophon">
<p><b>Jak korzystać z odnośników do map.</b> Znaczki w rodzaju
<a class="mref" href="#mapa3">M3·13</a> odsyłają do numeru na mapie: <i>M3</i> to numer
mapy, <i>13</i> to numer punktu w jej legendzie. Odnośnik pojawia się przy
pierwszej wzmiance o danym miejscu w każdym rozdziale.</p>
<p><b>Oznaczenia w tekście.</b> Ramki opisane jako <i>Ciekawostka</i>,
<i>Mit</i>, <i>W terenie</i> i <i>Słowo</i> wyróżniają, odpowiednio: rzecz wartą
zapamiętania, powszechnie powtarzaną nieprawdę, wskazówkę praktyczną
i termin hiszpański.</p>
<p><b>O rzetelności.</b> Część danych historycznych — liczba osób przewiezionych
przez port niewolniczy, liczba ofiar Inkwizycji, liczba chrztów Pedra Clavera —
to szacunki, o których historycy się spierają. Wszędzie tam, gdzie liczba jest
sporna, jest to w tekście zaznaczone. Ceny, godziny otwarcia i nazwy lokali
zmieniają się szybko; traktuj je jako rzędy wielkości.</p>
<p><b>O mapach.</b> Mapy narysowano na danych <b>OpenStreetMap</b>
(© OpenStreetMap contributors, licencja ODbL): linia brzegowa, mury, ulice,
kwartały, place i granice dzielnic mają rzeczywisty przebieg, a trasy spacerów
biegną po ulicach. Rysunek jest jednak mocno uproszczony i służy do orientacji
— zrozumienia, co gdzie leży i jak biegną trasy — a nie do nawigacji. W terenie
użyj mapy offline (np. Organic Maps albo OsmAnd z pobranym obszarem
Bolívar/Cartagena) i wyszukuj miejsca po nazwie.</p>
<p style="margin-top:6mm">Wydanie pierwsze · %s</p>
</div></section>'''


def build():
    md = open(SRC, encoding="utf-8").read()
    md = prep.apply_corrections(md)
    md = prep.strip_toc(md)
    md = prep.strip_rules(md)
    md = prep.normalize_lists(md)

    # miejsca wstawienia map
    ins = [("# 5. Mury: dwieście lat budowy", "1"),
           ("# KSIĘGA PIERWSZA", "2"),
           ("# 17. SPACER I: Serce", "3"),
           ("# 20. SPACER IV: Getsemaní", "4")]
    for anchor, num in ins:
        if anchor not in md:
            sys.exit("Brak kotwicy mapy: " + anchor)
        md = md.replace(anchor, map_figure(num) + "\n\n" + anchor, 1)

    md, missing = prep.add_maprefs(md)
    if missing:
        print("  [i] POI bez odnośnika w tekście:", ", ".join(missing))
    md = prep.wrap_callouts(md)
    md = prep.inline_labels(md)
    md = prep.stop_numbers(md)
    md, toc = headings(md)

    body = markdown.markdown(
        md, extensions=["tables", "attr_list", "md_in_html", "smarty"],
        extension_configs={"smarty": {"substitutions": {
            "left-double-quote": "„", "right-double-quote": "”"}}})

    # akapit po nagłówku rozdziału dostaje inicjał
    body = re.sub(r'(</h1>\s*)<p>(\w)', r'\1<p class="dropcap"><span class="dc">\2</span>', body)

    doc = (f'<!doctype html><html lang="pl"><head><meta charset="utf-8">'
           f'<title>Cartagena de Indias — przewodnik po Starym Mieście</title>'
           f'<meta name="description" content="Ultradokładny przewodnik po '
           f'Starym Mieście Cartageny: historia kolonialna, fortyfikacje, '
           f'sześć spacerów, kuchnia, muzyka, praktyka. Cztery mapy.">'
           f'<meta name="keywords" content="Cartagena de Indias, Kolumbia, '
           f'przewodnik, Getsemaní, Blas de Lezo, Palenque, champeta">'
           f'</head><body>'
           + COVER % GARITA
           + FRONT % datetime.date.today().strftime("%B %Y")
           + toc_html(toc)
           + f'<main>{body}</main></body></html>')
    open(os.path.join(HERE, "book.html"), "w", encoding="utf-8").write(doc)

    css = [CSS(filename=os.path.join(HERE, "fonts.css"), base_url=BASE + "/"),
           CSS(filename=os.path.join(HERE, "book.css"))]
    HTML(string=doc, base_url=BASE + "/").write_pdf(OUT, stylesheets=css)
    print("PDF:", os.path.normpath(OUT), os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    build()
