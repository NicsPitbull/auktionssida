from typing import List, Optional
from datetime import datetime
from database import db
from models.auction import Auction

class AuctionRepository:
    """Repository for Auction model operations using SQLAlchemy ORM"""
    
    def get_all(self) -> List[Auction]:
        """Get all auctions"""
        return Auction.query.order_by(Auction.created_at.desc()).all()
    
    def get_by_id(self, auction_id: int) -> Optional[Auction]:
        """Get auction by ID"""
        return Auction.query.filter_by(id=auction_id).first()
    
    def get_active_auctions(self) -> List[Auction]:
        """Get all active auctions (not ended)"""
        from datetime import datetime
        return Auction.query.filter(
            Auction.end_time > datetime.utcnow(),
            Auction.is_active == True
        ).order_by(Auction.end_time.asc()).all()
    
    def get_upcoming_auctions(self) -> List[Auction]:
        """Get upcoming auctions (start time in future)"""
        from datetime import datetime
        return Auction.query.filter(
            Auction.start_time > datetime.utcnow(),
            Auction.is_active == True
        ).order_by(Auction.start_time.asc()).all()
    
    def get_ended_auctions(self) -> List[Auction]:
        """Get ended auctions"""
        from datetime import datetime
        return Auction.query.filter(
            (Auction.end_time <= datetime.utcnow()) | 
            (Auction.is_active == False)
        ).order_by(Auction.end_time.desc()).all()
    
    def search_auctions(self, keyword: str) -> List[Auction]:
        """Search auctions by keyword in title or description"""
        query = """
            SELECT * FROM auctions 
            WHERE (title LIKE ? OR description LIKE ?)
            AND status IN ('active', 'upcoming')
            ORDER BY created_at DESC
        """
        search_term = f"%{keyword}%"
        rows = self.execute_query(query, (search_term, search_term))
        return [Auction.from_dict(dict(row)) for row in rows]
    
    def filter_auctions(self, category: str = None, min_price: float = None, 
                       max_price: float = None, end_before: datetime = None) -> List[Auction]:
        """Filter auctions by various criteria"""
        conditions = ["status IN ('active', 'upcoming')"]
        params = []
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if min_price is not None:
            conditions.append("starting_bid >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("starting_bid <= ?")
            params.append(max_price)
        
        if end_before:
            conditions.append("end_datetime <= ?")
            params.append(end_before.isoformat())
        
        query = f"""
            SELECT * FROM auctions 
            WHERE {' AND '.join(conditions)}
            ORDER BY end_datetime ASC
        """
        
        rows = self.execute_query(query, tuple(params))
        return [Auction.from_dict(dict(row)) for row in rows]
    
    def create(self, title: str, description: str, starting_bid: float, 
               start_datetime: datetime, end_datetime: datetime, 
               category: str = None, image_url: str = None, 
               created_by: int = None) -> int:
        """Create new auction"""
        query = """
            INSERT INTO auctions (title, description, starting_bid, current_bid, 
                                start_datetime, end_datetime, category, image_url, 
                                created_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'upcoming')
        """
        return self.execute_non_query(query, (
            title, description, starting_bid, starting_bid,
            start_datetime.isoformat(), end_datetime.isoformat(),
            category, image_url, created_by
        ))
    
    def update(self, auction_id: int, **kwargs) -> bool:
        """Update auction"""
        allowed_fields = ['title', 'description', 'starting_bid', 'current_bid',
                         'start_datetime', 'end_datetime', 'category', 'image_url', 'status']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field in ['start_datetime', 'end_datetime'] and isinstance(value, datetime):
                    value = value.isoformat()
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(auction_id)
        query = f"UPDATE auctions SET {', '.join(updates)} WHERE id = ?"
        return self.execute_non_query(query, tuple(params)) > 0
    
    def delete(self, auction_id: int) -> bool:
        """Delete auction"""
        query = "DELETE FROM auctions WHERE id = ?"
        return self.execute_non_query(query, (auction_id,)) > 0
    
    def update_current_bid(self, auction_id: int, new_bid: float) -> bool:
        """Update current bid for auction"""
        query = "UPDATE auctions SET current_bid = ? WHERE id = ?"
        return self.execute_non_query(query, (new_bid, auction_id)) > 0
    
    def get_by_category(self, category: str) -> List[Auction]:
        """Get auctions by category"""
        query = """
            SELECT * FROM auctions 
            WHERE category = ? AND status IN ('active', 'upcoming')
            ORDER BY end_datetime ASC
        """
        rows = self.execute_query(query, (category,))
        return [Auction.from_dict(dict(row)) for row in rows]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        query = "SELECT DISTINCT category FROM auctions WHERE category IS NOT NULL ORDER BY category"
        rows = self.execute_query(query)
        return [row['category'] for row in rows]
