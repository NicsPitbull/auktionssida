from typing import List, Optional
from database import db
from models.bid import Bid

class BidRepository:
    """Repository for Bid model operations using SQLAlchemy ORM"""
    
    
    def get_all(self) -> List[Bid]:
        """Get all bids"""
        return Bid.query.order_by(Bid.created_at.desc()).all()
    
    def get_by_id(self, bid_id: int) -> Optional[Bid]:
        """Get bid by ID"""
        return Bid.query.filter_by(id=bid_id).first()
    
    def get_by_auction(self, auction_id: int) -> List[Bid]:
        """Get all bids for a specific auction"""
        return Bid.query.filter_by(auction_id=auction_id).order_by(Bid.amount.desc(), Bid.created_at.asc()).all()
    
    def get_top_bids(self, auction_id: int, limit: int = 2) -> List[Bid]:
        """Get top N bids for an auction (highest amounts)"""
        return Bid.query.filter_by(auction_id=auction_id).order_by(Bid.amount.desc(), Bid.created_at.asc()).limit(limit).all()
    
    def get_highest_bid(self, auction_id: int) -> Optional[Bid]:
        """Get the highest bid for an auction"""
        return Bid.query.filter_by(auction_id=auction_id).order_by(Bid.amount.desc(), Bid.created_at.asc()).first()
    
    def get_by_user(self, user_id: int) -> List[Bid]:
        """Get all bids by a specific user"""
        return Bid.query.filter_by(user_id=user_id).order_by(Bid.created_at.desc()).all()
    
    def create(self, bid: Bid) -> Bid:
        """Create new bid"""
        db.session.add(bid)
        db.session.commit()
        return bid
    
    def update(self, bid: Bid) -> Bid:
        """Update bid"""
        db.session.commit()
        return bid
    
    def delete(self, bid_id: int) -> bool:
        """Delete bid"""
        bid = self.get_by_id(bid_id)
        if bid:
            db.session.delete(bid)
            db.session.commit()
            return True
        return False
    
    def delete_by_auction(self, auction_id: int) -> int:
        """Delete all bids for an auction (admin function)"""
        count = Bid.query.filter_by(auction_id=auction_id).delete()
        db.session.commit()
        return count
