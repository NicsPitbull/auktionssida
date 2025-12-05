# dbrepositories/models/bostad.py
"""
🏠 BOSTAD-MODELL - Beskriver hur en bostad ser ut i databasen (Schema Definition).

SINGLE RESPONSIBILITY: Denna fil har ENDAST ansvar för:
1. Definiera strukturen på 'bostader'-tabellen (kolumner, datatyper).
2. Tillhandahålla startdata (seeding data) för att fylla databasen vid första körningen.

OBS! Denna fil har INGEN affärslogik, rutter eller CRUD-operationer!
Den sköts av BostadRepository.
"""
# Importera 'db' som är instansen av SQLAlchemy (eller Flask-SQLAlchemy)
from database import db


# Importera nödvändiga funktioner (i detta fall, inga extra behövs)


class Bostad(db.Model):
    """
    Bostad-modellen representerar EN bostad i databasen.
    Ärver från db.Model för att få alla ORM-funktionaliteter.

    Varje rad i tabellen 'bostader' blir ett Bostad-objekt i Python.
    """
    # Berättar för SQLAlchemy vilket tabellnamn vi vill ha i databasen
    __tablename__ = 'bostader'

    # -----------------------------------------------------------------
    # KOLUMNDELAR (Tabellschema)
    # -----------------------------------------------------------------
    # id: Primärnyckel (unikt ID)
    id = db.Column(db.Integer, primary_key=True)

    # adress: Sträng (max 200 tecken), MÅSTE fyllas i (nullable=False)
    adress = db.Column(db.String(200), nullable=False)

    # stad: Sträng (max 100 tecken), MÅSTE fyllas i
    stad = db.Column(db.String(100), nullable=False)

    # pris: Sparas som sträng eftersom valutor ofta innehåller mellanslag/tecken
    pris = db.Column(db.String(50), nullable=False)

    # rum: Heltal
    rum = db.Column(db.Integer, nullable=False)

    # yta: Heltal (kvadratmeter)
    yta = db.Column(db.Integer, nullable=False)

    # beskrivning: Lång textsträng (Text), valfri (nullable är True som standard)
    beskrivning = db.Column(db.Text)

    # -----------------------------------------------------------------
    # RELATIONER (Läggs till senare om Bostad har FK till t.ex. Mäklare)
    # -----------------------------------------------------------------

    def __repr__(self):
        """
        Denna metod definierar hur objektet visas när vi printar det (används för debugging).
        Ger en läsbar representation av objektet.
        """
        return f'<Bostad {self.adress}, {self.stad}, {self.pris}>'


# ============================================================
# STARTDATA (Seeding Data)
# ============================================================

STARTDATA_BOSTADER = [
    {
        'adress': 'Storgatan 15A',
        'stad': 'Borlänge',
        'pris': '1 950 000 kr',
        'rum': 3,
        'yta': 75,
        'beskrivning': 'Trevlig lägenhet med balkong och centralt läge. Perfekt för pendlaren.'
    },
    {
        'adress': 'Ekbacken 4',
        'stad': 'Falun',
        'pris': '4 200 000 kr',
        'rum': 6,
        'yta': 150,
        'beskrivning': 'Fristående villa med stor trädgård och sjöutsikt. Ett måste för barnfamiljen.'
    },
    {
        'adress': 'Sjövägen 88',
        'stad': 'Leksand',
        'pris': '3 100 000 kr',
        'rum': 4,
        'yta': 98,
        'beskrivning': 'Radhus med utsikt över Siljan och nära till service. Lugnt och skönt område.'
    },
    {
        'adress': 'Åsgatan 2',
        'stad': 'Säter',
        'pris': '850 000 kr',
        'rum': 2,
        'yta': 55,
        'beskrivning': 'Mindre lägenhet, perfekt som första bostad. Låga driftkostnader.'
    }
]


def skapa_start_bostader():
    """
    Funktion som körs för att säkerställa att tabellen 'bostader' har grunddata.
    Lägger till startdata i databasen ENDAST OM tabellen är tom.
    """
    # Använder Repository-logik (men koden finns i modellen)
    # 1. Fråga databasen hur många rader som finns
    antal_bostader = Bostad.query.count()

    if antal_bostader == 0:
        print("📦 Lägger till startdata för bostäder...")

        # 2. Skapa ett Bostad-objekt för varje dictionary i listan
        for data in STARTDATA_BOSTADER:
            ny_bostad = Bostad(
                adress=data['adress'],
                stad=data['stad'],
                pris=data['pris'],
                rum=data['rum'],
                yta=data['yta'],
                beskrivning=data['beskrivning']
            )
            db.session.add(ny_bostad)  # Lägger till objektet i transaktionen

        # 3. Spara alla nya objekt permanent till databasen
        db.session.commit()
        print(f"✓ Lade till {len(STARTDATA_BOSTADER)} bostäder")
    else:
        print(f"✓ Tabellen 'bostader' har redan {antal_bostader} rader. Ingen startdata lades till.")