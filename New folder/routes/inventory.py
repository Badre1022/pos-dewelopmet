from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Dress
from utils import admin_required
import uuid

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def list_inventory():
    dresses = Dress.query.all()
    return render_template('inventory/list.html', dresses=dresses)

@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_dress():
    if request.method == 'POST':
        try:
            barcode = request.form['barcode']
            if not barcode:
                barcode = str(uuid.uuid4()).split('-')[0].upper() # Generate short unique ID

            dress = Dress(
                barcode=barcode,
                dress_code=request.form.get('dress_code'),
                category=request.form['category'],
                color=request.form['color'],
                size=request.form['size'],
                rent_price=float(request.form['rent_price']),
                deposit_amount=float(request.form['deposit_amount']),
                condition_notes=request.form.get('condition_notes')
            )
            db.session.add(dress)
            db.session.commit()
            flash('Dress added successfully!', 'success')
            return redirect(url_for('inventory.list_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding dress: {str(e)}', 'danger')
            
    return render_template('inventory/add.html')

@inventory_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_dress(id):
    dress = Dress.query.get_or_404(id)
    if request.method == 'POST':
        dress.barcode = request.form['barcode']
        dress.dress_code = request.form.get('dress_code')
        dress.category = request.form['category']
        dress.color = request.form['color']
        dress.size = request.form['size']
        dress.rent_price = float(request.form['rent_price'])
        dress.deposit_amount = float(request.form['deposit_amount'])
        dress.status = request.form['status']
        dress.condition_notes = request.form.get('condition_notes')
        
        db.session.commit()
        flash('Dress updated successfully!', 'success')
        return redirect(url_for('inventory.list_inventory'))
        
    return render_template('inventory/edit.html', dress=dress)
