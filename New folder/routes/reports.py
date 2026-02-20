from flask import Blueprint, render_template
from flask_login import login_required
from models import db, Payment, Rental, Dress
from sqlalchemy import func
from utils import admin_required
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/dashboard')
@login_required
def dashboard():
    from flask_login import current_user
    
    # Defaults
    daily_income = 0
    monthly_income = 0
    yearly_income = 0
    available_dresses = []
    rented_dresses = []
    maintenance_dresses = []
    month_breakdown = []
    monthly_chart_data = {'labels': [], 'data': []}
    today = datetime.utcnow().date()

    # Shared Data (Cashier & Admin)
    # Upcoming Returns
    upcoming_returns = Rental.query.filter(Rental.status == 'Active').order_by(Rental.due_time.asc()).limit(15).all()
    
    # Reminders: Due within next 3 days
    three_days_from_now = datetime.utcnow() + timedelta(days=3)
    reminders = Rental.query.filter(
        Rental.status == 'Active',
        Rental.due_time <= three_days_from_now
    ).order_by(Rental.due_time.asc()).all()

    if current_user.role == 'admin':
        # Dress Status Counts and Lists
        available_dresses = Dress.query.filter_by(status='Available').all()
        rented_dresses = Dress.query.filter(Dress.status.in_(['Rented'])).all()
        maintenance_dresses = Dress.query.filter(Dress.status.in_(['Maintenance', 'Damaged', 'Retired'])).all()

        # Financials
        today_dt = datetime.utcnow().date()
        daily_income = db.session.query(func.sum(Payment.amount))\
            .filter(func.date(Payment.payment_date) == today_dt).scalar() or 0.0
        
        current_month = datetime.utcnow().strftime('%Y-%m')
        monthly_income = db.session.query(func.sum(Payment.amount))\
            .filter(func.strftime('%Y-%m', Payment.payment_date) == current_month).scalar() or 0.0

        current_year = datetime.utcnow().strftime('%Y')
        yearly_income = db.session.query(func.sum(Payment.amount))\
            .filter(func.strftime('%Y', Payment.payment_date) == current_year).scalar() or 0.0

        # Daily Income Breakdown (Current Month)
        start_date = datetime(today.year, today.month, 1).date()
        import calendar
        _, last_day = calendar.monthrange(today.year, today.month)
        end_date = datetime(today.year, today.month, last_day).date()

        daily_totals = db.session.query(
            func.date(Payment.payment_date), 
            func.sum(Payment.amount)
        ).filter(
            func.date(Payment.payment_date) >= start_date,
            func.date(Payment.payment_date) <= end_date
        ).group_by(func.date(Payment.payment_date)).all()
        
        totals_map = {str(day): amount for day, amount in daily_totals}
        
        current_iter_date = start_date
        while current_iter_date <= end_date:
            date_str = current_iter_date.strftime('%Y-%m-%d')
            amount = totals_map.get(date_str, 0.0)
            month_breakdown.append({'date': current_iter_date, 'amount': amount})
            current_iter_date += timedelta(days=1)

        # Monthly Chart Data (Last 12 Months or Current Year)
        # Using Current Year Jan-Dec
        months_labels = []
        months_data = []
        for i in range(1, 13):
            month_str = f"{today.year}-{i:02d}"
            # Get month name
            month_name = datetime.strptime(month_str, "%Y-%m").strftime("%b")
            months_labels.append(month_name)
            
            m_income = db.session.query(func.sum(Payment.amount))\
                .filter(func.strftime('%Y-%m', Payment.payment_date) == month_str).scalar() or 0.0
            months_data.append(m_income)
            
        monthly_chart_data = {'labels': months_labels, 'data': months_data}

    return render_template('reports/dashboard.html', 
                         daily_income=daily_income,
                         monthly_income=monthly_income, 
                         yearly_income=yearly_income,
                         available_dresses=available_dresses,
                         rented_dresses=rented_dresses,
                         maintenance_dresses=maintenance_dresses,
                         upcoming_returns=upcoming_returns,
                         reminders=reminders,
                         month_breakdown=month_breakdown,
                         monthly_chart_data=monthly_chart_data,
                         today_date=today)
