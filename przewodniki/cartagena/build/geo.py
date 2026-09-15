# -*- coding: utf-8 -*-
"""Dane geograficzne przewodnika.

Geometria (linia brzegowa, mury, ulice, kwartały, place, akweny) pochodzi
z OpenStreetMap i leży w `maps/osm-data.json` — plik generuje `osm_build.py`.
Tutaj zostaje warstwa redakcyjna: które punkty trafiają na mapy, w jakiej
kategorii, pod jakim hasłem w tekście i w jakiej kolejności na trasach.

Współrzędne punktów są nadpisywane tymi z OSM wszędzie tam, gdzie udało się
dopasować obiekt po nazwie i rodzaju; reszta zostaje z ręcznego szkicu
(patrz raport z `osm_build.py`).

Dane: © OpenStreetMap contributors, ODbL.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "maps", "osm-data.json"), encoding="utf-8") as _f:
    OSM = json.load(_f)

ATTRIBUTION = OSM["attribution"]
BBOX = {k: tuple(v) for k, v in OSM["bbox"].items()}

# ---------- warstwy z OpenStreetMap ----------
_D = OSM["detail"]
WALLS = [[tuple(p) for p in w] for w in _D["walls"]]            # mury miejskie
COAST = [[tuple(p) for p in w] for w in _D["coast"]]            # linia brzegowa
STREETS = [(k, [tuple(p) for p in w]) for k, w in _D["streets"]]
BUILDINGS = [[tuple(p) for p in w] for w in _D["buildings"]]
SQUARES = [(n, [tuple(p) for p in w]) for n, w in _D["squares"]]
DISTRICTS = {n: [tuple(p) for p in w] for n, w in _D["districts"].items()}

AREAS = {k: {"name": v["name"], "cat": v["cat"],
             "rings": [[tuple(p) for p in r] for r in v["rings"]]}
         for k, v in OSM["areas"].items()}


def rings(key):
    return AREAS[key]["rings"]


# Gminy tworzące maskę lądu i akweny rysowane na wierzchu.
LAND_KEYS = ("R1343457", "R1448412", "R2460383", "R1448415",
             "R1448413", "R4062807", "R1324937", "R1448410")
WATER_KEYS = ("R18430278", "R20607558", "R20607560", "R4004791",
              "W25896749", "W238972766")

# Kwartały Starego Miasta wewnątrz murów (Centro + San Diego).
WALLED_CITY = [DISTRICTS[n] for n in ("Centro", "San Diego") if n in DISTRICTS]
GETSEMANI = DISTRICTS.get("Getsemaní", [])
LA_MATUNA = DISTRICTS.get("La Matuna", [])
EL_CABRERO = DISTRICTS.get("El Cabrero", [])

# ---------- POI ----------
# (id, nazwa na mapie, lat, lon, kategoria, anchor w markdownie)
# kategorie: hist (zabytek/muzeum), plaza (plac), fort (fortyfikacja),
#            view (widok), life (życie/jedzenie/muzyka), gate (brama)

_POI_BASE = [
 # --- MAPA 3: Stare Miasto (Centro + San Diego) ---
 ("3.1","Torre del Reloj",10.4227,-75.5480,"gate","**Torre del Reloj**"),
 ("3.2","Plaza de los Coches",10.42295,-75.54825,"plaza","**Plaza de los Coches**"),
 ("3.3","Portal de los Dulces",10.42305,-75.54845,"life","**Portal de los Dulces**"),
 ("3.4","Plaza de la Aduana",10.4233,-75.5489,"plaza","**Plaza de la Aduana**"),
 ("3.5","Plaza de San Pedro Claver",10.42300,-75.55000,"plaza","**Plaza de San Pedro Claver**"),
 ("3.6","Iglesia San Pedro Claver",10.42315,-75.55012,"hist","**Iglesia y Convento de San Pedro Claver**"),
 ("3.7","Museo de Arte Moderno",10.42288,-75.54985,"hist","**Museo de Arte Moderno (MAMCartagena)**"),
 ("3.8","Museo Naval del Caribe",10.42330,-75.55020,"hist","**Museo Naval del Caribe**"),
 ("3.9","Plaza de Bolívar",10.4243,-75.5505,"plaza","**Plaza de Bolívar**"),
 ("3.10","Palacio de la Inquisición",10.42420,-75.55082,"hist","**Palacio de la Inquisición**"),
 ("3.11","Museo del Oro Zenú",10.42443,-75.55032,"hist","**Museo del Oro Zenú**"),
 ("3.12","Catedral Santa Catalina",10.42458,-75.55022,"hist","**Katedra Świętej Katarzyny Aleksandryjskiej**"),
 ("3.13","Plaza Santo Domingo",10.42520,-75.55162,"plaza","**Plaza Santo Domingo**"),
 ("3.14","Iglesia Santo Domingo",10.42533,-75.55148,"hist","**Iglesia y Convento de Santo Domingo**"),
 ("3.15","Plaza de Santa Teresa",10.42360,-75.55105,"plaza","**Convento de Santa Teresa**"),
 ("3.16","Teatro Adolfo Mejía",10.42568,-75.55040,"hist","**Teatro Heredia**"),
 ("3.17","Claustro de La Merced – Gabo",10.42556,-75.55055,"hist","**Claustro de La Merced**"),
 ("3.18","Casa Marqués de Valdehoyos",10.42350,-75.54972,"hist","**Casa del Marqués de Valdehoyos**"),
 ("3.19","Plaza Fernández de Madrid",10.42642,-75.54962,"plaza","**Plaza Fernández de Madrid**"),
 ("3.20","Iglesia Santo Toribio",10.42628,-75.54982,"hist","**Iglesia de Santo Toribio de Mogrovejo**"),
 ("3.21","Plaza de San Diego",10.42710,-75.54942,"plaza","**Plaza de San Diego**"),
 ("3.22","Calle Segunda de Badillo",10.42680,-75.55002,"life","**Calle Segunda de Badillo**"),
 ("3.23","Convento Santa Clara (Sofitel)",10.42762,-75.55072,"hist","**Convento de Santa Clara**"),
 ("3.24","Las Bóvedas",10.42882,-75.54872,"fort","**Las Bóvedas**"),
 ("3.25","Bal. de Santa Catalina",10.42862,-75.54952,"fort","**Baluarte de Santa Catalina**"),
 ("3.26","Bal. de Santo Domingo",10.42605,-75.55238,"fort","**Baluarte de Santo Domingo**"),
 ("3.27","Bal. San Francisco Javier",10.42498,-75.55302,"view","**Baluarte de San Francisco Javier**"),
 ("3.28","Bal. de San Ignacio",10.42318,-75.55192,"fort","**Baluarte de San Ignacio**"),
 ("3.29","Puerta de Santo Domingo",10.42487,-75.55243,"gate","**Puerta de Santo Domingo**"),

 # --- MAPA 4: Getsemaní ---
 ("4.1","Muelle de los Pegasos",10.42222,-75.54742,"life","**Muelle de los Pegasos**"),
 ("4.2","Camellón de los Mártires",10.42188,-75.54718,"hist","**Camellón de los Mártires**"),
 ("4.3","Parque Centenario",10.42118,-75.54682,"life","**Parque Centenario**"),
 ("4.4","Puerta de la Media Luna",10.41892,-75.54682,"gate","**Puerta de la Media Luna**"),
 ("4.5","Calle de la Media Luna",10.41932,-75.54638,"life","**Calle de la Media Luna**"),
 ("4.6","Callejón Angosto",10.41945,-75.54608,"life","**Callejón Angosto**"),
 ("4.7","Calle del Espíritu Santo",10.41988,-75.54605,"life","**Calle del Espíritu Santo**"),
 ("4.8","Plaza de la Trinidad",10.41962,-75.54572,"plaza","**Plaza de la Trinidad**"),
 ("4.9","Iglesia Santísima Trinidad",10.41972,-75.54558,"hist","**Iglesia de la Santísima Trinidad**"),
 ("4.10","Calle del Arsenal",10.42028,-75.54432,"life","**Calle del Arsenal**"),
 ("4.11","Bal. del Reducto",10.42062,-75.54468,"fort","**Baluarte del Reducto**"),
 ("4.12","Centro de Convenciones",10.42132,-75.54612,"hist","**Centro de Convenciones**"),
 ("4.13","India Catalina",10.42082,-75.54402,"hist","**India Catalina**"),

 # --- MAPA 2: miasto ---
 ("2.1","Castillo San Felipe",10.42258,-75.53902,"fort","**Castillo San Felipe de Barajas**"),
 ("2.2","Zapatos Viejos",10.42218,-75.53852,"hist","**Monumento a los Zapatos Viejos**"),
 ("2.3","Cerro de la Popa",10.41722,-75.53222,"view","**Cerro de la Popa**"),
 ("2.4","Casa Museo Rafael Núñez",10.42982,-75.54742,"hist","**Casa Museo Rafael Núñez**"),
 ("2.5","Ermita del Cabrero",10.42952,-75.54702,"hist","**Ermita del Cabrero**"),
 ("2.6","Mercado de Bazurto",10.41102,-75.52302,"life","**Mercado de Bazurto**"),
 ("2.7","Fuerte del Pastelillo",10.41662,-75.54202,"fort","**Fuerte de San Sebastián del Pastelillo**"),
 ("2.8","Lotnisko Rafael Núñez",10.44242,-75.51302,"life","**Rafael Núñez (CTG)**"),
 ("2.9","La Boquilla",10.46702,-75.49402,"life","**La Boquilla**"),

 # --- MAPA 1: zatoka ---
 ("1.1","Bocagrande (kanał)",10.4005,-75.5640,"fort","**Bocagrande**"),
 ("1.2","Bocachica (cieśnina)",10.3232,-75.5652,"fort","**Bocachica**"),
 ("1.3","Fuerte San Fernando",10.3216,-75.5691,"fort","**Fuerte de San Fernando de Bocachica**"),
 ("1.4","Batería de San José",10.3238,-75.5638,"fort","**Batería de San José**"),
 ("1.5","Tierrabomba",10.3720,-75.5690,"life","**Tierrabomba**"),
 ("1.6","Barú / Playa Blanca",10.1750,-75.6720,"life","**Playa Blanca (Barú)**"),
 ("1.7","Islas del Rosario",10.1780,-75.7500,"life","**Islas del Rosario**"),
]

def _at(pid, la, lo):
    p = OSM["pois"].get(pid)
    return (p[0], p[1]) if p else (la, lo)


POIS = [(pid, nm, *_at(pid, la, lo), cat, anc)
        for pid, nm, la, lo, cat, anc in _POI_BASE]

# Skąd wzięła się współrzędna: "osm" — z obiektu w OpenStreetMap,
# "sasiedzi" — przesunięta razem z sąsiadami, brak klucza — ze szkicu autora.
POI_SOURCE = OSM.get("poi_source", {})
VERIFIED = [p[0] for p in _POI_BASE if POI_SOURCE.get(p[0]) == "osm"]
APPROX = [p[0] for p in _POI_BASE if POI_SOURCE.get(p[0]) != "osm"]


# --- TRASY SPACEROWE (lista id POI) ---
ROUTES = {
 "I":   ["4.1","4.2","4.3","3.1","3.2","3.4","3.5","3.18","3.9","3.12","3.13"],
 "II":  ["3.21","3.22","3.19","3.20","3.24","3.25","3.26"],
 "III": ["3.28","3.27","3.26","3.29","3.25","3.24","3.23"],
 "IV":  ["4.4","4.5","4.6","4.7","4.8","4.10","4.11","4.12"],
 "V":   ["2.1","2.2","2.3","2.4","2.5","2.6"],
}
