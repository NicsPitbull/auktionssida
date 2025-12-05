from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import admin_bp
from myblueprints.auth import admin_required
from models.auction import Auction
from models.bid import Bid
from models.user import User  # Importera User-modellen
from database import db
from datetime import datetime

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard showing overview of auctions and bids"""
    total_auctions = Auction.query.count()
    active_auctions = Auction.query.filter(Auction.end_time > datetime.now()).count()
    total_bids = Bid.query.count()
    total_users = User.query.count()  # Använd modellen för att räkna användare
    
    recent_auctions = Auction.query.order_by(Auction.created_at.desc()).limit(5).all()
    recent_bids = Bid.query.order_by(Bid.bid_time.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_auctions=total_auctions,
                         active_auctions=active_auctions,
                         total_bids=total_bids,
                         total_users=total_users,
                         recent_auctions=recent_auctions,
                         recent_bids=recent_bids)
