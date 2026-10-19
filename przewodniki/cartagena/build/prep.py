# -*- coding: utf-8 -*-
"""Przygotowanie markdownu: korekty, ramki, odnośniki do map, numery przystanków."""
import re
from geo import POIS

MAPTITLE = {"1": "M1", "2": "M2", "3": "M3", "4": "M4"}

CAL = [("🔍", "fact"), ("⚠️", "myth"), ("📍", "field"), ("💬", "word")]
EMO = {e: c for e, c in CAL}

STOPS = {"①":1,"②":2,"③":3,"④":4,"⑤":5,"⑥":6,"⑦":7,"⑧":8,"⑨":9,
         "⑩":10,"⑪":11,"⑫":12,"⑬":13}

CORRECTIONS = [
    # prochy Gabo leżą w Claustro de La Merced (obok Teatru Heredia), nie w San Agustín
    ("""## Convento de San Agustín / Universidad de Cartagena

Augustianie. Dziś **Uniwersytet w Cartagenie**, założony w 1827 roku. W przylegającym **Claustro de la Merced** złożono w 2016 roku **prochy Gabriela Garcíi Márqueza** — w niewielkim monumencie z jego popiersiem.""",
     """## Convento de San Agustín / Universidad de Cartagena

Augustianie. Dziś **Uniwersytet w Cartagenie**, założony w 1827 roku. Uczelnia zajmuje kilka dawnych klasztorów rozsianych po Starym Mieście.

W jednym z nich — **Claustro de La Merced**, przylegającym do Teatru Adolfo Mejía — złożono w 2016 roku **prochy Gabriela Garcíi Márqueza**, w niewielkim monumencie z jego popiersiem."""),
]


def apply_corrections(md):
    for a, b in CORRECTIONS:
        if a not in md:
            raise SystemExit("KOREKTA nie pasuje:\n" + a[:90])
        md = md.replace(a, b)
    return md


def normalize_lists(md):
    """Python-Markdown wymaga pustej linii przed listą; GitHub nie.
    Dopisujemy brakujące odstępy, żeby listy nie zlewały się w akapit."""
    ITEM = re.compile(r"^(\s*)([-*+] |\d+\. )")
    out = []
    for ln in md.split("\n"):
        if (ITEM.match(ln) and out and out[-1].strip()
                and not ITEM.match(out[-1]) and not out[-1].lstrip().startswith("|")
                and not out[-1].lstrip().startswith("<")
                and not out[-1].startswith("#")):
            out.append("")
        out.append(ln)
    return "\n".join(out)


def strip_rules(md):
    """Usuwa poziome linie '---' — w książce rolę separatora pełnią otwarcia
    rozdziałów, a samotny <hr> potrafi zostać sam na stronie."""
    out, prev_blank = [], True
    for ln in md.split("\n"):
        if ln.strip() in ("---", "***", "___") and prev_blank:
            continue
        out.append(ln)
        prev_blank = not ln.strip()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


def strip_toc(md):
    """Usuwa ręczny spis treści — PDF dostaje generowany, z numerami stron."""
    i = md.index("# SPIS TREŚCI")
    j = md.index("---\n---\n\n# PROLOG")
    return md[:i] + md[j:]


