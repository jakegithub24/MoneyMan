import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

# Import database connection helpers
from db import get_db_connection, init_db, hash_pin, verify_pin

app = Flask(__name__)
app.secret_key = 'moneyman_secret_key_for_security_and_sessions'

# Ensure the database is initialized before any requests
with app.app_context():
    init_db()

# Helper function to check if the user is onboarded
def is_user_onboarded():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    conn.close()
    if user and user['is_onboarded'] == 1:
        return True
    return False

# Helper function to get current user details
def get_user_profile():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    conn.close()
    if user:
        return {
            'username': user['username'],
            'persona': user['persona'],
            'user_role': f"{user['persona'].replace('_', ' ').title()} Profile"
        }
    return {
        'username': 'Happy User',
        'persona': 'student',
        'user_role': 'Student Profile'
    }

# Helper to format numbers with commas (Indian formatting style or standard)
def format_currency(val):
    try:
        return f"{int(val):,}"
    except (ValueError, TypeError):
        return "0"

# Category Icon Map
def get_category_icon(category):
    icons = {
        'food': 'restaurant',
        'transport': 'directions_bus',
        'rent': 'house',
        'entertainment': 'movie',
        'study': 'menu_book',
        'shopping': 'shopping_bag'
    }
    return icons.get(category.lower(), 'payments')

# Budget styling generator
def get_budget_status_styles(percent):
    if percent >= 100:
        return {
            'status': 'danger',
            'color': 'bg-secondary',
            'icon_bg': 'bg-expense-red-subtle text-error dark:bg-error/20 dark:text-secondary-fixed-dim'
        }
    elif percent >= 80:
        return {
            'status': 'warning',
            'color': 'bg-tertiary',
            'icon_bg': 'bg-tertiary-fixed text-tertiary-container dark:bg-tertiary/20 dark:text-tertiary-fixed-dim'
        }
    else:
        return {
            'status': 'good',
            'color': 'bg-primary-container',
            'icon_bg': 'bg-income-green-subtle text-primary dark:bg-primary/20 dark:text-primary-fixed'
        }

