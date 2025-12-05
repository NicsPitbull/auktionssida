# myblueprints/bostader/__init__.py
"""
🏘️ BOSTÄDER BLUEPRINT - Initialiseringsfil (Instruktioner för att starta den publika modulen)

SYFTE: Att definiera den publika delen av applikationen, som visar listor och detaljer
över tillgängliga bostäder för besökare.

SINGLE RESPONSIBILITY: Denna fil har ENDAST ansvar för:
1. Definiera bostäder-blueprintet (Blueprint-objektet).
2. Importera nödvändiga resurser (bostad_repo).
3. Importera routes (URL-hanterarna) som tillhör bostäder-delen.

VIKTIGT OM IMPORTORDNING:
1. Blueprint-objektet (bostader_bp) måste skapas FÖRST.
2. Repository (bostad_repo) måste importeras.
3. Routes-filen (bostader_routes) importeras SIST, eftersom den använder både bostader_bp och bostad_repo.
"""
# Importera Blueprint-klassen från Flask
from flask import Blueprint

# ============================================================
# 1. SKAPA BLUEPRINTET
# ============================================================
bostader_bp = Blueprint(
    'bostader_bp',                       # Internt namn/identifierare. Används för url_for('bostader_bp.hamta_lista').
    __name__,                         # Python-modulens namn. Säger var Flask ska leta efter resurser.
    template_folder='templates',      # Säger till Flask var HTML-mallarna för detta blueprint ligger.
    # OBS: Detta blueprint registreras ofta utan url_prefix i huvudappen för att vara startsidan.
)


# ============================================================
# 2. IMPORTERA REPOSITORY (Databaslagret)
# ============================================================
# Importerar den enda instansen av bostad_repository.
# Detta är nödvändigt för att routarna ska kunna hämta bostadsdata.
from dbrepositories.bostad_repository import bostad_repo


# ============================================================
# 3. IMPORTERA ROUTES (URL:er och logik)
# ============================================================
# Denna import MÅSTE vara sist!
# Filen 'bostader_routes.py' importerar och använder de objekt som definieras ovan.
from . import bostader_routes