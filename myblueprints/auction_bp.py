from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.auction import Auction
from models.bid import Bid
from models.like import Like
from models.user import User
from database import db
from datetime import datetime

# Create auction blueprint
auction_bp = Blueprint('auction', __name__, url_prefix='/auctions')

@auction_bp.route('/')
def browse_auctions():
    """Browse all auctions with filtering and search"""
    # Get query parameters
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', 'all')  # all, active, upcoming, ended
    sort_by = request.args.get('sort', 'end_time')  # end_time, created_at, current_bid
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    # Start with base query
    query = Auction.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                Auction.title.ilike(f'%{search_query}%'),
                Auction.description.ilike(f'%{search_query}%')
            )
        )
    
    # Apply category filter
    if category:
        query = query.filter(Auction.category == category)
    
    # Apply status filter
    now = datetime.utcnow()
    if status == 'active':
        query = query.filter(
            Auction.start_time <= now,
            Auction.end_time > now,
            Auction.is_active == True
        )
    elif status == 'upcoming':
        query = query.filter(
            Auction.start_time > now,
            Auction.is_active == True
        )
    elif status == 'ended':
        query = query.filter(
            db.or_(
                Auction.end_time <= now,
                Auction.is_active == False
            )
        )
    
    # Apply price range filter
    if min_price:
        try:
            min_price_val = float(min_price)
            query = query.filter(Auction.current_bid >= min_price_val)
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price_val = float(max_price)
            query = query.filter(Auction.current_bid <= max_price_val)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'end_time':
        query = query.order_by(Auction.end_time.asc())
    elif sort_by == 'created_at':
        query = query.order_by(Auction.created_at.desc())
    elif sort_by == 'current_bid':
        query = query.order_by(Auction.current_bid.desc().nullslast())
    
    auctions = query.all()
    
    # Get all categories for filter dropdown
    categories = db.session.query(Auction.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Add like/dislike counts and user reactions
    auction_data = []
    for auction in auctions:
        auction_info = {
            'auction': auction,
            'like_count': auction.like_count,
            'dislike_count': auction.dislike_count,
            'user_reaction': None
        }
        
        # Get user's reaction if logged in
        if current_user.is_authenticated:
            user_like = Like.query.filter_by(
                user_id=current_user.id,
                auction_id=auction.id
            ).first()
            if user_like:
                auction_info['user_reaction'] = 'like' if user_like.is_like else 'dislike'
        
        auction_data.append(auction_info)
    
    return render_template('auctions/browse.html', 
                         auction_data=auction_data,
                         categories=categories,
                         current_search=search_query,
                         current_category=category,
                         current_status=status,
                         current_sort=sort_by)

@auction_bp.route('/<int:auction_id>')
def auction_detail(auction_id):
    """View detailed information about a specific auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    # Get top 2 bids with bidder information
    top_bids = db.session.query(Bid, User).\
        join(User, Bid.user_id == User.id).\
        filter(Bid.auction_id == auction_id).\
        order_by(Bid.amount.desc(), Bid.created_at.asc()).\
        limit(2).all()
    
    # Get all bids for history (limited to recent ones)
    bid_history = db.session.query(Bid, User).\
        join(User, Bid.user_id == User.id).\
        filter(Bid.auction_id == auction_id).\
        order_by(Bid.created_at.desc()).\
        limit(10).all()
    
    # Get like/dislike counts
    like_count = auction.like_count
    dislike_count = auction.dislike_count
    
    # Get user's reaction if logged in
    user_reaction = None
    if current_user.is_authenticated:
        user_like = Like.query.filter_by(
            user_id=current_user.id,
            auction_id=auction_id
        ).first()
        if user_like:
            user_reaction = 'like' if user_like.is_like else 'dislike'
    
    return render_template('auctions/detail.html',
                         auction=auction,
                         top_bids=top_bids,
                         bid_history=bid_history,
                         like_count=like_count,
                         dislike_count=dislike_count,
                         user_reaction=user_reaction)

@auction_bp.route('/<int:auction_id>/like', methods=['POST'])
@login_required
def toggle_like(auction_id):
    """Toggle like for an auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    like_obj, action = Like.toggle_like(current_user.id, auction_id, True)
    
    # Get updated counts
    like_count = auction.like_count
    dislike_count = auction.dislike_count
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'action': action,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'user_reaction': 'like' if action != 'deleted' else None
        })
    
    flash(f"{'Liked' if action != 'deleted' else 'Removed like from'} {auction.title}", 'success')
    return redirect(url_for('auction.auction_detail', auction_id=auction_id))

@auction_bp.route('/<int:auction_id>/dislike', methods=['POST'])
@login_required
def toggle_dislike(auction_id):
    """Toggle dislike for an auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    like_obj, action = Like.toggle_like(current_user.id, auction_id, False)
    
    # Get updated counts
    like_count = auction.like_count
    dislike_count = auction.dislike_count
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'action': action,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'user_reaction': 'dislike' if action != 'deleted' else None
        })
    
    flash(f"{'Disliked' if action != 'deleted' else 'Removed dislike from'} {auction.title}", 'success')
    return redirect(url_for('auction.auction_detail', auction_id=auction_id))

@auction_bp.route('/categories')
def get_categories():
    """API endpoint to get all auction categories"""
    categories = db.session.query(Auction.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    return jsonify({'categories': sorted(categories)})

@auction_bp.route('/search')
def search_auctions():
    """API endpoint for AJAX search"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'auctions': []})
    
    auctions = Auction.query.filter(
        db.or_(
            Auction.title.ilike(f'%{query}%'),
            Auction.description.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for auction in auctions:
        results.append({
            'id': auction.id,
            'title': auction.title,
            'current_bid': auction.current_bid or auction.starting_bid,
            'end_time': auction.end_time.isoformat(),
            'status': 'active' if auction.is_ongoing else 'ended' if auction.is_ended else 'upcoming'
        })
    
    return jsonify({'auctions': results})
