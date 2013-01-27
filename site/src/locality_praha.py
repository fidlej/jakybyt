# coding: utf-8

# template where page number %s will be replaced with 1-100
# category_type_cb=1 ... Prodej
# category_main_cb=1 ... Byty
# rg[]=10 ... Praha
# sort=0 ... Newest first
HOME_LIST_URL_TEMPLATE = "http://sreality.cz/search?category_main_cb=1&rg[]=10&category_type_cb=1&sort=0&perPage=30&page=%s&rss=1"

ADDRESS_SUFFIX = ", Praha, Czech Republic"
CENTRAL_POINT = (50.087811, 14.42046)
SPAN = (0.3, 0.6)
AREA_NAMES = [u"Hlavní město Praha", u"Praha"]
LOCALITY_NAMES = [u"Prague"]

# Bounds used for coloring warm zones
GEO_BOUNDS = ((49.948, 14.258), (50.173, 14.706))

# Mapping from geocoder locality to proper locality name
NAME_MAPPING = {
        u"Praha": "Praha 1",
        }

# Mapping from locality name to one of locality choices
NAME_TO_CHOICE_MAPPING = {
        u"Kunratice": "Praha 4",
        u"Slivenec": "Praha 5",
        u"Suchdol": "Praha 6",
        u"Lysolaje": "Praha 6",
        u"Nebušice": "Praha 6",
        u"Přední Kopanina": "Praha 6",
        u"Troja": "Praha 7",
        u"Ďáblice": "Praha 8",
        u"Březiněves": "Praha 8",
        u"Dolní Chabry": "Praha 8",
        u"Šeberov": "Praha 11",
        u"Újezd u Průhonic": "Praha 11",
        u"Újezd": "Praha 11",
        u"Křeslice": "Praha 11",
        u"Libuš": "Praha 12",
        u"Řeporyje": "Praha 13",
        u"Dolní Počernice": "Praha 14",
        u"Dolní Měcholupy": "Praha 15",
        u"Štěrboholy": "Praha 15",
        u"Petrovice": "Praha 15",
        u"Dubeč": "Praha 15",
        u"Velká Chuchle": "Praha 16",
        u"Lochkov": "Praha 16",
        u"Zbraslav": "Praha 16",
        u"Lipence": "Praha 16",
        u"Zličín": "Praha 17",
        u"Čakovice": "Praha 19",
        u"Vinoř": "Praha 19",
        u"Satalice": "Praha 19",
        u"Klánovice": "Praha 21",
        u"Koloděje": "Praha 21",
        u"Běchovice": "Praha 21",
        u"Královice": "Praha 22",
        u"Nedvězí": "Praha 22",
        u"Kolovraty": "Praha 22",
        u"Benice": "Praha 22",
        }

LOCALITY_CHOICES = []
for i in range(1, 23):
    LOCALITY_CHOICES.append("Praha %s" % i)

# Prague and its cadastral districts
# Taken from:
# http://www.pis.cz/cz/praha/zakladni_info/spravni_cleneni_prahy
DISTRICS = u"Praha, Běchovice, Benice, Bohnice, Braník, Břevnov, Březiněves, Bubeneč, Čakovice, Černý Most, Čimice, Ďáblice, Dejvice, Dolní Chabry, Dolní Měcholupy, Dolní Počernice, Dubeč, Háje, Hájek u Uhříněvsi, Hloubětín, Hlubočepy, Hodkovičky, Holešovice, Holyně, Horní Měcholupy, Horní Počernice, Hostavice, Hostivař, Hradčany, Hrdlořezy, Chodov, Cholupice, Jinonice, Josefov, Kamýk, Karlín, Kbely, Klánovice, Kobylisy, Koloděje, Kolovraty, Komořany, Košíře, Královice, Krč, Křeslice, Kunratice, Kyje, Lahovice, Letňany, Lhotka, Libeň, Liboc, Libuš, Lipany u Kolovrat, Lipence, Lochkov, Lysolaje, Malá Chuchle, Malá Strana, Malešice, Michle, Miškovice, Modřany, Motol, Nebušice, Nedvězí u Říčan, Nové Město, Nusle, Petrovice, Písnice, Pitkovice, Podolí, Prosek, Přední Kopanina, Radlice, Radotín, Ruzyně, Řeporyje, Řepy, Satalice, Sedlec, Slivenec, Smíchov, Sobín, Staré Město, Stodůlky, Strašnice, Střešovice, Střížkov, Suchdol, Šeberov, Štěrboholy, Točná, Troja, Třebonice, Třeboradice, Uhříněves, Újezd nad Lesy, Újezd u Průhonic, Veleslavín, Velká Chuchle, Vinohrady, Vinoř, Vokovice, Vršovice, Vysočany, Vyšehrad, Záběhlice, Zadní Kopanina, Zbraslav, Zličín, Žižkov"

N_DISTRICS = 113

DISTRICS = u"Praha"
N_DISTRICS = 1

# PSCs obtained by ../psc/get_pscs.sh
PSC_SET = frozenset((10000,10100,10200,10300,10400,10600,10700,10800,10900,11000,11800,11900,12000,12800,13000,14000,14100,14200,14300,14700,14800,14900,15000,15018,15200,15300,15400,15500,15521,15531,15600,15800,15900,16000,16100,16200,16300,16400,16500,16900,17000,17100,18000,18100,18200,18400,18600,19000,19011,19012,19014,19015,19016,19017,19300,19600,19700,19800,19900,25226,25228))
