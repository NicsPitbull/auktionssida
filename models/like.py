# models/like.py
"""
👍 LIKE MODEL - Like/Dislike modell för auktioner
"""
from database import db
from datetime import datetime

class Like(db.Model):
    """
    Like/Dislike modell för auktioner
    """
    __tablename__ = 'likes'
    
    # Primärnyckel
    id = db.Column(db.Integer, primary_key=True)
    
    # Like eller dislike
    is_like = db.Column(db.Boolean, nullable=False)  # True = like, False = dislike
    
    # Tidsstämpel
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Främmande nycklar
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Unik constraint - en användare kan bara ha en like/dislike per auktion
    __table_args__ = (
        db.UniqueConstraint('auction_id', 'user_id', name='unique_user_auction_like'),
        db.Index('idx_auction_likes', 'auction_id', 'is_like'),
    )
    
    def __repr__(self):
        action = 'like' if self.is_like else 'dislike'
        return f'<{action.title()} på auction {self.auction_id} av user {self.user_id}>'
    
    @classmethod
    def toggle_like(cls, user_id, auction_id, is_like):
        """
        Växlar like/dislike för en användare på en auktion
        Returnerar (like_object, action) där action är 'created', 'updated', eller 'deleted'
        """
        existing_like = cls.query.filter_by(user_id=user_id, auction_id=auction_id).first()
        
        if existing_like:
            if existing_like.is_like == is_like:
                # Samma som innan - ta bort
                db.session.delete(existing_like)
                db.session.commit()
                return None, 'deleted'
            else:
                # Ändra från like till dislike eller tvärtom
                existing_like.is_like = is_like
                existing_like.created_at = datetime.utcnow()
                db.session.commit()
                return existing_like, 'updated'
        else:
            # Skapa ny like/dislike
            new_like = cls(user_id=user_id, auction_id=auction_id, is_like=is_like)
            db.session.add(new_like)
            db.session.commit()
            return new_like, 'created'
    
    @classmethod
    def get_user_reaction(cls, user_id, auction_id):
        """
        Hämtar användarens reaktion på en auktion
        Returnerar 'like', 'dislike', eller None
        """
        like = cls.query.filter_by(user_id=user_id, auction_id=auction_id).first()
        if like:
            return 'like' if like.is_like else 'dislike'
        return None


def skapa_start_likes():
    """Skapar start likes/dislikes om inga finns"""
    from models.auction import Auction
    from models.user import User
    
    antal_likes = Like.query.count()
    
    if antal_likes == 0:
        print("👍 Lägger till start likes/dislikes...")
        
        # Hämta första auktionen och användaren
        auction = Auction.query.first()
        user = User.query.filter_by(is_admin=False).first()
        
        if auction and user:
            # Skapa några test likes/dislikes
            test_likes = [
                {'user_id': user.id, 'auction_id': auction.id, 'is_like': True},
            ]
            
            for like_data in test_likes:
                ny_like = Like(
                    user_id=like_data['user_id'],
                    auction_id=like_data['auction_id'],
                    is_like=like_data['is_like']
                )
                db.session.add(ny_like)
            
            db.session.commit()
            print(f"✓ Lade till {len(test_likes)} test likes/dislikes")
        else:
            print("⚠️ Kunde inte skapa start likes - saknar auktioner eller användare")
    else:
        print(f"✓ Tabellen 'likes' har redan {antal_likes} likes/dislikes.")
