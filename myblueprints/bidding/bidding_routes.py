from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.auction import Auction
from models.bid import Bid
from models.like import Like
from models.user import User
from database import db
from datetime import datetime
from . import bidding_bp

@bidding_bp.route('/place/<int:auction_id>', methods=['POST'])
@login_required
def place_bid(auction_id):
    """Place a bid on an auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        # Validate bid amount
        if amount <= 0:
            flash('Bid amount must be greater than zero.', 'error')
            return redirect(url_for('auctions_bp.auction_detail', auction_id=auction_id))
        
        # Check if the user has already placed a bid on this auction
        existing_bid = Bid.query.filter_by(user_id=current_user.id, auction_id=auction_id).first()
        if existing_bid:
            flash('You have already placed a bid on this auction.', 'error')
            return redirect(url_for('auctions_bp.auction_detail', auction_id=auction_id))
        
        # Check if the new bid is higher than the current highest bid
        if existing_bid and amount <= existing_bid.amount:
            flash('Your bid must be higher than the current highest bid.', 'error')
            return redirect(url_for('auctions_bp.auction_detail', auction_id=auction_id))
        
        # Create a new bid
        new_bid = Bid(
            amount=amount,
            user_id=current_user.id,
            auction_id=auction_id
        )
        
        db.session.add(new_bid)
        db.session.commit()
        
        # Update current_bid for the auction
        remaining_bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.amount.desc()).all()
        if remaining_bids:
            auction.current_bid = remaining_bids[0].amount
        
        flash('Bid placed successfully!', 'success')
        return redirect(url_for('auctions_bp.auction_detail', auction_id=auction_id))
    
    return render_template('bidding/place.html', auction=auction)

@bidding_bp.route('/history/<int:auction_id>')
@login_required
def bid_history(auction_id):
    """View bid history for a specific auction"""
    auction = Auction.query.get_or_404(auction_id)
    
    # Get all bids with bidder information
    bids = db.session.query(Bid, User).\
        join(User, Bid.user_id == User.id).\
        filter(Bid.auction_id == auction_id).\
        order_by(Bid.created_at.desc()).all()
    
    return render_template('bidding/history.html', auction=auction, bids=bids)

@bidding_bp.route('/my-bids')
@login_required
def my_bids():
    """View all bids made by the current user"""
    user = User.query.get_or_404(current_user.id)
    
    # Get all bids made by the user
    bids = db.session.query(Bid, Auction).\
        join(Auction, Bid.auction_id == Auction.id).\
        filter(Bid.user_id == current_user.id).\
        order_by(Bid.created_at.desc()).all()
    
    return render_template('bidding/my_bids.html', user=user, bids=bids)

@bidding_bp.route('/validate', methods=['POST'])
@login_required
def validate_bid():
    """Validate a bid"""
    auction_id = request.form.get('auction_id')
    amount = float(request.form.get('amount'))
    
    # Validate bid amount
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Bid amount must be greater than zero.'})
    
    # Check if the user has already placed a bid on this auction
    existing_bid = Bid.query.filter_by(user_id=current_user.id, auction_id=auction_id).first()
    if existing_bid:
        return jsonify({'success': False, 'message': 'You have already placed a bid on this auction.'})
    
    # Check if the new bid is higher than the current highest bid
    if existing_bid and amount <= existing_bid.amount:
        return jsonify({'success': False, 'message': 'Your bid must be higher than the current highest bid.'})
    
    return jsonify({'success': True, 'message': 'Bid is valid.'})
