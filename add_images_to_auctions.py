"""
Skript för att lägga till image-kolumn och uppdatera auktioner med bilder
"""
import sqlite3
import os

# Sökväg till databasen
DB_PATH = 'instance/blgeestates.db'

# Bildnamn för varje auktion (id: bildnamn)
AUKTION_BILDER = {
    1: 'vintage_klocka.jpg',
    2: 'tavla_landskap.jpg',
    3: 'bok_forsta_tryckning.jpg',
    4: 'keramikvas_gustavsberg.jpg',
    5: 'silverbestick.jpg',
    6: 'vinylspelare_technics.jpg',
    7: 'persisk_matta.jpg',
    8: 'leica_kamera.jpg',
    9: 'pippi_langstrump_bok.jpg',
    10: 'art_deco_lampa.jpg',
    11: 'rolex_datejust.jpg',
    12: 'hans_wegner_stol.jpg',
    13: 'gamla_mynt.jpg',
    14: 'gibson_les_paul.jpg',
}

def add_image_column():
    """Lägger till image-kolumn om den inte finns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Kontrollera om kolumnen redan finns
    cursor.execute("PRAGMA table_info(auctions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'image' not in columns:
        print("🖼️  Lägger till 'image' kolumn i auctions-tabellen...")
        cursor.execute("ALTER TABLE auctions ADD COLUMN image VARCHAR(255) DEFAULT 'default_auction.jpg'")
        conn.commit()
        print("✅ Kolumn tillagd!")
    else:
        print("ℹ️  'image' kolumn finns redan.")
    
    conn.close()

def update_auction_images():
    """Uppdaterar alla auktioner med bildnamn"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🖼️  Uppdaterar auktioner med bilder...")
    print("-" * 50)
    
    for auction_id, image_name in AUKTION_BILDER.items():
        cursor.execute("UPDATE auctions SET image = ? WHERE id = ?", (image_name, auction_id))
        print(f"  ✅ Auktion {auction_id}: {image_name}")
    
    conn.commit()
    conn.close()
    
    print("-" * 50)
    print(f"✅ Uppdaterade {len(AUKTION_BILDER)} auktioner med bilder!")

def show_auctions():
    """Visar alla auktioner med deras bilder"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, image FROM auctions ORDER BY id")
    auctions = cursor.fetchall()
    
    print("\n📊 AUKTIONER I DATABASEN:")
    print("=" * 70)
    print(f"{'ID':<4} {'Titel':<40} {'Bild':<25}")
    print("-" * 70)
    
    for auction in auctions:
        print(f"{auction[0]:<4} {auction[1][:38]:<40} {auction[2] or 'Ingen bild':<25}")
    
    print("=" * 70)
    conn.close()

def create_placeholder_images():
    """Skapar en lista över vilka bilder som behövs"""
    print("\n🖼️  BILDER SOM BEHÖVS I static/images/:")
    print("=" * 50)
    
    for auction_id, image_name in AUKTION_BILDER.items():
        print(f"  - {image_name}")
    
    print(f"\n  + default_auction.jpg (för auktioner utan bild)")
    print("=" * 50)
    print("\nLägg dessa bilder i: static/images/")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🖼️  AUKTIONSBILDER - DATABASUPPDATERING")
    print("=" * 50)
    
    # 1. Lägg till kolumn
    add_image_column()
    
    # 2. Uppdatera auktioner med bilder
    update_auction_images()
    
    # 3. Visa resultat
    show_auctions()
    
    # 4. Visa vilka bilder som behövs
    create_placeholder_images()
