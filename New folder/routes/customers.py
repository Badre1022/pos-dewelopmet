from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Customer

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')

@customer_bp.route('/')
@login_required
def list_customers():
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/list.html', customers=customers)

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            nic = request.form.get('nic')
            
            customer = Customer(name=name, phone=phone, nic=nic)
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('customer.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'danger')
            
    return render_template('customers/add.html')

@customer_bp.route('/<int:id>/history')
@login_required
def customer_history(id):
    customer = Customer.query.get_or_404(id)
    return render_template('customers/history.html', customer=customer)
