from datetime import datetime
from flask_login import UserMixin
from database import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cashier') # admin, cashier

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    nic = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rentals = db.relationship('Rental', backref='customer', lazy=True)

class Dress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    dress_code = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    rent_price = db.Column(db.Float, nullable=False) # For 3 days / 75 hours
    deposit_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Available') # Available, Rented, Maintenance, Returned, Damaged
    condition_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rentals = db.relationship('Rental', backref='dress', lazy=True)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    dress_id = db.Column(db.Integer, db.ForeignKey('dress.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    due_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Returned, Overdue
    total_rent = db.Column(db.Float, nullable=False)
    late_fee = db.Column(db.Float, default=0.0)
    security_deposit_status = db.Column(db.String(20), default='Held') # Held, Refunded, Forfeited
    payments = db.relationship('Payment', backref='rental', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False) # Advance, Balance, LateFee, Deposit
    payment_method = db.Column(db.String(20), nullable=False) # Cash, Card, Online
