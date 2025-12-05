from typing import List, Optional, Tuple
from database import db
from models.like import Like

class LikeRepository:
    """Repository for Like model operations using SQLAlchemy ORM"""
    
    
    def get_all(self) -> List[Like]:
        """Get all likes/dislikes"""
        return Like.query.order_by(Like.created_at.desc()).all()
    
    def get_by_id(self, like_id: int) -> Optional[Like]:
        """Get like by ID"""
        return Like.query.filter_by(id=like_id).first()
    
    def get_by_auction(self, auction_id: int) -> List[Like]:
        """Get all likes/dislikes for a specific auction"""
        return Like.query.filter_by(auction_id=auction_id).order_by(Like.created_at.desc()).all()
    
    def get_by_user(self, user_id: int) -> List[Like]:
        """Get all likes/dislikes by a specific user"""
        return Like.query.filter_by(user_id=user_id).order_by(Like.created_at.desc()).all()
    
    def get_user_like_on_auction(self, user_id: int, auction_id: int) -> Optional[Like]:
        """Get user's like/dislike on a specific auction"""
        return Like.query.filter_by(user_id=user_id, auction_id=auction_id).first()
    
    def get_auction_like_counts(self, auction_id: int) -> Tuple[int, int]:
        """Get like and dislike counts for an auction"""
        like_count = Like.query.filter_by(auction_id=auction_id, is_like=True).count()
        dislike_count = Like.query.filter_by(auction_id=auction_id, is_like=False).count()
        return like_count, dislike_count
    
    def create(self, like: Like) -> Like:
        """Create new like/dislike"""
        db.session.add(like)
        db.session.commit()
        return like
    
    def update(self, like: Like) -> Like:
        """Update like/dislike"""
        db.session.commit()
        return like
    
    def delete(self, like_id: int) -> bool:
        """Delete like/dislike"""
        like = self.get_by_id(like_id)
        if like:
            db.session.delete(like)
            db.session.commit()
            return True
        return False