VARIANTS = {
 "3.1": ["Torre del Reloj", "Puerta del Reloj"],
 "3.2": ["Plaza de los Coches"],
 "3.3": ["Portal de los Dulces"],
 "3.4": ["Plaza de la Aduana"],
 "3.5": ["Plaza de San Pedro Claver"],
 "3.6": ["Iglesia y Convento de San Pedro Claver", "Iglesia de San Pedro Claver"],
 "3.7": ["Museo de Arte Moderno"],
 "3.8": ["Museo Naval del Caribe"],
 "3.9": ["Plaza de Bolívar"],
 "3.10": ["Palacio de la Inquisición"],
 "3.11": ["Museo del Oro Zenú"],
 "3.12": ["Katedra Świętej Katarzyny Aleksandryjskiej", "Katedra Santa Catalina",
          "Katedrę Santa Catalina", "katedry Santa Catalina"],
 "3.13": ["Plaza Santo Domingo"],
 "3.14": ["Iglesia y Convento de Santo Domingo", "Iglesia de Santo Domingo",
          "kościoła Santo Domingo", "wieża Santo Domingo", "Krzywa wieża Santo Domingo"],
 "3.15": ["Convento de Santa Teresa", "Hotel Charleston Santa Teresa"],
 "3.16": ["Teatro Heredia", "Teatro Adolfo Mejía"],
 "3.17": ["Claustro de La Merced"],
 "3.18": ["Casa del Marqués de Valdehoyos"],
 "3.19": ["Plaza Fernández de Madrid"],
 "3.20": ["Iglesia de Santo Toribio de Mogrovejo", "Santo Toribio"],
 "3.21": ["Plaza de San Diego"],
 "3.22": ["Calle Segunda de Badillo"],
 "3.23": ["Convento de Santa Clara", "klasztoru Santa Clara", "Sofitel Santa Clara",
          "klasztor Santa Clara", "Santa Clara"],
 "3.24": ["Las Bóvedas"],
 "3.25": ["Baluarte de Santa Catalina"],
 "3.26": ["Baluarte de Santo Domingo"],
 "3.27": ["Baluarte de San Francisco Javier", "Café del Mar"],
 "3.28": ["Baluarte de San Ignacio"],
 "3.29": ["Puerta de Santo Domingo"],
 "4.1": ["Muelle de los Pegasos"],
 "4.2": ["Camellón de los Mártires"],
 "4.3": ["Parque Centenario"],
 "4.4": ["Puerta de la Media Luna"],
 "4.5": ["Calle de la Media Luna"],
 "4.6": ["Callejón Angosto"],
 "4.7": ["Calle del Espíritu Santo"],
 "4.8": ["Plaza de la Trinidad"],
 "4.9": ["Iglesia de la Santísima Trinidad"],
 "4.10": ["Calle del Arsenal"],
 "4.11": ["Baluarte del Reducto"],
 "4.12": ["Centro de Convenciones"],
 "4.13": ["India Catalina"],
 "2.1": ["Castillo San Felipe de Barajas", "Castillo San Felipe", "San Felipe de Barajas"],
 "2.2": ["Zapatos Viejos"],
 "2.3": ["Cerro de la Popa"],
 "2.4": ["Casa Museo Rafael Núñez"],
 "2.5": ["Ermita del Cabrero"],
 "2.6": ["Mercado de Bazurto", "Bazurto"],
 "2.7": ["Fuerte de San Sebastián del Pastelillo", "Fuerte del Pastelillo"],
 "2.8": ["Rafael Núñez (CTG)"],
 "2.9": ["La Boquilla"],
 "1.1": ["Escollera de Bocagrande", "Escollera"],
 "1.2": ["Bocachica"],
 "1.3": ["Fuerte de San Fernando de Bocachica", "San Fernando"],
 "1.4": ["Batería de San José"],
 "1.5": ["Tierrabomba"],
 "1.6": ["Playa Blanca"],
 "1.7": ["Islas del Rosario"],
}
BADGE = {p[0]: f'M{p[0].split(".")[0]}\u00b7{p[0].split(".")[1]}' for p in POIS}


