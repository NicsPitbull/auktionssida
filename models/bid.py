# models/bid.py
"""
💰 BID MODEL - Budmodell för auktionssajten
"""
from database import db
from datetime import datetime

class Bid(db.Model):
    """
    Budmodell som representerar ett bud på en auktion
    """
    __tablename__ = 'bids'
    
    # Primärnyckel
    id = db.Column(db.Integer, primary_key=True)
    
    # Budbelopp
    amount = db.Column(db.Float, nullable=False)
    
    # Tidsstämpel
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Främmande nycklar
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Indexering för prestanda
    __table_args__ = (
        db.Index('idx_auction_amount', 'auction_id', 'amount'),
        db.Index('idx_auction_created', 'auction_id', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Bid {self.amount} kr på auction {self.auction_id}>'
    
    @property
    def formatted_amount(self):
        """Returnerar formaterat belopp"""
        return f"{self.amount:,.0f} kr"
    
    @property
    def bidder_email(self):
        """Returnerar budgivarens email (för admin)"""
        return self.bidder.email if self.bidder else 'Okänd'
    
    @property
    def bidder_name(self):
        """Returnerar budgivarens namn"""
        return self.bidder.full_name if self.bidder else 'Okänd'


# Startdata för bud (skapas efter auktioner och användare)
def skapa_start_bids():
    """Skapar startbud om inga finns"""
    from models.auction import Auction
    from models.user import User
    
    antal_bids = Bid.query.count()
    
    if antal_bids == 0:
        print("💰 Lägger till startbud...")
        
        # Hämta första auktionen och användaren
        auction = Auction.query.first()
        user = User.query.filter_by(is_admin=False).first()
        
        if auction and user:
            # Skapa några testbud
            test_bids = [
                {'amount': auction.starting_bid + 100, 'user_id': user.id, 'auction_id': auction.id},
                {'amount': auction.starting_bid + 250, 'user_id': user.id, 'auction_id': auction.id}
            ]
            
            for bid_data in test_bids:
                nytt_bid = Bid(
                    amount=bid_data['amount'],
                    user_id=bid_data['user_id'],
                    auction_id=bid_data['auction_id']
                )
                db.session.add(nytt_bid)
            
            # Uppdatera current_bid på auktionen
            auction.current_bid = test_bids[-1]['amount']
            
            db.session.commit()
            print(f"✓ Lade till {len(test_bids)} testbud")
        else:
            print("⚠️ Kunde inte skapa startbud - saknar auktioner eller användare")
    else:
        print(f"✓ Tabellen 'bids' har redan {antal_bids} bud.")
