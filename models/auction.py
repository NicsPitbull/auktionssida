# models/auction.py
"""
🏛️ AUCTION MODEL - Auktionsmodell för auktionssajten
"""
from database import db
from datetime import datetime, timedelta
from sqlalchemy import func

class Auction(db.Model):
    """
    Auktionsmodell som representerar en auktion
    """
    __tablename__ = 'auctions'
    
    # Primärnyckel
    id = db.Column(db.Integer, primary_key=True)
    
    # Grundläggande auktionsinformation
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    
    # Prisrelaterade fält
    starting_bid = db.Column(db.Float, nullable=False)
    current_bid = db.Column(db.Float, nullable=True)  # Null om inga bud
    
    # Tidsrelaterade fält
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Bild
    image = db.Column(db.String(255), nullable=True, default='default_auction.jpg')  # Bildfilnamn
    
    # Relationer
    bids = db.relationship('Bid', backref='auction', lazy=True, cascade='all, delete-orphan', order_by='Bid.created_at.desc()')
    likes = db.relationship('Like', backref='auction', lazy=True, cascade='all, delete-orphan')
    
    @property
    def is_ongoing(self):
        """Kontrollerar om auktionen pågår"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time and self.is_active
    
    @property
    def is_upcoming(self):
        """Kontrollerar om auktionen är kommande"""
        return datetime.utcnow() < self.start_time and self.is_active
    
    @property
    def is_ended(self):
        """Kontrollerar om auktionen är avslutad"""
        return datetime.utcnow() > self.end_time
    
    @property
    def time_left(self):
        """Returnerar tid kvar på auktionen"""
        if self.is_ended:
            return timedelta(0)
        return self.end_time - datetime.utcnow()
    
    @property
    def highest_bids(self):
        """Returnerar de två högsta buden"""
        return self.bids[:2]  # Redan sorterade i desc ordning
    
    @property
    def bid_count(self):
        """Returnerar antal bud"""
        return len(self.bids)
    
    @property
    def like_count(self):
        """Returnerar antal likes"""
        return len([like for like in self.likes if like.is_like])
    
    @property
    def dislike_count(self):
        """Returnerar antal dislikes"""
        return len([like for like in self.likes if not like.is_like])
    
    @property
    def image_url(self):
        """Returnerar URL till auktionens bild"""
        from flask import url_for
        if self.image:
            return url_for('static', filename=f'images/{self.image}')
        return url_for('static', filename='images/default_auction.jpg')
    
    @classmethod
    def from_dict(cls, data):
        """Skapar en Auction-instans från en dictionary"""
        auction = cls()
        
        # Mappa fält från databas till modell
        field_mapping = {
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'category': 'category',
            'starting_bid': 'starting_bid',
            'current_bid': 'current_bid',
            'start_datetime': 'start_time',
            'end_datetime': 'end_time',
            'created_at': 'created_at',
            'status': 'is_active'  # Konvertera status till boolean
        }
        
        for db_field, model_field in field_mapping.items():
            if db_field in data:
                value = data[db_field]
                
                # Hantera datetime-fält
                if db_field in ['start_datetime', 'end_datetime', 'created_at'] and isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except:
                        value = datetime.utcnow()
                
                # Hantera status -> is_active konvertering
                if db_field == 'status':
                    value = value in ['active', 'upcoming']
                
                setattr(auction, model_field, value)
        
        return auction
    
    def __repr__(self):
        return f'<Auction {self.title}>'


# Startdata för auktioner
STARTDATA_AUCTIONS = [
    {
        'title': 'Vintage Klocka från 1950-talet',
        'description': 'En vacker vintage klocka i utmärkt skick. Perfekt för samlare.',
        'category': 'Antikviteter',
        'starting_bid': 500.0,
        'end_time': datetime.utcnow() + timedelta(days=7),
        'image': 'vintage_klocka.jpg'
    },
    {
        'title': 'Handmålad Tavla - Landskap',
        'description': 'Original oljemålning av svenskt landskap. Signerad av konstnären.',
        'category': 'Konst',
        'starting_bid': 1200.0,
        'end_time': datetime.utcnow() + timedelta(days=5),
        'image': 'tavla_landskap.jpg'
    },
    {
        'title': 'Samlarupplaga Bok - Första Tryckning',
        'description': 'Sällsynt första tryckning av klassisk svensk litteratur.',
        'category': 'Böcker',
        'starting_bid': 800.0,
        'end_time': datetime.utcnow() + timedelta(days=3),
        'image': 'bok_forsta_tryckning.jpg'
    },
    {
        'title': 'Keramikvas - Gustavsberg',
        'description': 'Vintage keramikvas från Gustavsberg. Perfekt skick.',
        'category': 'Keramik',
        'starting_bid': 300.0,
        'end_time': datetime.utcnow() + timedelta(days=10),
        'image': 'keramikvas_gustavsberg.jpg'
    }
]

def skapa_start_auctions():
    """Skapar startauktioner om inga finns"""
    antal_auctions = Auction.query.count()
    
    if antal_auctions == 0:
        print("🏛️ Lägger till startauktioner...")
        
        for data in STARTDATA_AUCTIONS:
            ny_auction = Auction(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                starting_bid=data['starting_bid'],
                end_time=data['end_time'],
                image=data.get('image', 'default_auction.jpg')
            )
            db.session.add(ny_auction)
        
        db.session.commit()
        print(f"✓ Lade till {len(STARTDATA_AUCTIONS)} auktioner")
    else:
        print(f"✓ Tabellen 'auctions' har redan {antal_auctions} auktioner.")
