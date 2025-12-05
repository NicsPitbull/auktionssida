# dbrepositories/bostad_repository.py
"""
🏠 BOSTAD REPOSITORY - Ansvarar för ALL databasåtkomst för bostäder.

DETTA ÄR ETT DESIGNMÖNSTER (Repository Pattern / Data Access Layer):
Syftet är att isolera logiken för hur man pratar med databasen (t.ex. SQL-frågor)
från resten av applikationen (t.ex. webbroutning, användargränssnitt).

SINGLE RESPONSIBILITY (Enkelt ansvar): Denna fil har ENDAST ansvar för:
- Hämta data från databasen (READ/Hämta)
- Lägga till ny data (CREATE/Skapa)
- Uppdatera befintlig data (UPDATE/Uppdatera)
- Ta bort data (DELETE/Radera)

Viktigt: Denna fil känner INTE till routing, HTML, eller JSON!
Den är ENDAST fokuserad på att prata med databasen (CRUD-operationerna).
"""

# Importera Bostad-modellen (klassen som representerar tabellen 'bostad' i databasen)
from models.bostad import Bostad
# Importera databasobjektet (ofta en instans av SQLAlchemy) för att hantera sessioner
from database import db

from sqlalchemy import or_, cast, String

class BostadRepository:
    """
    Repository-klass för Bostad.
    Innehåller alla databasoperationer (CRUD = Create, Read, Update, Delete).
    Denna klass fungerar som en 'butler' som sköter kommunikationen med databasen
    åt resten av applikationen.
    """

    def hamta_alla(self):
        """
        Hämtar ALLA bostäder från databasen.
        Använder SQLAlchemy:s query-system för att göra en 'SELECT * FROM bostad'.

        Returns:
            list: En lista med alla Bostad-objekt. Varje objekt motsvarar en rad i tabellen.
        """
        # Bostad.query är basfrågan, .all() exekverar frågan och returnerar resultaten som en lista.
        return Bostad.query.all()

    def hamta_en(self, bostad_id):
        """
        Hämtar EN specifik bostad baserat på dess primärnyckel (ID).

        Args:
            bostad_id (int): ID för bostaden (Primärnyckel i databasen)

        Returns:
            Bostad: Bostad-objektet om det hittas, eller None om ID:t inte existerar.
        """
        # .get(id) är en snabb metod för att hämta en rad baserat på dess Primärnyckel.
        return Bostad.query.get(bostad_id)

    def hamta_eller_404(self, bostad_id):
        """
        Hämtar EN bostad eller utlöser ett 404-fel (Not Found).
        Denna metod är användbar i webbapplikationer där du vill att servern ska
        krascha snyggt med ett 404 om resursen inte finns.

        Args:
            bostad_id (int): ID för bostaden

        Returns:
            Bostad: Bostad-objektet (Garanterat att existera)

        Raises:
            404: Om bostaden inte hittas, utlöses ett Flask/webb-fel.
        """
        # .get_or_404(id) är en Flask-SQLAlchemy-funktion som automatiserar felhanteringen.
        return Bostad.query.get_or_404(bostad_id)

    def skapa_ny(self, data):
        """
        Skapar en NY bostad i databasen (INSERT-operation).

        Args:
            data (dict): En Python Dictionary som innehåller fälten (adress, stad, pris, etc.)
                         som ska sparas i den nya bostaden.

        Returns:
            Bostad: Den nya Bostad-instansen som skapades och sparades.
        """
        # Skapa en ny instans av Bostad-modellen baserat på datan i dictionaryn.
        ny_bostad = Bostad(
            adress=data['adress'],
            stad=data['stad'],
            pris=data['pris'],
            rum=data['rum'],
            yta=data['yta'],
            # Använder .get() med standardvärde för att hantera frivilliga fält (för att undvika KeyError)
            beskrivning=data.get('beskrivning', '')
        )

        # 1. Lägg till i session: Förbereder objektet för att sparas i databasen
        #    ('Staging' i en temporär buffert).
        db.session.add(ny_bostad)
        # 2. Spara/Committa: Utför den faktiska INSERT-frågan till databasen
        #    och gör ändringen permanent.
        db.session.commit()

        return ny_bostad

    def uppdatera(self, bostad_id, data):
        """
        Uppdaterar en BEFINTLIG bostad (UPDATE-operation).

        Args:
            bostad_id (int): ID för bostaden att uppdatera
            data (dict): Ny data att skriva över den gamla med.

        Returns:
            Bostad: Den uppdaterade bostaden, eller None om den inte fanns (och därmed inte uppdaterades).
        """
        # Först: Hämta det befintliga objektet från databasen.
        bostad = Bostad.query.get(bostad_id)

        if bostad:
            # Objektet hittades: Uppdatera fälten på Python-objektet.
            bostad.adress = data['adress']
            bostad.stad = data['stad']
            bostad.pris = data['pris']
            bostad.rum = data['rum']
            bostad.yta = data['yta']
            bostad.beskrivning = data.get('beskrivning', '')

            # Spara ändringarna: Berättar för databasen att ändringarna på objektet ska sparas (UPDATE-fråga).
            # I SQLAlchemy lägger man inte till igen (.add) vid uppdatering, utan committar direkt.
            db.session.commit()

        return bostad

    def radera(self, bostad_id):
        """
        Raderar en bostad från databasen (DELETE-operation).

        Args:
            bostad_id (int): ID för bostaden att radera

        Returns:
            bool: True om radering lyckades, False om bostaden inte fanns att radera.
        """
        # Först: Hämta objektet för att säkerställa att det finns.
        bostad = Bostad.query.get(bostad_id)

        if bostad:
            # Markera objektet för radering i databassessionen.
            db.session.delete(bostad)
            # Utför den faktiska DELETE-frågan till databasen.
            db.session.commit()
            return True

        return False
    
    def sok_fritext(self, query):
        """
        Gör en enkel fritextsökning i flera fält.

        Args:
            query (str): Texten som användaren skriver in i sökfältet.

        Returns:
            list: Lista med Bostad objekt som matchar sökningen.
        """
        if not query:
            return self.hamta_alla()

        pattern = f"%{query}%"

        return Bostad.query.filter(
            or_(
                Bostad.adress.ilike(pattern),
                Bostad.stad.ilike(pattern),
                Bostad.beskrivning.ilike(pattern),
                cast(Bostad.pris, String).ilike(pattern),
                cast(Bostad.rum, String).ilike(pattern),
                cast(Bostad.yta, String).ilike(pattern),
            )
        ).all()


    def sok_efter_stad(self, stad):
        """
        Söker bostäder i en specifik stad (En specialiserad READ-operation).

        Args:
            stad (str): Stadnamn att söka efter, t.ex. "Stockholm"

        Returns:
            list: Lista med Bostad-objekt där fältet 'stad' matchar in-parametern.
        """
        # .filter_by(stad=stad) lägger till en WHERE-klausul i SQL-frågan (t.ex. WHERE stad = 'Stockholm').
        # .all() exekverar frågan.
        return Bostad.query.filter_by(stad=stad).all()
    
    


# Skapa EN instans av repository som kan användas överallt
# Detta objekt är nu redo att importeras och användas i andra delar av koden,
# t.ex. i dina rutter (views).
bostad_repo = BostadRepository()