# Goal styling generator
def get_goal_styles(percent):
    if percent >= 50:
        return {
            'status': 'On Track',
            'status_color': 'text-primary dark:text-primary-fixed',
            'bar_color': 'bg-primary-container',
            'icon_bg': 'bg-income-green-subtle text-primary dark:bg-primary/20 dark:text-primary-fixed',
            'bg_decor': 'bg-income-green-subtle dark:bg-primary/10'
        }
    else:
        return {
            'status': 'Needs Attention',
            'status_color': 'text-secondary dark:text-secondary-fixed-dim',
            'bar_color': 'bg-tertiary',
            'icon_bg': 'bg-surface-container-high text-on-surface-variant dark:bg-tertiary/20 dark:text-tertiary-fixed-dim',
            'bg_decor': 'bg-secondary-fixed-dim dark:bg-secondary/10'
        }

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    if is_user_onboarded():
        return redirect(url_for('dashboard'))
    return redirect(url_for('onboarding'))

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == 'POST':
        persona = request.form.get('persona', 'student')
        pin = request.form.get('pin', '1234')
        
        # Determine default username based on persona
        default_names = {
            'student': 'Aarav Mehta',
            'gig_worker': 'Kabir Singh',
            'retired': 'Ramesh Kumar'
        }
        username = default_names.get(persona, 'MoneyMan User')
        
        # Hash the PIN
        hashed_pin = hash_pin(pin)
        
        # Save or Update User in database
        conn = get_db_connection()
        conn.execute("DELETE FROM users") # Clear any old users
        conn.execute(
            "INSERT INTO users (username, persona, pin, is_onboarded) VALUES (?, ?, ?, 1)",
            (username, persona, hashed_pin)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
        
    if is_user_onboarded():
        return redirect(url_for('dashboard'))
    return render_template('onboarding.html')

@app.route('/dashboard')
def dashboard():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    profile = get_user_profile()
    conn = get_db_connection()
    
    # 1. Calculate Summary Cards Values
    # Total Income
    inc_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='income'").fetchone()
    income_val = inc_row[0] if inc_row[0] is not None else 0.0
    
    # Total Expenses
    exp_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'").fetchone()
    expense_val = exp_row[0] if exp_row[0] is not None else 0.0
    
    # Savings Progress (total saved across goals)
    sav_row = conn.execute("SELECT SUM(saved_amount) FROM goals").fetchone()
    savings_val = sav_row[0] if sav_row[0] is not None else 0.0
    
    # Upcoming EMIs Monthly Total
    emi_row = conn.execute("SELECT SUM(amount) FROM emis").fetchone()
    emi_val = emi_row[0] if emi_row[0] is not None else 0.0
    
    # 2. Calculate Weekly Spending (Expenses this month)
    # Query current month's expenses
    month_expenses = conn.execute("""
        SELECT amount, date FROM transactions 
        WHERE type='expense' AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """).fetchall()
    
    week_totals = [0.0] * 5
    for row in month_expenses:
        try:
            day = int(row['date'].split('-')[2])
        except (IndexError, ValueError):
            continue
        
        if day <= 7:
            week_totals[0] += row['amount']
        elif day <= 14:
            week_totals[1] += row['amount']
        elif day <= 21:
            week_totals[2] += row['amount']
        elif day <= 28:
            week_totals[3] += row['amount']
        else:
            week_totals[4] += row['amount']
            
    # Calculate chart heights relative to the highest spending week (max height 90%)
    max_week = max(week_totals)
    spending_weekly = []
    for val in week_totals:
        if val == 0:
            spending_weekly.append(5) # small spacer so week is visible
        elif max_week > 0:
            spending_weekly.append(max(10, int((val / max_week) * 90)))
        else:
            spending_weekly.append(10)
            
    # 3. Fetch Upcoming Bills (Combining active EMIs and a mock utility bill)
    upcoming_emis = conn.execute("SELECT name, amount FROM emis LIMIT 2").fetchall()
    bills = []
    
    # Feed active EMIs to upcoming list
    for index, emi in enumerate(upcoming_emis):
        due_days = 3 if index == 0 else 7
        bills.append({
            'title': emi['name'],
            'due': f"Due in {due_days} days",
            'amount': format_currency(emi['amount']),
            'icon': 'calculate'
        })
        
    # If no EMIs, feed standard mock bills
    if not bills:
        bills = [
            {'title': 'Electricity Bill', 'due': 'Due in 5 days', 'amount': '1,300', 'icon': 'bolt'},
            {'title': 'Broadband Wifi', 'due': 'Due in 10 days', 'amount': '799', 'icon': 'wifi'}
        ]
        
    # 4. Generate AI Insight dynamically
    ai_insight = "You're doing great! Keep tracking your transactions to build healthy financial habits."
    if expense_val > income_val and income_val > 0:
        ai_insight = "Alert: Your spending has exceeded your income this month. Consider cutting down on non-essential categories."
    else:
        # Check if food budget is close to max
        food_spent_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND category='food'").fetchone()
        food_spent = food_spent_row[0] if food_spent_row[0] else 0.0
        if food_spent > 2500:
            ai_insight = f"AI Insight: Your Dining & Food spending is high (₹{format_currency(food_spent)}). Cooking at home twice next week will save you roughly <strong class='text-primary dark:text-primary-fixed font-bold'>₹800</strong>!"

    conn.close()

    return render_template(
        'dashboard.html',
        username=profile['username'],
        user_role=profile['user_role'],
        income=format_currency(income_val),
        expense=format_currency(expense_val),
        savings=format_currency(savings_val),
        active_emi_total=format_currency(emi_val),
        spending_weekly=spending_weekly,
        bills=bills,
        ai_insight=ai_insight
    )

@app.route('/add-transaction')
def add_transaction():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
    profile = get_user_profile()
    return render_template('add_transaction.html', username=profile['username'], user_role=profile['user_role'])

@app.route('/transaction/add', methods=['POST'])
def transaction_add():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    tx_type = request.form.get('type', 'expense')
    amount = float(request.form.get('amount', 0.0))
    category = request.form.get('category', 'other')
    date = request.form.get('date')
    note = request.form.get('note', '')
    recurring = 1 if request.form.get('recurring') == 'true' else 0
    
    if amount > 0:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO transactions (type, amount, category, date, note, recurring) VALUES (?, ?, ?, ?, ?, ?)",
            (tx_type, amount, category, date, note, recurring)
        )
        conn.commit()
        conn.close()
        
    return redirect(url_for('dashboard'))

