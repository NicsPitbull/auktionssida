"""
Skript för att lägga till fler auktioner i databasen
"""
from flask_app import skapa_app
from database import db
from models.auction import Auction
from datetime import datetime, timedelta

# Nya auktioner att lägga till
NYA_AUKTIONER = [
    {
        'title': 'Antik Silverbestick - 12 personer',
        'description': 'Komplett silverbestick för 12 personer från tidigt 1900-tal. Stämplade med svenska silversmärken. Inkluderar knivar, gafflar, skedar och dessertbestick.',
        'category': 'Antikviteter',
        'starting_bid': 3500.0,
        'end_time': datetime.utcnow() + timedelta(days=14)
    },
    {
        'title': 'Retro Vinylspelare - Technics SL-1200',
        'description': 'Klassisk DJ-skivspelare i utmärkt skick. Perfekt för vinylentusiaster. Inkluderar original pickup.',
        'category': 'Elektronik',
        'starting_bid': 4500.0,
        'end_time': datetime.utcnow() + timedelta(days=10)
    },
    {
        'title': 'Handknuten Persisk Matta',
        'description': 'Autentisk persisk matta, handknuten i Isfahan. Mått: 200x300 cm. Vackra traditionella mönster i rött och blått.',
        'category': 'Textilier',
        'starting_bid': 8000.0,
        'end_time': datetime.utcnow() + timedelta(days=21)
    },
    {
        'title': 'Vintage Leica Kamera M3',
        'description': 'Ikonisk Leica M3 från 1954. Fullt fungerande med original läderetui. Samlarodjekt i toppskick.',
        'category': 'Foto',
        'starting_bid': 12000.0,
        'end_time': datetime.utcnow() + timedelta(days=7)
    },
    {
        'title': 'Signerad Första Upplaga - Astrid Lindgren',
        'description': 'Första upplagan av "Pippi Långstrump" från 1945, signerad av Astrid Lindgren. Extremt sällsynt samlarobjekt.',
        'category': 'Böcker',
        'starting_bid': 25000.0,
        'end_time': datetime.utcnow() + timedelta(days=30)
    },
    {
        'title': 'Art Deco Lampa - 1920-tal',
        'description': 'Elegant Art Deco bordslampa i brons och opalglas. Original från 1920-talet. Höjd: 45 cm.',
        'category': 'Belysning',
        'starting_bid': 2200.0,
        'end_time': datetime.utcnow() + timedelta(days=12)
    },
    {
        'title': 'Vintage Rolex Datejust',
        'description': 'Rolex Datejust från 1978 i 18k guld och stål. Nyservad med certifikat. Klassisk elegans.',
        'category': 'Klockor',
        'starting_bid': 45000.0,
        'end_time': datetime.utcnow() + timedelta(days=14)
    },
    {
        'title': 'Skandinavisk Design Stol - Hans Wegner',
        'description': 'Original "The Chair" (PP501) av Hans Wegner. Tillverkad av PP Møbler. Ek och läder.',
        'category': 'Möbler',
        'starting_bid': 18000.0,
        'end_time': datetime.utcnow() + timedelta(days=18)
    },
    {
        'title': 'Samling Gamla Mynt - Sverige 1800-tal',
        'description': 'Samling av 25 svenska mynt från 1800-talet. Inkluderar sällsynta riksdaler och öre. Med certifikat.',
        'category': 'Numismatik',
        'starting_bid': 6500.0,
        'end_time': datetime.utcnow() + timedelta(days=9)
    },
    {
        'title': 'Vintage Gibson Les Paul Standard',
        'description': 'Gibson Les Paul Standard från 1959 reissue. Sunburst finish. Inkluderar original hardcase.',
        'category': 'Musikinstrument',
        'starting_bid': 35000.0,
        'end_time': datetime.utcnow() + timedelta(days=21)
    }
]

def lagg_till_auktioner():
    """Lägger till nya auktioner i databasen"""
    app = skapa_app()
    
    with app.app_context():
        print("\n" + "=" * 50)
        print("🏛️ LÄGGER TILL NYA AUKTIONER")
        print("=" * 50)
        
        # Kontrollera nuvarande antal
        nuvarande_antal = Auction.query.count()
        print(f"\nNuvarande antal auktioner: {nuvarande_antal}")
        
        # Lägg till nya auktioner
        tillagda = 0
        for data in NYA_AUKTIONER:
            # Kontrollera om auktionen redan finns (baserat på titel)
            existing = Auction.query.filter_by(title=data['title']).first()
            if existing:
                print(f"  ⚠️  '{data['title']}' finns redan - hoppar över")
                continue
            
            ny_auction = Auction(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                starting_bid=data['starting_bid'],
                end_time=data['end_time']
            )
            db.session.add(ny_auction)
            tillagda += 1
            print(f"  ✅ Lade till: '{data['title']}'")
        
        db.session.commit()
        
        # Visa resultat
        nytt_antal = Auction.query.count()
        print(f"\n" + "-" * 50)
        print(f"✅ Klart! Lade till {tillagda} nya auktioner.")
        print(f"   Totalt antal auktioner nu: {nytt_antal}")
        print("=" * 50 + "\n")

if __name__ == '__main__':
    lagg_till_auktioner()
