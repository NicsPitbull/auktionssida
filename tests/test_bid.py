import pytest
from flask import Flask
from myblueprints.bidding import bidding_routes
from models.bid import Bid
from datetime import datetime, timedelta
from database import db
from models.user import User  # Importera User modellen

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(bidding_routes.bidding_bp)
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_place_bid(client):
    auction = Bid(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.post(f'/bidding/place/{auction.id}', data={'amount': 200.0})
    assert response.status_code == 302
    assert b'Bid placed successfully!' in response.data

def test_bid_history(client):
    auction = Bid(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.get(f'/bidding/history/{auction.id}')
    assert response.status_code == 200
    assert b'Bid History' in response.data

def test_my_bids(client):
    user = User(email='test@example.com', password='password', first_name='Test', last_name='User')
    db.session.add(user)
    db.session.commit()
    
    auction = Bid(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    bid = Bid(amount=200.0, user_id=user.id, auction_id=auction.id)
    db.session.add(bid)
    db.session.commit()
    
    client.post(f'/auth/login', data={'email': 'test@example.com', 'password': 'password'})
    response = client.get('/bidding/my-bids')
    assert response.status_code == 200
    assert b'My Bids' in response.data

def test_validate_bid(client):
    auction = Bid(title='Test Auction', description='This is a test auction.', starting_bid=100.0, start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow() + timedelta(days=7))
    db.session.add(auction)
    db.session.commit()
    
    response = client.post('/bidding/validate', data={'auction_id': auction.id, 'amount': 200.0})
    assert response.status_code == 200
    assert b'Success' in response.data
