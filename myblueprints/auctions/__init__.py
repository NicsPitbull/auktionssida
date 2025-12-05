# myblueprints/auctions/__init__.py
"""
🏛️ AUCTIONS BLUEPRINT - Auction browsing and bidding functionality

SYFTE: Hanterar alla auktionsrelaterade funktioner:
- Visa auktioner (pågående och kommande)
- Visa auktionsdetaljer med budhistorik
- Hantera budgivning
- Sök och filtrera auktioner
- Like/dislike funktionalitet
"""
from flask import Blueprint

# Skapa auctions blueprint
auctions_bp = Blueprint(
    'auctions_bp',
    __name__,
    template_folder='templates'
)

# Import routes
from . import auction_routes
