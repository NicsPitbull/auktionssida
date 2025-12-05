from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.auction import Auction
from models.bid import Bid
from models.user import User
from database import db
from datetime import datetime

# Create bidding blueprint
bidding_bp = Blueprint('bidding', __name__, url_prefix='/bidding')

@bidding_bp.route('/place/<int:auction_id>', methods=['POST'])
@login_required
def place_bid(auction_id):
    """Place a bid on an auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    # Check if auction is active
    if not auction.is_ongoing:
        flash('This auction is not currently active for bidding.', 'error')
        return redirect(url_for('auction.auction_detail', auction_id=auction_id))
    
    try:
        bid_amount = float(request.form.get('amount', 0))
    except (ValueError, TypeError):
        flash('Invalid bid amount.', 'error')
        return redirect(url_for('auction.auction_detail', auction_id=auction_id))
    
    # Validate bid amount
    current_highest = auction.current_bid or auction.starting_bid
    if bid_amount <= current_highest:
        flash(f'Bid must be higher than current bid of {current_highest:.0f} SEK.', 'error')
        return redirect(url_for('auction.auction_detail', auction_id=auction_id))
    
    # Check if user is already the highest bidder
    highest_bid = Bid.query.filter_by(auction_id=auction_id).\
        order_by(Bid.amount.desc(), Bid.created_at.asc()).first()
    
    if highest_bid and highest_bid.user_id == current_user.id:
        flash('You are already the highest bidder on this auction.', 'warning')
        return redirect(url_for('auction.auction_detail', auction_id=auction_id))
    
    try:
        # Create new bid
        new_bid = Bid(
            auction_id=auction_id,
            user_id=current_user.id,
            amount=bid_amount
        )
        db.session.add(new_bid)
        
        # Update auction's current bid
        auction.current_bid = bid_amount
        
        db.session.commit()
        
        flash(f'Bid of {bid_amount:.0f} SEK placed successfully!', 'success')
        
        # Return JSON for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': f'Bid of {bid_amount:.0f} SEK placed successfully!',
                'new_current_bid': bid_amount,
                'bid_count': auction.bid_count + 1
            })
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while placing your bid. Please try again.', 'error')
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': False,
                'message': 'An error occurred while placing your bid.'
            })
    
    return redirect(url_for('auction.auction_detail', auction_id=auction_id))

@bidding_bp.route('/history/<int:auction_id>')
def bid_history(auction_id):
    """Get bid history for an auction (API endpoint)"""
    auction = Auction.query.get_or_404(auction_id)
    
    # Get bid history with user information
    bids = db.session.query(Bid, User).\
        join(User, Bid.user_id == User.id).\
        filter(Bid.auction_id == auction_id).\
        order_by(Bid.created_at.desc()).\
        limit(20).all()
    
    bid_data = []
    for bid, user in bids:
        # Mask email for privacy unless admin
        if current_user.is_authenticated and current_user.is_admin:
            bidder_name = f"{user.full_name} ({user.email})"
        else:
            email_parts = user.email.split('@')
            masked_email = f"{email_parts[0][0]}***@{email_parts[1]}"
            bidder_name = masked_email
        
        bid_data.append({
            'id': bid.id,
            'amount': bid.amount,
            'bidder': bidder_name,
            'created_at': bid.created_at.isoformat(),
            'formatted_time': bid.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({
        'auction_id': auction_id,
        'auction_title': auction.title,
        'bids': bid_data
    })

@bidding_bp.route('/my-bids')
@login_required
def my_bids():
    """Show user's bidding history"""
    # Get user's bids with auction information
    user_bids = db.session.query(Bid, Auction).\
        join(Auction, Bid.auction_id == Auction.id).\
        filter(Bid.user_id == current_user.id).\
        order_by(Bid.created_at.desc()).all()
    
    # Group bids by auction and determine status
    auction_bids = {}
    for bid, auction in user_bids:
        if auction.id not in auction_bids:
            # Get highest bid for this auction
            highest_bid = Bid.query.filter_by(auction_id=auction.id).\
                order_by(Bid.amount.desc(), Bid.created_at.asc()).first()
            
            # Get user's highest bid for this auction
            user_highest = Bid.query.filter_by(
                auction_id=auction.id, 
                user_id=current_user.id
            ).order_by(Bid.amount.desc()).first()
            
            auction_bids[auction.id] = {
                'auction': auction,
                'user_highest_bid': user_highest,
                'is_winning': highest_bid and highest_bid.user_id == current_user.id,
                'current_highest': highest_bid.amount if highest_bid else auction.starting_bid,
                'bid_count': len([b for b, a in user_bids if a.id == auction.id])
            }
    
    return render_template('bidding/my_bids.html', auction_bids=auction_bids)

@bidding_bp.route('/validate', methods=['POST'])
@login_required
def validate_bid():
    """Validate a bid amount before submission (AJAX)"""
    auction_id = request.json.get('auction_id')
    bid_amount = request.json.get('amount')
    
    if not auction_id or not bid_amount:
        return jsonify({'valid': False, 'message': 'Missing auction ID or bid amount'})
    
    try:
        bid_amount = float(bid_amount)
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'message': 'Invalid bid amount format'})
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'valid': False, 'message': 'Auction not found'})
    
    if not auction.is_ongoing:
        return jsonify({'valid': False, 'message': 'Auction is not active'})
    
    current_highest = auction.current_bid or auction.starting_bid
    if bid_amount <= current_highest:
        return jsonify({
            'valid': False, 
            'message': f'Bid must be higher than {current_highest:.0f} SEK'
        })
    
    # Check if user is already highest bidder
    highest_bid = Bid.query.filter_by(auction_id=auction_id).\
        order_by(Bid.amount.desc(), Bid.created_at.asc()).first()
    
    if highest_bid and highest_bid.user_id == current_user.id:
        return jsonify({
            'valid': False,
            'message': 'You are already the highest bidder'
        })
    
    return jsonify({
        'valid': True,
        'message': f'Bid of {bid_amount:.0f} SEK is valid'
    })
