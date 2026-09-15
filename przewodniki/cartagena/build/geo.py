# -*- coding: utf-8 -*-
"""Dane geograficzne (przybliżone) i punkty POI dla map przewodnika."""

# ---------- POI ----------
# (id, nazwa na mapie, lat, lon, kategoria, anchor w markdownie)
# kategorie: hist (zabytek/muzeum), plaza (plac), fort (fortyfikacja),
#            view (widok), life (życie/jedzenie/muzyka), gate (brama)

POIS = [
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

# ---------- obrysy ----------
WALLED_CITY = [
 (10.4231,-75.55192),(10.42270,-75.55100),(10.42240,-75.54975),(10.42255,-75.54878),
 (10.42272,-75.54798),(10.42350,-75.54772),(10.42480,-75.54762),(10.42620,-75.54770),
 (10.42760,-75.54792),(10.42868,-75.54852),(10.42892,-75.54888),(10.42800,-75.55050),
 (10.42690,-75.55178),(10.42605,-75.55238),(10.42498,-75.55302),(10.42400,-75.55258),
]

GETSEMANI = [
 (10.42200,-75.54760),(10.42150,-75.54628),(10.42172,-75.54488),(10.42098,-75.54382),
 (10.41960,-75.54382),(10.41852,-75.54520),(10.41862,-75.54700),(10.42000,-75.54782),
]

LA_MATUNA = [
 (10.42272,-75.54798),(10.42480,-75.54762),(10.42500,-75.54660),(10.42300,-75.54620),
 (10.42200,-75.54700),
]




# Woda: morze Karaibskie (NW) + Bahía de las Ánimas (S) jako jeden wielokąt,
# którego wewnętrzna krawędź biegnie dokładnie po murze i obrysie Getsemaní.
SEA_NW = [
 (10.43250,-75.55620),(10.41700,-75.55620),(10.41660,-75.54900),(10.41720,-75.54420),
 (10.41852,-75.54520),(10.41862,-75.54700),(10.42000,-75.54782),(10.42200,-75.54760),
 (10.42272,-75.54798),(10.42255,-75.54878),(10.42240,-75.54975),(10.42270,-75.55100),
 (10.42310,-75.55192),(10.42400,-75.55258),(10.42498,-75.55302),(10.42605,-75.55238),
 (10.42690,-75.55178),(10.42800,-75.55050),(10.42892,-75.54888),(10.43060,-75.55020),
 (10.43180,-75.55300),
]
BAY_S = SEA_NW

LAGUNA_CABRERO = [
 (10.42892,-75.54888),(10.43040,-75.54700),(10.43060,-75.54460),(10.42880,-75.54400),
 (10.42760,-75.54600),(10.42760,-75.54792),
]

# --- TRASY SPACEROWE (lista id POI) ---
ROUTES = {
 "I":   ["4.1","4.2","4.3","3.1","3.2","3.4","3.5","3.18","3.9","3.12","3.13"],
 "II":  ["3.21","3.22","3.19","3.20","3.24","3.25","3.26"],
 "III": ["3.28","3.27","3.26","3.29","3.25","3.24","3.23"],
 "IV":  ["4.4","4.5","4.6","4.7","4.8","4.10","4.11","4.12"],
 "V":   ["2.1","2.2","2.3","2.4","2.5","2.6"],
}
