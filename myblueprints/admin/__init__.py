# myblueprints/admin/__init__.py
"""
⚙️ ADMIN BLUEPRINT - Admin management functionality

SYFTE: Hanterar administratörsfunktioner:
- Skapa, redigera, radera auktioner
- Hantera bud (radera vid behov)
- Användarhantering
- Administratörspanel
"""
from flask import Blueprint

# Skapa admin blueprint
admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
)

# Importera routes
from . import admin_routes
