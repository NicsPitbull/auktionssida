"""
Models package for auction site.
Contains all database models and their relationships.
"""

from .user import User, skapa_start_users
from .auction import Auction, skapa_start_auctions
from .bid import Bid, skapa_start_bids
from .like import Like, skapa_start_likes
# from .bostad import Bostad, skapa_start_bostader  # Removed - not needed for auction site

__all__ = [
    'User',
    'Auction',
    'Bid',
    'Like',
    # 'Bostad',  # Removed
    'skapa_start_users',
    'skapa_start_auctions',
    'skapa_start_bids',
    'skapa_start_likes',
    # 'skapa_start_bostader'  # Removed
]
