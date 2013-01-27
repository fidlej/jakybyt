# coding: utf-8

# template where page number %s will be replaced with 0-100
#TODO: update the URL
#HOME_LIST_URL_TEMPLATE = "http://www.sreality.cz/search_s.php?kind=flat&fce=1&lang=cz&k=4&ft=strakonice&pR=20&pN=%s&fmt=RSS"

ADDRESS_SUFFIX = ", Strakonice, Czech Republic"
CENTRAL_POINT = (49.261748, 13.903453)
SPAN = (0.3, 0.6)
AREA_NAMES = [u"Jihočeský"]
LOCALITY_NAMES = [u"Strakonice"]

# Bounds used for coloring warm zones
GEO_BOUNDS = (
        (CENTRAL_POINT[0] - SPAN[0], CENTRAL_POINT[1] - SPAN[1]),
        (CENTRAL_POINT[0] + SPAN[0], CENTRAL_POINT[1] + SPAN[1]))

NAME_MAPPING = {}
LOCALITY_CHOICES = []

# Cadastral districts
# http://www.cuzk.cz/Dokument.aspx?PRARESKOD=307&MENUID=104&AKCE=GEN:SEZNAM_KATUZ
DISTRICS = "Albrechtice, Bavorov, Bělčice, Bezdědovice, Bílsko u Vodňan, Blanice, Blatenka, Blatná, Bratronice, Brusy, Březí u Blatné, Budyně, Buzice, Cehnice, Chelčice, Chlum u Blatné, Chobot, Chrášťovice, Chvalšovice, Čavyně, Čečelovice, Čejetice, Čekanice, Čepřovice, Černětice, Černěves u Libějovic, Černíkov u Strakonic, Čestice, Čichtice, Číčenice, Dobrš, Dolní Poříčí, Domanice, Doubravice u Strakonic, Doubravice u Volyně, Drachkov u Strakonic, Drahenický Málkov, Drahonice, Dražejov u Strakonic, Drážov, Droužetice, Dřešín, Dřešínek, Dunovice, Hajany u Blatné, Hájek u Bavorova, Hajská, Hlupín, Hněvkov u Mačkova, Hodějov, Holušice u Mužetic, Horní Poříčí, Hornosín, Hoslovice, Hostišovice, Hoštice u Volyně, Hubenov u Třebohostic, Hvožďany u Vodňan, Jemnice u Oseka, Jetišov, Jindřichovice u Blatenky, Jinín, Jiřetice u Čepřovic, Kadov u Blatné, Kakovice u Volyně, Kalenice, Kaletice, Kapsova Lhota, Katovice, Kbelnice, Kladruby u Strakonic, Klínovice, Kloub, Kocelovice, Koclov, Koječín u Čepřovic, Kozlov nad Otavou, Kožlí u Myštic, Krajníčko, Kraselov, Krašlovice, Krejnice, Krty u Strakonic, Krušlov, Křepice u Vodňan, Křtětice, Kuřimany, Kváskovice, Kváskovice u Drážova, Láz u Radomyšle, Lažánky, Lažany u Doubravice, Leskovice u Radomyšle, Lhota pod Kůstrým, Libějovice, Libětice, Lidmovice, Litochovice u Volyně, Lnáře, Lnářský Málkov, Lom u Blatné, Mačkov, Makarov, Malá Turná, Malenice, Marčovice, Mečichov, Měkynec, Metly, Milčice u Čekanic, Milejovice, Milíkovice, Miloňovice, Míreč, Mladějovice, Mladotice u Kraselova, Mnichov, Modlešovice, Mračov, Mutěnice u Strakonic, Mužetice, Myštice, Nahořany u Čkyně, Nahošín, Nebřehovice, Němčice u Sedlice, Němčice u Volyně, Němětice, Nestanice, Netonice, Neuslužice, Nihošovice, Nišovice, Nová Ves u Strakonic, Nové Strakonice, Novosedly u Strakonic, Nuzín, Ohrazenice u Tažovic, Osek u Radomyšle, Pacelice, Paračov, Petrovice u Oseka, Pivkovice, Počátky u Volyně, Podolí u Strakonic, Podruhlí, Pohorovice, Pole, Pracejovice, Přechovice, Předmíř, Přední Ptákovice, Přední Zborovice, Předslavice, Přešťovice, Račí u Nišovic, Radčice u Vodňan, Radějovice u Netonic, Radešov u Čestic, Radkovice, Radomyšl, Radošovice u Strakonic, Rohozná u Rovné, Rojice, Rovná u Strakonic, Řepice, Řiště, Sedlice u Blatné, Sedlíkovice, Sedliště u Mladějovic, Sedlo u Horažďovic, Skaličany, Skály u Kváskovic, Skočice, Slaník, Sloučín, Smiradice, Sousedovice, Starov, Stožice, Strakonice, Strašice v Pošumaví, Strunkovice nad Volyňkou, Střela, Střelské Hoštice, Střelskohoštická Lhota, Střídka, Střítež u Volyně, Sudkovice, Sudoměř u Čejetic, Svaryšov, Svinětice, Škrobočov, Škůdra, Škvořetice, Štěchovice, Štěkeň, Švejcarova Lhota, Tažovice, Tchořovice, Tisov, Tourov, Truskovice, Třebohostice, Třešovice, Újezd u Vodňan, Újezdec u Bělčic, Úlehle, Úlehle u Předslavic, Únice, Útěšov, Uzenice, Uzeničky, Vacovice, Vahlovice, Velká Turná, Víska u Strakonic, Vitice u Vodňan, Vítkov u Štěkně, Vodňany, Vojnice, Volenice, Volyně, Vrbno, Všechlapy u Volyně, Výšice, Záboří u Blatné, Zadní Ptákovice, Zadní Zborovice, Zahorčice u Lnář, Zahorčice u Volyně, Záhrobí, Zálesí u Drážova, Záluží u Vodňan, Zámlyní, Závišín u Bělčic, Zechovice, Zorkovice, Zvotoky"

N_DISTRICS = 239

# known PSCs obtained by ../psc/get_pscs.sh
PSC_SET = frozenset((26242, 34201, 38411, 38473, 38601, 38701, 38706, 38711, 38715, 38716, 38719, 38731, 38732, 38733, 38734, 38735, 38736, 38737, 38742, 38743, 38751, 38752, 38756, 38771, 38772, 38773, 38775, 38801, 38901))

