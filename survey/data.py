# wipe the DB:
# rm db.sqlite3
# source venv/bin/activate
# python manage.py migrate

PEOPLE = [
    {"name": "Karla Čulo", "sex": "F"},
    {"name": "Marija Dumančić", "sex": "F"},
    {"name": "Tea Fruk", "sex": "F"},
    {"name": "Marija Gršić", "sex": "F"},
    {"name": "Franka Holjevac", "sex": "F"},
    {"name": "Nika Inđić", "sex": "F"},
    {"name": "Ema Jurač", "sex": "F"},
    {"name": "Mia Karlovčan", "sex": "F"},
    {"name": "Katarina Kunjko", "sex": "F"},
    {"name": "Mia Marton", "sex": "F"},
    {"name": "Sofija Matejić", "sex": "F"},
    {"name": "Ana Šimić", "sex": "F"},
    {"name": "Aleksandar Topolnik", "sex": "M"},
    {"name": "Lili Topolnik", "sex": "F"},
    {"name": "Marko Topolnik", "sex": "M"},
    {"name": "Tijana Gojić Topolnik", "sex": "F"},
]

PEOPLE_BY_NAME = {p["name"]: p for p in PEOPLE}

QUESTIONS_M = [
    "Bilo mi je teško smiriti se.",
    "Sušila su mi se usta.",
    "Uopće nisam mogao doživjeti neki pozitivan osjećaj.",
    "Doživio sam teškoće s disanjem (npr. ubrzano disanje, gubitak daha bez fizičkog napora).",
    "Bilo mi je teško započeti aktivnosti.",
    "Bio sam sklon pretjeranim reakcijama na događaje.",
    "Doživljavao sam drhtanje (npr. u rukama).",
    "Osjećao sam se jako nervozno.",
    "Zabrinjavale su me situacije u kojima bih mogao paničariti ili se osramotiti.",
    "Osjetio sam kao da se nemam čemu radovati.",
    "Osjetio sam da postajem uznemiren.",
    "Bilo mi je teško opustiti se.",
    "Bio sam potišten i tužan.",
    "Nisam podnosio da me išta ometa u onome što sam radio.",
    "Osjetio sam da sam blizu panici.",
    "Ništa me nije moglo oduševiti.",
    "Osjetio sam da ne vrijedim mnogo kao osoba.",
    "Događalo mi se da sam bio prilično osjetljiv.",
    "Bio sam svjestan rada svog srca bez fizičkog napora (npr. osjećaj preskakanja i ubrzanog rada srca).",
    "Bio sam uplašen bez opravdanog razloga.",
    "Osjetio sam kao da život nema smisla.",
]

QUESTIONS_F = [
    "Bilo mi je teško smiriti se.",
    "Sušila su mi se usta.",
    "Uopće nisam mogla doživjeti neki pozitivan osjećaj.",
    "Doživjela sam teškoće s disanjem (npr. ubrzano disanje, gubitak daha bez fizičkog napora).",
    "Bilo mi je teško započeti aktivnosti.",
    "Bila sam sklona pretjeranim reakcijama na događaje.",
    "Doživljavala sam drhtanje (npr. u rukama).",
    "Osjećala sam se jako nervozno.",
    "Zabrinjavale su me situacije u kojima bih mogla paničariti ili se osramotiti.",
    "Osjetila sam kao da se nemam čemu radovati.",
    "Osjetila sam da postajem uznemirena.",
    "Bilo mi je teško opustiti se.",
    "Bila sam potištena i tužna.",
    "Nisam podnosila da me išta ometa u onome što sam radila.",
    "Osjetila sam da sam blizu panici.",
    "Ništa me nije moglo oduševiti.",
    "Osjetila sam da ne vrijedim mnogo kao osoba.",
    "Događalo mi se da sam bila prilično osjetljiva.",
    "Bila sam svjesna rada svog srca bez fizičkog napora (npr. osjećaj preskakanja i ubrzanog rada srca).",
    "Bila sam uplašena bez opravdanog razloga.",
    "Osjetila sam kao da život nema smisla.",
]


def questions_for(sex):
    return QUESTIONS_F if sex == "F" else QUESTIONS_M


EXPERIMENT_START = "2026-04-22"
EXPERIMENT_DAYS = 14