@app.route('/budgets')
def budgets():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    profile = get_user_profile()
    conn = get_db_connection()
    
    # Fetch all budgets
    db_budgets = conn.execute("SELECT * FROM budgets").fetchall()
    active_budgets = []
    
    for budget in db_budgets:
        cat = budget['category']
        limit_val = budget['limit_amount']
        
        # Calculate amount spent in current month for this category
        spent_row = conn.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type='expense' AND category=? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        """, (cat,)).fetchone()
        spent_val = spent_row[0] if spent_row[0] is not None else 0.0
        
        percent = int((spent_val / limit_val * 100)) if limit_val > 0 else 0
        styles = get_budget_status_styles(percent)
        
        active_budgets.append({
            'category': cat.title(),
            'spent': format_currency(spent_val),
            'limit': format_currency(limit_val),
            'percent': percent,
            'status': styles['status'],
            'color': styles['color'],
            'icon_bg': styles['icon_bg'],
            'icon': get_category_icon(cat)
        })
        
    conn.close()
    return render_template('budgets.html', username=profile['username'], user_role=profile['user_role'], active_budgets=active_budgets)

@app.route('/budgets/create', methods=['POST'])
def budgets_create():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    category = request.form.get('category', 'other').lower()
    limit = float(request.form.get('limit', 0.0))
    alert_threshold = 80 if request.form.get('alert_80') else 0
    
    if limit > 0:
        conn = get_db_connection()
        conn.execute("""
            INSERT OR REPLACE INTO budgets (category, limit_amount, alert_threshold)
            VALUES (?, ?, ?)
        """, (category, limit, alert_threshold))
        conn.commit()
        conn.close()
        
    return redirect(url_for('budgets'))

@app.route('/emi')
def emi():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    profile = get_user_profile()
    conn = get_db_connection()
    
    # Fetch active EMIs
    db_emis = conn.execute("SELECT * FROM emis").fetchall()
    emis = []
    
    for item in db_emis:
        emis.append({
            'name': item['name'],
            'bank': item['bank'],
            'amount': format_currency(item['amount']),
            'remaining_months': item['remaining_months'],
            'total_months': item['total_months'],
            'icon': item['icon'],
            'color': item['color']
        })
        
    conn.close()
    return render_template('emi.html', username=profile['username'], user_role=profile['user_role'], emis=emis)

@app.route('/emi/create', methods=['POST'])
def emi_create():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    name = request.form.get('name', 'Personal Loan')
    bank = request.form.get('bank', 'General Bank')
    amount = float(request.form.get('amount', 0.0))
    total_months = int(request.form.get('total_months', 12))
    
    # Map icon and progress bar color based on loan name keywords
    name_lower = name.lower()
    icon = 'calculate'
    color = 'bg-primary'
    
    if 'home' in name_lower or 'house' in name_lower:
        icon = 'home'
        color = 'bg-tertiary-container'
    elif 'phone' in name_lower or 'mobile' in name_lower or 'gadget' in name_lower:
        icon = 'smartphone'
        color = 'bg-primary'
    elif 'car' in name_lower or 'bike' in name_lower or 'vehicle' in name_lower:
        icon = 'directions_car'
        color = 'bg-secondary-container'
        
    if amount > 0 and total_months > 0:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO emis (name, bank, amount, remaining_months, total_months, icon, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, bank, amount, total_months, total_months, icon, color))
        conn.commit()
        conn.close()
        
    return redirect(url_for('emi'))

@app.route('/goals')
def goals():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    profile = get_user_profile()
    conn = get_db_connection()
    
    # Fetch active goals
    db_goals = conn.execute("SELECT * FROM goals").fetchall()
    active_goals = []
    
    for item in db_goals:
        saved = item['saved_amount']
        target = item['target_amount']
        percent = int((saved / target * 100)) if target > 0 else 0
        styles = get_goal_styles(percent)
        
        active_goals.append({
            'id': item['id'],
            'name': item['name'],
            'tag': item['tag'],
            'saved': format_currency(saved),
            'target': format_currency(target),
            'percent': percent,
            'status': styles['status'],
            'status_color': styles['status_color'],
            'bar_color': styles['bar_color'],
            'icon': item['icon'] or 'flag',
            'icon_bg': item['icon_bg'] or 'bg-surface-container-high text-on-surface dark:bg-surface-container/20',
            'bg_decor': item['bg_decor'] or 'bg-surface-container-high/40'
        })
        
    conn.close()
    return render_template('goals.html', username=profile['username'], user_role=profile['user_role'], active_goals=active_goals)

@app.route('/goals/create', methods=['POST'])
def goals_create():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    name = request.form.get('name')
    target = float(request.form.get('target', 0.0))
    tag = request.form.get('tag', 'Other')
    target_date = request.form.get('target_date', '')
    
    # Map styles based on Tag selected
    icon = 'flag'
    icon_bg = 'bg-surface-container-high text-on-surface-variant dark:bg-surface-container/20 dark:text-text-main-dark'
    bg_decor = 'bg-surface-container-high dark:bg-surface-container/10'
    
    if tag == 'Safety Net':
        icon = 'health_and_safety'
        icon_bg = 'bg-income-green-subtle text-primary dark:bg-primary/20 dark:text-primary-fixed'
        bg_decor = 'bg-income-green-subtle dark:bg-primary/10'
    elif tag == 'Tech':
        icon = 'laptop_mac'
        icon_bg = 'bg-surface-container-high text-tertiary dark:bg-tertiary/20 dark:text-tertiary-fixed-dim'
        bg_decor = 'bg-secondary-fixed-dim dark:bg-secondary/10'
    elif tag == 'Travel':
        icon = 'flight'
        icon_bg = 'bg-tertiary-fixed text-on-tertiary-fixed-variant dark:bg-tertiary/20'
        bg_decor = 'bg-tertiary-fixed/30 dark:bg-tertiary/10'
    elif tag == 'Education':
        icon = 'school'
        icon_bg = 'bg-primary-fixed text-on-primary-fixed-variant dark:bg-primary/20'
        bg_decor = 'bg-primary-fixed/30 dark:bg-primary/10'
        
    if name and target > 0:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO goals (name, tag, saved_amount, target_amount, target_date, icon, icon_bg, bg_decor)
            VALUES (?, ?, 0.0, ?, ?, ?, ?, ?)
        """, (name, tag, target, target_date, icon, icon_bg, bg_decor))
        conn.commit()
        conn.close()
        
    return redirect(url_for('goals'))

@app.route('/goals/update', methods=['POST'])
def goals_update():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    goal_id = int(request.form.get('goal_id', 0))
    saved_amount = float(request.form.get('saved_amount', 0.0))
    
    if goal_id > 0:
        conn = get_db_connection()
        conn.execute("UPDATE goals SET saved_amount=? WHERE id=?", (saved_amount, goal_id))
        conn.commit()
        conn.close()
        
    return redirect(url_for('goals'))

@app.route('/learn')
def learn():
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
    profile = get_user_profile()
    return render_template('learn.html', username=profile['username'], user_role=profile['user_role'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print("Starting MoneyMan Web Server on Localhost...")
    print(f"Open http://127.0.0.1:{port}/ to view the app.")
    app.run(debug=True, port=port)
