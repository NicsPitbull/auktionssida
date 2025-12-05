import pytest
from flask import Flask
from myblueprints.auction import auction_routes
from models.auction import Auction
from datetime import datetime, timedelta
from database import db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(auction_routes.auctions_bp)
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_browse_auctions(client):
    response = client.get('/auctions')
    assert response.status_code == 200
    assert b'Auktioner' in response.data

def test_auction_detail(client):
    auction = Auction(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.get(f'/auctions/{auction.id}')
    assert response.status_code == 200
    assert b'Test Auction' in response.data

def test_toggle_like(client):
    auction = Auction(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.post(f'/auctions/{auction.id}/like')
    assert response.status_code == 302
    assert b'Liked Test Auction' in response.data

def test_toggle_dislike(client):
    auction = Auction(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.post(f'/auctions/{auction.id}/dislike')
    assert response.status_code == 302
    assert b'Disliked Test Auction' in response.data

def test_get_categories(client):
    response = client.get('/categories')
    assert response.status_code == 200
    assert b'Categories' in response.data

def test_search_auctions(client):
    auction = Auction(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.get('/search?q=test')
    assert response.status_code == 200
    assert b'Test Auction' in response.data
