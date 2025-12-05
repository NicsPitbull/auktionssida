from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from myblueprints.auth import admin_required
from dbrepositories.auction_repository import AuctionRepository
from dbrepositories.bid_repository import BidRepository
from dbrepositories.user_repository import UserRepository
from models.auction import Auction
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)
auction_repo = AuctionRepository()
bid_repo = BidRepository()
user_repo = UserRepository()

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    # Get statistics
    total_auctions = len(auction_repo.get_all())
    active_auctions = len([a for a in auction_repo.get_all() if a.status == 'active'])
    total_bids = len(bid_repo.get_all())
    total_users = len(user_repo.get_all())
    
    # Get recent auctions
    recent_auctions = auction_repo.get_all()[:5]  # Get first 5
    
    # Get recent bids
    recent_bids = bid_repo.get_all()[:10]  # Get first 10
    
    return render_template('admin/dashboard.html',
                         total_auctions=total_auctions,
                         active_auctions=active_auctions,
                         total_bids=total_bids,
                         total_users=total_users,
                         recent_auctions=recent_auctions,
                         recent_bids=recent_bids)

@admin_bp.route('/auctions')
@login_required
@admin_required
def manage_auctions():
    """Manage all auctions - list, edit, delete."""
    auctions = auction_repo.get_all()
    return render_template('admin/manage_auctions.html', auctions=auctions)

@admin_bp.route('/auctions/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_auction():
    """Create a new auction."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        starting_bid = float(request.form.get('starting_bid', 0))
        category = request.form.get('category')
        duration_hours = int(request.form.get('duration_hours', 24))
        
        # Validation
        if not all([title, description, category]):
            flash('All fields are required.', 'error')
            return render_template('admin/create_auction.html')
        
        if starting_bid <= 0:
            flash('Starting bid must be greater than 0.', 'error')
            return render_template('admin/create_auction.html')
        
        # Calculate end time
        end_time = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Create auction
        try:
            new_auction = Auction(
                title=title,
                description=description,
                starting_bid=starting_bid,
                current_bid=starting_bid,
                category=category,
                end_time=end_time,
                status='active'
            )
            
            auction_repo.create(new_auction)
            flash(f'Auction "{title}" created successfully!', 'success')
            return redirect(url_for('admin.manage_auctions'))
        except Exception as e:
            flash('Failed to create auction. Please try again.', 'error')
            return render_template('admin/create_auction.html')
    
    return render_template('admin/create_auction.html')

@admin_bp.route('/auctions/<int:auction_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_auction(auction_id):
    """Edit an existing auction."""
    auction = auction_repo.get_by_id(auction_id)
    if not auction:
        flash('Auction not found.', 'error')
        return redirect(url_for('admin.manage_auctions'))
    
    if request.method == 'POST':
        auction.title = request.form.get('title')
        auction.description = request.form.get('description')
        auction.category = request.form.get('category')
        auction.status = request.form.get('status')
        
        # Only allow changing starting_bid if no bids have been placed
        if not auction.bids:
            new_starting_bid = float(request.form.get('starting_bid', auction.starting_bid))
            auction.starting_bid = new_starting_bid
            auction.current_bid = new_starting_bid
        
        try:
            auction_repo.update(auction)
            flash(f'Auction "{auction.title}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_auctions'))
        except Exception as e:
            flash('Failed to update auction. Please try again.', 'error')
    
    return render_template('admin/edit_auction.html', auction=auction)

@admin_bp.route('/auctions/<int:auction_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_auction(auction_id):
    """Delete an auction and all its bids."""
    auction = auction_repo.get_by_id(auction_id)
    if not auction:
        flash('Auction not found.', 'error')
        return redirect(url_for('admin.manage_auctions'))
    
    try:
        # Delete all bids for this auction first
        for bid in auction.bids:
            bid_repo.delete(bid.id)
        
        # Delete the auction
        auction_repo.delete(auction_id)
        flash(f'Auction "{auction.title}" and all its bids deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete auction. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_auctions'))

@admin_bp.route('/bids')
@login_required
@admin_required
def manage_bids():
    """Manage all bids - view and delete."""
    bids = bid_repo.get_all()
    return render_template('admin/manage_bids.html', bids=bids)

@admin_bp.route('/bids/<int:bid_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_bid(bid_id):
    """Delete a specific bid."""
    bid = bid_repo.get_by_id(bid_id)
    if not bid:
        flash('Bid not found.', 'error')
        return redirect(url_for('admin.manage_bids'))
    
    try:
        auction = bid.auction
        bid_repo.delete(bid_id)
        
        # Recalculate current bid for the auction
        remaining_bids = [b for b in auction.bids if b.id != bid_id]
        if remaining_bids:
            auction.current_bid = max(b.amount for b in remaining_bids)
        else:
            auction.current_bid = auction.starting_bid
        
        auction_repo.update(auction)
        flash('Bid deleted successfully and auction updated!', 'success')
    except Exception as e:
        flash('Failed to delete bid. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_bids'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """View all users."""
    users = user_repo.get_all()
    return render_template('admin/manage_users.html', users=users)