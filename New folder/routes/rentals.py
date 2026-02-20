from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import db, Rental, Dress, Customer, Payment

rental_bp = Blueprint('rental', __name__, url_prefix='/rentals')

def calculate_fees(rental):
    """Calculate late fees based on 75 hour rule"""
    if rental.status != 'Active':
        return 0.0
    
    now = datetime.utcnow()
    if now <= rental.due_time:
        return 0.0
    
    overdue_duration = now - rental.due_time
    overdue_hours = overdue_duration.total_seconds() / 3600
    
    # Example logic: 10% of rent price per overdue hour (customize as needed)
    # late_fee_per_hour = rental.total_rent * 0.05 
    late_fee_per_hour = 100.0 # Fixed amount or percentage
    
    return round(overdue_hours * late_fee_per_hour, 2)

@rental_bp.route('/check_availability', methods=['POST'])
@login_required
def check_availability():
    data = request.get_json()
    barcode = data.get('barcode')
    dress = Dress.query.filter_by(barcode=barcode).first()
    
    if not dress:
        return jsonify({'status': 'error', 'message': 'Dress not found'})
    
    if dress.status == 'Available':
        return jsonify({
            'status': 'success', 
            'message': 'Dress is Available',
            'dress': {
                'category': dress.category,
                'color': dress.color,
                'size': dress.size,
                'rent_price': dress.rent_price
            }
        })
    else:
        return jsonify({'status': 'warning', 'message': f'Dress is currently {dress.status}'})

@rental_bp.route('/<int:id>/receipt')
@login_required
def receipt(id):
    rental = Rental.query.get_or_404(id)
    return render_template('rentals/receipt.html', rental=rental)

@rental_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_rental():
    if request.method == 'POST':
        try:
            barcode = request.form['barcode']
            customer_id = request.form['customer_id']
            advance_amount = float(request.form['advance_amount'])
            
            dress = Dress.query.filter_by(barcode=barcode).first()
            if not dress:
                flash('Invalid Barcode', 'danger')
                return redirect(url_for('rental.new_rental'))
            
            if dress.status != 'Available':
                flash(f'Dress is currently {dress.status}', 'warning')
                return redirect(url_for('rental.new_rental'))
                
            customer = Customer.query.get(customer_id)
            
            # Create Rental
            start_hash = datetime.utcnow()
            # Due time is 75 hours from now (3 days + 3 hours approx)
            due_time = start_hash + timedelta(hours=75)
            
            rental = Rental(
                customer_id=customer.id,
                dress_id=dress.id,
                start_time=start_hash,
                due_time=due_time,
                total_rent=dress.rent_price,
                security_deposit_status='Held'
            )
            
            dress.status = 'Rented'
            db.session.add(rental)
            db.session.flush() # get ID
            
            # Record Advance Payment
            if advance_amount > 0:
                payment = Payment(
                    rental_id=rental.id,
                    amount=advance_amount,
                    payment_type='Advance',
                    payment_method='Cash' # Default for now
                )
                db.session.add(payment)
                
            db.session.commit()
            flash('Rental created successfully!', 'success')
            return redirect(url_for('rental.receipt', id=rental.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            
    customers = Customer.query.all()
    return render_template('rentals/new.html', customers=customers)

@rental_bp.route('/return', methods=['GET', 'POST'])
@login_required
def return_rental():
    rental = None
    late_fee = 0.0
    balance = 0.0
    
    if request.method == 'POST':
        if 'search_barcode' in request.form:
            barcode = request.form['search_barcode']
            dress = Dress.query.filter_by(barcode=barcode).first()
            if dress:
                # Find active rental
                rental = Rental.query.filter_by(dress_id=dress.id, status='Active').first()
                if rental:
                     late_fee = calculate_fees(rental)
                     paid_so_far = sum(p.amount for p in rental.payments if p.payment_type in ['Advance', 'Balance'])
                     balance = (rental.total_rent + late_fee) - paid_so_far
                else:
                    flash('No active rental found for this dress.', 'warning')
            else:
                flash('Dress not found.', 'danger')
        
        elif 'confirm_return' in request.form:
             rental_id = request.form['rental_id']
             rental = Rental.query.get(rental_id)
             
             final_payment = float(request.form['final_payment'])
             damage_fee = float(request.form.get('damage_fee', 0))
             
             rental.return_time = datetime.utcnow()
             rental.status = 'Returned'
             rental.dress.status = 'Available' # Or Maintenance if damage
             rental.late_fee = float(request.form['late_fee_val'])
             
             # Record final payment
             if final_payment > 0:
                 db.session.add(Payment(
                     rental_id=rental.id,
                     amount=final_payment,
                     payment_type='Balance',
                     payment_method='Cash'
                 ))
                 
             if damage_fee > 0:
                 rental.dress.status = 'Maintenance'
                 # Could handle damage payment separately or include in balance
             
             db.session.commit()
             flash('Dress returned successfully!', 'success')
             return redirect(url_for('rental.receipt', id=rental.id))
             
    return render_template('rentals/return.html', rental=rental, late_fee=late_fee, balance=balance)