def add_maprefs(md):
    """Odnośnik do mapy przy pierwszej wzmiance o miejscu w każdym rozdziale.
    Dodatki i epilog pomijamy — tam badge tylko zaśmieca."""
    pairs = []
    for pid, variants in VARIANTS.items():
        for v in variants:
            pairs.append((v, pid))
    pairs.sort(key=lambda x: -len(x[0]))

    lines = md.split("\n")
    chapter, seen, hits, stop = 0, set(), set(), False
    for n, ln in enumerate(lines):
        if ln.startswith("# "):
            chapter += 1
            t = ln[2:]
            if t.startswith("DODAT") or t.startswith("EPILOG"):
                stop = True
        if (stop or ln.startswith("# ") or ln.startswith("|")
                or ln.lstrip().startswith("<figure")):
            continue
        taken = []
        for name, pid in pairs:
            if (pid, chapter) in seen:
                continue
            for m in re.finditer(re.escape(name), ln):
                if any(m.start() < b and m.end() > a for a, b in taken):
                    continue
                taken.append((m.start(), m.end()))
                seen.add((pid, chapter)); hits.add(pid)
                tag = (f' <a class="mref" href="#mapa{pid.split(".")[0]}">'
                       f'{BADGE[pid]}</a>')
                ln = ln[:m.end()] + tag + ln[m.end():]
                taken = [(a, b) if b <= m.end() else
                         (a + len(tag), b + len(tag)) for a, b in taken]
                break
        lines[n] = ln
    return "\n".join(lines), [p[0] for p in POIS if p[0] not in hits]


def wrap_callouts(md):
    """Grupuje akapity ramek w bloki <div class='cal cal-x'>."""
    DEF = {"fact": "Ciekawostka", "myth": "Mit", "field": "W terenie",
           "word": "Słowo"}
    HEAD = re.compile(r"^\*\*(🔍|⚠️|📍|💬)\s*([^*]+?)\*\*")
    CONT = re.compile(r"^(- |\* |\d+\. )")
    blocks = md.split("\n\n")
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        m = HEAD.match(b.strip())
        if not m:
            out.append(b); i += 1; continue
        kind = EMO[m.group(1)]
        full = m.group(2).rstrip(".:— ").strip()
        if len(full) <= 30:
            label = full
            lead = re.sub(r"^\*\*(🔍|⚠️|📍|💬)\s*[^*]+?\*\*\s*", "",
                          b.strip(), count=1)
        else:
            # zbyt długi nagłówek ramki: zostaje w treści jako wytłuszczenie
            label = DEF[kind]
            lead = re.sub(r"^\*\*(🔍|⚠️|📍|💬)\s*", "**", b.strip(), count=1)
        body = [lead]
        i += 1
        while i < len(blocks):
            nxt = blocks[i].strip()
            if not nxt or not (CONT.match(nxt) or nxt[:1].islower()):
                break
            body.append(blocks[i]); i += 1
        out.append(f'<div class="cal cal-{kind}" markdown="1">'
                   f'<span class="lbl">{label}</span>\n\n'
                   + "\n\n".join(body) + "\n\n</div>")
    return "\n\n".join(out)


def inline_labels(md):
    """Znaczniki ramek, które zostały wewnątrz list i akapitów, zamienia
    na etykiety tekstowe (bez emoji — w druku i tak się nie składają)."""
    def rep(m):
        k = EMO[m.group(1)]
        return f'<b class="ilbl ilbl-{k}">{m.group(2).strip()}</b>'
    md = re.sub(r"\*\*(🔍|⚠️|📍|💬)\s*([^*]+?)\*\*", rep, md)
    return re.sub(r"[🔍⚠️📍💬]\uFE0F?\s*", "", md)


def stop_numbers(md):
    for ch, n in STOPS.items():
        md = md.replace("### " + ch + " ", f'### <span class="stopnum">{n}</span>')
        md = md.replace(ch + " ", f'<span class="stopnum">{n}</span>')
        md = md.replace(ch, f'<span class="stopnum">{n}</span>')
    return md


def chapter_numbers(md):
    """'# 7. Miasto niewolników' -> nagłówek z nadtytułem 'ROZDZIAŁ 7'."""
    def rep(m):
        return f'# <span class="num">Rozdział {m.group(1)}</span>{m.group(2)}'
    md = re.sub(r"^# (\d+)\.\s+(.+)$", rep, md, flags=re.M)
    md = re.sub(r"^# (KSIĘGA [^\n]+)$",
                lambda m: f'# {{.part}}<span class="num">Część</span>{m.group(1)}',
                md, flags=re.M)
    md = re.sub(r"^# (DODATEK [A-E]): (.+)$",
                lambda m: f'# <span class="num">{m.group(1)}</span>{m.group(2)}',
                md, flags=re.M)
    return md
