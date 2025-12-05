# blueprints/bostader/bostader_routes.py
"""
🏘️ BOSTÄDER ROUTES - Hanterar publika URL:er för att visa bostäder (READ-operationer).

SINGLE RESPONSIBILITY: Fungerar som "Controller"-lagret för publika vyer.
- Hanterar URL:er för listvisning och detaljvisning.
- Anropar bostad_repo för att hämta data från databasen.
- Renderar HTML-mallar för slutanvändaren.
"""
from flask import render_template, request
# Importera Blueprint-objektet och bostad_repo som definierades i __init__.py
from . import bostader_bp  # Blueprint-instansen används som decorator
from . import bostad_repo  # Repository-instansen används för dataåtkomst


# Notera: Den simulerade databasdatan (BOSTADER-listan) har behållits som referens,
# men den faktiska koden använder bostad_repo.

# Route 1: Visar listan över alla bostäder
# @bostader_bp.route('/') kan bli antingen /bostader/ eller bara / (startsidan),
# beroende på hur Blueprintet registreras i app.py.
@bostader_bp.route('/')
def lista_bostader():
    """
    Visar en lista över alla tillgängliga bostäder.

    Anropar: bostad_repo.hamta_alla()
    """
    # 1. Anropa Repository för att hämta alla Bostad-objekt
    alla_bostader = bostad_repo.hamta_alla()

    # 2. Returnera HTML (View Layer) med data
    return render_template(
        'bostader_lista.html',
        bostader=alla_bostader,  # Skickar ORM-objekten till mallen
        titel='Våra bostäder'
    )


# Route 2: Visar detaljer för en specifik bostad
# <int:bostad_id> skapar en dynamisk URL-parameter och säkerställer att den är ett heltal
@bostader_bp.route('/bostader/<int:bostad_id>')
def bostad_detalj(bostad_id):
    """
    Visar en enskild bostadsdetaljsida baserat på ID.

    Args:
        bostad_id (int): Primärnyckeln för den bostad som ska visas.
    """
    # 1. Anropa Repository för att hämta ETT Bostad-objekt
    bostad = bostad_repo.hamta_en(bostad_id)

    # 2. Kontrollera om bostaden hittades
    if bostad is None:
        # Returnera en 404 Not Found-sida
        # I en riktig app skulle man använda flask.abort(404)
        return "Bostaden hittades inte (404)", 404

    # 3. Returnera HTML (View Layer) med det enskilda objektet
    return render_template(
        'bostad_detalj.html',
        bostad=bostad,
        titel=bostad.adress  # Använd objektets adress som sidtitel
    )
@bostader_bp.route('/sok')
def sok_bostader():
    """
    Sök efter bostäder med fritext.
    Tar emot query parametern q via GET.
    """
    query = request.args.get('q', '').strip()

    if not query:
        resultat = bostad_repo.hamta_alla()
        titel = "Våra bostäder"
    else:
        resultat = bostad_repo.sok_fritext(query)
        titel = f"Sökresultat: {query}"

    return render_template(
        'bostader_lista.html',
        bostader=resultat,
        titel=titel
    )
