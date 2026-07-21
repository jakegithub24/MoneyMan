import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Import database connection helpers
from db import get_db_connection, init_db, hash_pin, verify_pin

from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'moneyman_secret_key_for_security_and_sessions')
CORS(app, supports_credentials=True)

# Ensure the database is initialized before any requests
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"Failed to initialize database: {e}")

@app.before_request
def check_auth():
    allowed_endpoints = ['onboarding', 'login', 'static']
    if request.endpoint in allowed_endpoints:
        return
        
    if not request.endpoint:
        return
        
    if not is_user_onboarded():
        return redirect(url_for('onboarding'))
        
    if not session.get('logged_in'):
        return redirect(url_for('login'))

# Helper function to check if the user is onboarded
def is_user_onboarded():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return False
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if user and user['is_onboarded'] == 1:
            return True
        return False
    except Exception as e:
        app.logger.error(f"Error checking user onboarding: {e}")
        return False

# Helper function to get current user details
def get_user_profile():
    try:
        user_id = session.get('user_id')
        if user_id:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            conn.close()
            if user:
                name_val = user['name'] if 'name' in user.keys() else user['username']
                profile_pic_val = user['profile_pic'] if ('profile_pic' in user.keys() and user['profile_pic']) else None
                return {
                    'username': name_val,
                    'username_val': user['username'],
                    'persona': user['persona'],
                    'profile_pic': profile_pic_val,
                    'user_role': f"{user['persona'].replace('_', ' ').title()} Profile"
                }
    except Exception as e:
        app.logger.error(f"Error getting user profile: {e}")
    return {
        'username': 'Happy User',
        'persona': 'student',
        'profile_pic': None,
        'user_role': 'Student Profile'
    }

@app.context_processor
def inject_profile_pic():
    try:
        profile = get_user_profile()
        return {
            'profile_pic': profile.get('profile_pic')
        }
    except Exception:
        return {
            'profile_pic': None
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
    try:
        if is_user_onboarded():
            return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Index route error: {e}")
    return redirect(url_for('onboarding'))

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == 'POST':
        try:
            persona = request.form.get('persona', 'student')
            name = request.form.get('name', 'MoneyMan User')
            username = request.form.get('username', 'moneyman_user')
            pin = request.form.get('pin', '1234')
            
            sync_enabled = 1 if request.form.get('sync_enabled') == 'true' or request.form.get('sync_enabled') == 'on' else 0
            password = request.form.get('password')
            
            conn = get_db_connection()
            try:
                # Once username is taken, it is not available to others (both ways)
                existing_user = conn.execute("SELECT * FROM users WHERE username = ? AND username NOT LIKE '%_del'", (username,)).fetchone()
                
                is_existing_cloud_path = (request.form.get('already_cloud') == 'yes')
                
                if is_existing_cloud_path:
                    hashed_pin = hash_pin(pin)
                    hashed_password = hash_pin(password) if password else None
                    
                    if existing_user:
                        # Check if it was an offline user trying to log in/restore
                        if existing_user['sync_enabled'] == 0:
                            # Offline users can't login once logged out. If they do so, their data is deleted.
                            del_username = f"{existing_user['username']}_del"
                            conn.execute("UPDATE users SET username = ? WHERE user_id = ?", (del_username, existing_user['user_id']))
                            conn.execute("DELETE FROM transactions WHERE user_id = ?", (existing_user['user_id'],))
                            conn.execute("DELETE FROM budgets WHERE user_id = ?", (existing_user['user_id'],))
                            conn.execute("DELETE FROM emis WHERE user_id = ?", (existing_user['user_id'],))
                            conn.execute("DELETE FROM goals WHERE user_id = ?", (existing_user['user_id'],))
                            conn.commit()
                            return render_template('onboarding.html', error="Offline users cannot log in once logged out. Your local data has been deleted.")
                        else:
                            # Online cloud sync user restore
                            conn.execute(
                                "UPDATE users SET pin = ?, password = ?, is_onboarded = 1, sync_enabled = 1, is_logged_out = 0 WHERE user_id = ?",
                                (hashed_pin, hashed_password, existing_user['user_id'])
                            )
                            user_id = existing_user['user_id']
                    else:
                        # If they tried to log in/restore as a non-existing user, or restore from cloud sync
                        user_id = str(uuid.uuid4())
                        conn.execute(
                            "INSERT INTO users (user_id, name, username, persona, pin, password, profile_pic, is_onboarded, sync_enabled, is_logged_out) VALUES (?, ?, ?, ?, ?, ?, None, 1, 1, 0)",
                            (user_id, username, username, persona, hashed_pin, hashed_password)
                        )
                else:
                    # New profile path
                    if existing_user:
                        return render_template('onboarding.html', error="Username is already taken. Please choose another.")
                        
                    hashed_pin = hash_pin(pin)
                    hashed_password = hash_pin(password) if (sync_enabled and password) else None
                    
                    profile_pic_path = None
                    if 'profile_pic' in request.files:
                        file = request.files['profile_pic']
                        if file and file.filename != '':
                            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                            os.makedirs(upload_folder, exist_ok=True)
                            from werkzeug.utils import secure_filename
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(upload_folder, filename)
                            file.save(file_path)
                            profile_pic_path = f"/static/uploads/{filename}"
                            
                    user_id = str(uuid.uuid4())
                    conn.execute(
                        "INSERT INTO users (user_id, name, username, persona, pin, password, profile_pic, is_onboarded, sync_enabled, is_logged_out) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 0)",
                        (user_id, name, username, persona, hashed_pin, hashed_password, profile_pic_path, sync_enabled)
                    )
                conn.commit()
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Onboarding database error: {se}")
                return render_template('onboarding.html', error="Database error occurred. Please try again.")
            finally:
                conn.close()
                
            session['user_id'] = user_id
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(f"Onboarding POST error: {e}")
            return render_template('onboarding.html', error=f"An error occurred: {str(e)}")
            
    try:
        if is_user_onboarded():
            return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Onboarding GET error: {e}")
    return render_template('onboarding.html', error=request.args.get('error'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
    except Exception as e:
        app.logger.error(f"Login auth check error: {e}")
        return redirect(url_for('onboarding'))
        
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    error = None
    if request.method == 'POST':
        try:
            entered_pin = request.form.get('pin', '')
            user_id = session.get('user_id')
            if user_id:
                conn = get_db_connection()
                try:
                    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
                    
                    if user:
                        # If they are an offline user and logged out, delete local data and flag username
                        if user['sync_enabled'] == 0 and user['is_logged_out'] == 1:
                            del_username = f"{user['username']}_del"
                            conn.execute("UPDATE users SET username = ? WHERE user_id = ?", (del_username, user_id))
                            conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                            conn.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
                            conn.execute("DELETE FROM emis WHERE user_id = ?", (user_id,))
                            conn.execute("DELETE FROM goals WHERE user_id = ?", (user_id,))
                            conn.commit()
                            session.clear()
                            error = "Offline users cannot log in once logged out. Your local data has been deleted."
                        elif verify_pin(entered_pin, user['pin']):
                            conn.execute("UPDATE users SET is_logged_out = 0 WHERE user_id = ?", (user_id,))
                            conn.commit()
                            session['logged_in'] = True
                            return redirect(url_for('dashboard'))
                        else:
                            error = "Invalid security PIN. Please try again."
                    else:
                        return redirect(url_for('onboarding'))
                except sqlite3.Error as se:
                    conn.rollback()
                    app.logger.error(f"Login database error: {se}")
                    error = "Database error. Please try again."
                finally:
                    conn.close()
            else:
                return redirect(url_for('onboarding'))
        except Exception as e:
            app.logger.error(f"Login POST error: {e}")
            error = f"An error occurred: {str(e)}"
            
    try:
        profile = get_user_profile()
        username = profile['username']
    except Exception:
        username = "Happy User"
    return render_template('login.html', error=error, username=username)

@app.route('/lock')
def lock():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    try:
        user_id = session.get('user_id')
        session.clear()
        if user_id:
            conn = get_db_connection()
            try:
                conn.execute("UPDATE users SET is_logged_out = 1 WHERE user_id = ?", (user_id,))
                conn.commit()
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Logout database error: {se}")
            finally:
                conn.close()
    except Exception as e:
        app.logger.error(f"Logout error: {e}")
    return redirect(url_for('onboarding'))

@app.route('/settings')
def settings():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            sync_enabled = user['sync_enabled'] == 1 if user else False
        except sqlite3.Error as se:
            app.logger.error(f"Settings view database error: {se}")
            sync_enabled = False
        finally:
            conn.close()
            
        success = request.args.get('success')
        error = request.args.get('error')
        
        return render_template(
            'settings.html',
            username=profile['username'],
            user_role=profile['user_role'],
            sync_enabled=sync_enabled,
            success=success,
            error=error,
            active_page='settings'
        )
    except Exception as e:
        app.logger.error(f"Settings page error: {e}")
        flash("Failed to load settings.", "error")
        return redirect(url_for('dashboard'))

@app.route('/settings/change-pin', methods=['POST'])
def settings_change_pin():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        current_pin = request.form.get('current_pin', '')
        new_pin = request.form.get('new_pin', '')
        confirm_pin = request.form.get('confirm_pin', '')
        
        user_id = session.get('user_id')
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            
            if not user or not verify_pin(current_pin, user['pin']):
                return redirect(url_for('settings', error="Current PIN is incorrect."))
                
            if new_pin != confirm_pin:
                return redirect(url_for('settings', error="New PINs do not match."))
                
            if len(new_pin) != 4 or not new_pin.isdigit():
                return redirect(url_for('settings', error="PIN must be exactly 4 digits."))
                
            hashed_pin = hash_pin(new_pin)
            conn.execute("UPDATE users SET pin=? WHERE user_id=?", (hashed_pin, user_id))
            conn.commit()
        except sqlite3.Error as se:
            conn.rollback()
            app.logger.error(f"Change PIN database error: {se}")
            return redirect(url_for('settings', error="Database error. Failed to change PIN."))
        finally:
            conn.close()
            
        return redirect(url_for('settings', success="Security PIN updated successfully."))
    except Exception as e:
        app.logger.error(f"Change PIN error: {e}")
        return redirect(url_for('settings', error=f"An error occurred: {str(e)}"))

@app.route('/settings/update-sync', methods=['POST'])
def settings_update_sync():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        sync_enabled = 1 if request.form.get('sync_enabled') == 'true' or request.form.get('sync_enabled') == 'on' else 0
        
        user_id = session.get('user_id')
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if user:
                conn.execute("UPDATE users SET sync_enabled=? WHERE user_id=?", (sync_enabled, user_id))
                conn.commit()
        except sqlite3.Error as se:
            conn.rollback()
            app.logger.error(f"Update sync settings database error: {se}")
            return redirect(url_for('settings', error="Database error. Failed to update sync."))
        finally:
            conn.close()
            
        status_str = "enabled" if sync_enabled == 1 else "disabled"
        return redirect(url_for('settings', success=f"Online sync settings saved. Profile sync is now {status_str}."))
    except Exception as e:
        app.logger.error(f"Update sync error: {e}")
        return redirect(url_for('settings', error=f"An error occurred: {str(e)}"))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if not user:
                return redirect(url_for('onboarding'))
        except sqlite3.Error as se:
            app.logger.error(f"Profile route database read error: {se}")
            flash("Database read error.", "error")
            return redirect(url_for('dashboard'))
        finally:
            if request.method != 'POST':
                conn.close()
                
        success = request.args.get('success')
        error = request.args.get('error')
        
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                if not name:
                    return redirect(url_for('profile', error='Name cannot be empty.'))
                    
                # Handle profile picture upload
                profile_pic_path = user['profile_pic']
                if 'profile_pic' in request.files:
                    file = request.files['profile_pic']
                    if file and file.filename != '':
                        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        from werkzeug.utils import secure_filename
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(upload_folder, filename)
                        file.save(file_path)
                        profile_pic_path = f"/static/uploads/{filename}"
                        
                # Update user
                conn.execute("UPDATE users SET name = ?, profile_pic = ? WHERE user_id = ?", (name, profile_pic_path, user_id))
                conn.commit()
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Profile update database error: {se}")
                return redirect(url_for('profile', error="Database error occurred. Failed to save profile."))
            finally:
                conn.close()
                
            return redirect(url_for('profile', success='Profile updated successfully.'))
            
        return render_template(
            'profile.html',
            username=profile['username'],
            user_role=profile['user_role'],
            current_name=user['name'],
            current_username=user['username'],
            profile_pic=user['profile_pic'],
            success=success,
            error=error,
            active_page='profile'
        )
    except Exception as e:
        app.logger.error(f"Profile route error: {e}")
        flash("An error occurred loading profile.", "error")
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        try:
            # 1. Calculate Summary Cards Values
            # Total Income
            inc_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='income' AND user_id = ?", (user_id,)).fetchone()
            income_val = inc_row[0] if inc_row[0] is not None else 0.0
            
            # Total Expenses
            exp_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND user_id = ?", (user_id,)).fetchone()
            expense_val = exp_row[0] if exp_row[0] is not None else 0.0
            
            # Savings Progress (total saved across goals)
            sav_row = conn.execute("SELECT SUM(saved_amount) FROM goals WHERE user_id = ?", (user_id,)).fetchone()
            savings_val = sav_row[0] if sav_row[0] is not None else 0.0
            
            # Upcoming EMIs Monthly Total
            emi_row = conn.execute("SELECT SUM(amount) FROM emis WHERE user_id = ?", (user_id,)).fetchone()
            emi_val = emi_row[0] if emi_row[0] is not None else 0.0
            
            # 2. Calculate Weekly Spending (Expenses this month)
            month_expenses = conn.execute("""
                SELECT amount, date FROM transactions 
                WHERE type='expense' AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now') AND user_id = ?
            """, (user_id,)).fetchall()
            
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
            upcoming_emis = conn.execute("SELECT name, amount FROM emis WHERE user_id = ? LIMIT 2", (user_id,)).fetchall()
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
                
            # 4. Generate AI Insight dynamically
            ai_insight = "You're doing great! Keep tracking your transactions to build healthy financial habits."
            if expense_val > income_val and income_val > 0:
                ai_insight = "Alert: Your spending has exceeded your income this month. Consider cutting down on non-essential categories."
            else:
                # Check if food budget is close to max
                food_spent_row = conn.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND category='food' AND user_id = ?", (user_id,)).fetchone()
                food_spent = food_spent_row[0] if food_spent_row[0] else 0.0
                if food_spent > 2500:
                    ai_insight = f"AI Insight: Your Dining & Food spending is high (₹{format_currency(food_spent)}). Cooking at home twice next week will save you roughly <strong class='text-primary dark:text-primary-fixed font-bold'>₹800</strong>!"
        except sqlite3.Error as se:
            app.logger.error(f"Dashboard SQL error: {se}")
            flash("Database error occurred while fetching dashboard data.", "error")
            income_val = expense_val = savings_val = emi_val = 0.0
            spending_weekly = [10] * 5
            bills = []
            ai_insight = "Offline mode: Failed to load data."
        finally:
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
    except Exception as e:
        app.logger.error(f"Dashboard rendering error: {e}")
        return "An unexpected error occurred. Please reload the page."

@app.route('/add-transaction')
def add_transaction():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
        profile = get_user_profile()
        return render_template('add_transaction.html', username=profile['username'], user_role=profile['user_role'])
    except Exception as e:
        app.logger.error(f"Add transaction page error: {e}")
        flash("Failed to load page.", "error")
        return redirect(url_for('dashboard'))

@app.route('/transaction/add', methods=['POST'])
def transaction_add():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        tx_type = request.form.get('type', 'expense')
        try:
            amount = float(request.form.get('amount', 0.0))
        except ValueError:
            flash("Invalid amount format. Transaction not added.", "error")
            return redirect(url_for('dashboard'))
            
        category = request.form.get('category', 'other')
        date = request.form.get('date')
        note = request.form.get('note', '')
        recurring = 1 if request.form.get('recurring') == 'true' else 0
        
        if amount > 0:
            conn = get_db_connection()
            try:
                conn.execute(
                    "INSERT INTO transactions (user_id, type, amount, category, date, note, recurring) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, tx_type, amount, category, date, note, recurring)
                )
                conn.commit()
                flash("Transaction added successfully.", "success")
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Transaction add DB error: {se}")
                flash("Database error. Failed to add transaction.", "error")
            finally:
                conn.close()
                
        return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Transaction add error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/transactions')
def transactions():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        selected_type = request.args.get('type', 'all')
        selected_category = request.args.get('category', 'all')
        
        conn = get_db_connection()
        tx_list = []
        try:
            query = "SELECT * FROM transactions WHERE user_id = ?"
            params = [user_id]
            
            if selected_type != 'all':
                query += " AND type=?"
                params.append(selected_type)
                
            if selected_category != 'all':
                query += " AND category=?"
                params.append(selected_category)
                
            query += " ORDER BY date DESC, id DESC"
            
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                tx_list.append({
                    'id': row['id'],
                    'type': row['type'],
                    'amount': row['amount'],
                    'amount_formatted': format_currency(row['amount']),
                    'category': row['category'],
                    'date': row['date'],
                    'note': row['note'],
                    'recurring': row['recurring'],
                    'icon': get_category_icon(row['category'])
                })
        except sqlite3.Error as se:
            app.logger.error(f"Fetch transactions database error: {se}")
            flash("Database error. Failed to load transactions.", "error")
        finally:
            conn.close()
            
        return render_template(
            'transactions.html',
            username=profile['username'],
            user_role=profile['user_role'],
            transactions=tx_list,
            selected_type=selected_type,
            selected_category=selected_category
        )
    except Exception as e:
        app.logger.error(f"Transactions view error: {e}")
        flash("Failed to display transactions.", "error")
        return redirect(url_for('dashboard'))

@app.route('/transaction/delete/<int:tx_id>', methods=['POST'])
def transaction_delete(tx_id):
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (tx_id, user_id))
            conn.commit()
            flash("Transaction deleted successfully.", "success")
        except sqlite3.Error as se:
            conn.rollback()
            app.logger.error(f"Delete transaction DB error: {se}")
            flash("Database error. Failed to delete transaction.", "error")
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"Transaction delete error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        
    return redirect(url_for('transactions'))

@app.route('/transaction/edit/<int:tx_id>', methods=['GET', 'POST'])
def transaction_edit(tx_id):
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        
        if request.method == 'POST':
            try:
                tx_type = request.form.get('type', 'expense')
                try:
                    amount = float(request.form.get('amount', 0.0))
                except ValueError:
                    flash("Invalid amount format. Transaction not updated.", "error")
                    return redirect(url_for('transactions'))
                    
                category = request.form.get('category', 'other')
                date = request.form.get('date')
                note = request.form.get('note', '')
                recurring = 1 if request.form.get('recurring') == 'true' else 0
                
                if amount > 0:
                    conn = get_db_connection()
                    try:
                        conn.execute("""
                            UPDATE transactions 
                            SET type=?, amount=?, category=?, date=?, note=?, recurring=? 
                            WHERE id=? AND user_id=?
                        """, (tx_type, amount, category, date, note, recurring, tx_id, user_id))
                        conn.commit()
                        flash("Transaction updated successfully.", "success")
                    except sqlite3.Error as se:
                        conn.rollback()
                        app.logger.error(f"Edit transaction DB write error: {se}")
                        flash("Database error. Failed to update transaction.", "error")
                    finally:
                        conn.close()
            except Exception as e:
                app.logger.error(f"Edit transaction POST error: {e}")
                flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('transactions'))
            
        conn = get_db_connection()
        row = None
        try:
            row = conn.execute("SELECT * FROM transactions WHERE id=? AND user_id=?", (tx_id, user_id)).fetchone()
        except sqlite3.Error as se:
            app.logger.error(f"Edit transaction DB read error: {se}")
            flash("Database error. Failed to read transaction details.", "error")
        finally:
            conn.close()
            
        if not row:
            return redirect(url_for('transactions'))
            
        tx = {
            'id': row['id'],
            'type': row['type'],
            'amount': row['amount'],
            'category': row['category'],
            'date': row['date'],
            'note': row['note'],
            'recurring': row['recurring']
        }
        
        return render_template(
            'edit_transaction.html',
            username=profile['username'],
            user_role=profile['user_role'],
            tx=tx
        )
    except Exception as e:
        app.logger.error(f"Transaction edit view error: {e}")
        flash("Failed to load edit page.", "error")
        return redirect(url_for('transactions'))

@app.route('/ai-analysis')
def ai_analysis():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        
        income_val = 0.0
        expense_val = 0.0
        category_totals = {}
        tx_rows = []
        try:
            tx_rows = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
            for row in tx_rows:
                amount = row['amount']
                if row['type'] == 'income':
                    income_val += amount
                else:
                    expense_val += amount
                    cat = row['category']
                    category_totals[cat] = category_totals.get(cat, 0.0) + amount
        except sqlite3.Error as se:
            app.logger.error(f"AI analysis DB fetch error: {se}")
            flash("Database error occurred while fetching transactions.", "error")
        finally:
            conn.close()
            
        savings_val = max(0.0, income_val - expense_val)
        savings_rate = int((savings_val / income_val * 100)) if income_val > 0 else 0
        
        api_key = os.environ.get('GEMINI_API_KEY')
        is_real_ai = False
        
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_cat_str = ""
        if top_categories:
            top_cat_str = f"Your highest expense category is **{top_categories[0][0].title()}** (₹{format_currency(top_categories[0][1])})."
        else:
            top_cat_str = "You haven't recorded any expenses yet."
            
        persona = profile['persona']
        
        if persona == 'student':
            persona_tip = "As a Student, tracking allowances is key. Allocate 10% of your allowance to savings first before spending, and watch out for minor social outing expenses."
            persona_icon = "school"
            persona_title = "Student Allowance Tip"
        elif persona == 'gig_worker':
            persona_tip = "As a Gig Worker, your income is variable. Aim to build an emergency fund of at least 3 months of fixed costs to smooth out low-income periods."
            persona_icon = "two_wheeler"
            persona_title = "Variable Income Tip"
        else:
            persona_tip = "As a Retired / Elderly user, securing fixed monthly savings and tracking medical costs is crucial. Focus on keeping grocery and pharmacy expenses predictable."
            persona_icon = "health_and_safety"
            persona_title = "Retired Wealth Preservation"
            
        ai_report = {
            'summary': f"For the current monthly cycle, you earned **₹{format_currency(income_val)}** and spent **₹{format_currency(expense_val)}**. This leaves you with **₹{format_currency(savings_val)}** in net savings, achieving a **{savings_rate}% savings rate**. {top_cat_str}",
            'observations': [
                f"You spent a total of ₹{format_currency(expense_val)} across your expense categories. Checking your budgets page is recommended to ensure you are within bounds.",
                f"Your active savings rate is {savings_rate}%. A healthy financial goal is to maintain a savings rate of at least 20% to achieve your financial milestones faster.",
                "You have active EMI commitments. Ensuring these are budgeted for first guarantees you avoid late fee penalties."
            ],
            'recommendations': [
                {
                    'title': persona_title,
                    'text': persona_tip,
                    'icon': persona_icon
                },
                {
                    'title': "Cut Non-Essentials",
                    'text': "Consider reducing shopping and entertainment spend by 10% next month. This simple micro-saving will free up extra funds for your active savings goals.",
                    'icon': "trending_down"
                }
            ]
        }
        
        if api_key:
            try:
                import json
                import urllib.request
                
                tx_data_for_api = []
                for row in tx_rows:
                    tx_data_for_api.append({
                        'type': row['type'],
                        'amount': row['amount'],
                        'category': row['category'],
                        'date': row['date'],
                        'note': row['note']
                    })
                    
                prompt = f"""
                You are MoneyMan AI, a friendly financial assistant. Analyze this user's transactions:
                User Name: {profile['username']}
                Profile Persona: {persona} (role: {profile['user_role']})
                Monthly Income: {income_val}
                Monthly Expenses: {expense_val}
                Savings: {savings_val} (Savings Rate: {savings_rate}%)
                Transactions list: {json.dumps(tx_data_for_api)}
                
                Provide a financial analysis in JSON format matching this EXACT structure:
                {{
                    "summary": "a short paragraphs summarizing their spending health and patterns",
                    "observations": [
                        "observation bullet point 1",
                        "observation bullet point 2",
                        "observation bullet point 3"
                    ],
                    "recommendations": [
                        {{
                            "title": "recommendation title 1",
                            "text": "details of recommendation 1",
                            "icon": "material symbol icon name (e.g. trending_down, savings, restaurant, school)"
                        }},
                        {{
                            "title": "recommendation title 2",
                            "text": "details of recommendation 2",
                            "icon": "material symbol icon name"
                        }}
                    ]
                }}
                Return ONLY the raw JSON document, no markdown formatting.
                """
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)
                    content_text = res_json['candidates'][0]['content']['parts'][0]['text']
                    parsed_report = json.loads(content_text)
                    
                    if 'summary' in parsed_report and 'observations' in parsed_report and 'recommendations' in parsed_report:
                        ai_report = parsed_report
                        is_real_ai = True
            except Exception as e:
                ai_report['observations'].append(f"AI API request failed: {str(e)}. Using local offline insights.")
                
        return render_template(
            'ai_analysis.html',
            username=profile['username'],
            user_role=profile['user_role'],
            income_formatted=format_currency(income_val),
            expense_formatted=format_currency(expense_val),
            savings_rate=savings_rate,
            is_real_ai=is_real_ai,
            ai_report=ai_report
        )
    except Exception as e:
        app.logger.error(f"AI analysis page rendering error: {e}")
        flash("An error occurred loading AI analysis.", "error")
        return redirect(url_for('dashboard'))

@app.route('/budgets')
def budgets():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        active_budgets = []
        try:
            db_budgets = conn.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,)).fetchall()
            
            for budget in db_budgets:
                cat = budget['category']
                limit_val = budget['limit_amount']
                
                spent_row = conn.execute("""
                    SELECT SUM(amount) FROM transactions 
                    WHERE type='expense' AND category=? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now') AND user_id = ?
                """, (cat, user_id)).fetchone()
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
        except sqlite3.Error as se:
            app.logger.error(f"Budgets DB fetch error: {se}")
            flash("Database error. Failed to load budgets.", "error")
        finally:
            conn.close()
            
        return render_template('budgets.html', username=profile['username'], user_role=profile['user_role'], active_budgets=active_budgets)
    except Exception as e:
        app.logger.error(f"Budgets view error: {e}")
        flash("An error occurred loading budgets page.", "error")
        return redirect(url_for('dashboard'))

@app.route('/budgets/create', methods=['POST'])
def budgets_create():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        category = request.form.get('category', 'other').lower()
        try:
            limit = float(request.form.get('limit', 0.0))
        except ValueError:
            flash("Invalid limit format. Budget not set.", "error")
            return redirect(url_for('budgets'))
            
        alert_threshold = 80 if request.form.get('alert_80') else 0
        
        if limit > 0:
            conn = get_db_connection()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO budgets (user_id, category, limit_amount, alert_threshold)
                    VALUES (?, ?, ?, ?)
                """, (user_id, category, limit, alert_threshold))
                conn.commit()
                flash("Budget saved successfully.", "success")
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Budgets create DB error: {se}")
                flash("Database error. Failed to save budget.", "error")
            finally:
                conn.close()
                
        return redirect(url_for('budgets'))
    except Exception as e:
        app.logger.error(f"Budgets create error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('budgets'))

@app.route('/emi')
def emi():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        emis = []
        try:
            db_emis = conn.execute("SELECT * FROM emis WHERE user_id = ?", (user_id,)).fetchall()
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
        except sqlite3.Error as se:
            app.logger.error(f"EMI DB fetch error: {se}")
            flash("Database error. Failed to load EMIs.", "error")
        finally:
            conn.close()
            
        return render_template('emi.html', username=profile['username'], user_role=profile['user_role'], emis=emis)
    except Exception as e:
        app.logger.error(f"EMI view error: {e}")
        flash("An error occurred loading EMI page.", "error")
        return redirect(url_for('dashboard'))

@app.route('/emi/create', methods=['POST'])
def emi_create():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        name = request.form.get('name', 'Personal Loan')
        bank = request.form.get('bank', 'General Bank')
        try:
            amount = float(request.form.get('amount', 0.0))
            total_months = int(request.form.get('total_months', 12))
        except ValueError:
            flash("Invalid numeric format. EMI tracker not created.", "error")
            return redirect(url_for('emi'))
            
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
            try:
                conn.execute("""
                    INSERT INTO emis (user_id, name, bank, amount, remaining_months, total_months, icon, color)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, bank, amount, total_months, total_months, icon, color))
                conn.commit()
                flash("EMI tracker created successfully.", "success")
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"EMI create DB error: {se}")
                flash("Database error. Failed to save EMI.", "error")
            finally:
                conn.close()
                
        return redirect(url_for('emi'))
    except Exception as e:
        app.logger.error(f"EMI create error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('emi'))

@app.route('/goals')
def goals():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        profile = get_user_profile()
        conn = get_db_connection()
        active_goals = []
        try:
            db_goals = conn.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,)).fetchall()
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
        except sqlite3.Error as se:
            app.logger.error(f"Goals DB fetch error: {se}")
            flash("Database error. Failed to load goals.", "error")
        finally:
            conn.close()
            
        return render_template('goals.html', username=profile['username'], user_role=profile['user_role'], active_goals=active_goals)
    except Exception as e:
        app.logger.error(f"Goals view error: {e}")
        flash("An error occurred loading goals.", "error")
        return redirect(url_for('dashboard'))

@app.route('/goals/create', methods=['POST'])
def goals_create():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        name = request.form.get('name')
        try:
            target = float(request.form.get('target', 0.0))
        except ValueError:
            flash("Invalid target format. Goal not created.", "error")
            return redirect(url_for('goals'))
            
        tag = request.form.get('tag', 'Other')
        target_date = request.form.get('target_date', '')
        
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
            try:
                conn.execute("""
                    INSERT INTO goals (user_id, name, tag, saved_amount, target_amount, target_date, icon, icon_bg, bg_decor)
                    VALUES (?, ?, ?, 0.0, ?, ?, ?, ?, ?)
                """, (user_id, name, tag, target, target_date, icon, icon_bg, bg_decor))
                conn.commit()
                flash("Savings goal created successfully.", "success")
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Goal create DB error: {se}")
                flash("Database error. Failed to save savings goal.", "error")
            finally:
                conn.close()
                
        return redirect(url_for('goals'))
    except Exception as e:
        app.logger.error(f"Goals create error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('goals'))

@app.route('/goals/update', methods=['POST'])
def goals_update():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
            
        user_id = session.get('user_id')
        try:
            goal_id = int(request.form.get('goal_id', 0))
            saved_amount = float(request.form.get('saved_amount', 0.0))
        except ValueError:
            flash("Invalid amount format. Savings not updated.", "error")
            return redirect(url_for('goals'))
            
        if goal_id > 0:
            conn = get_db_connection()
            try:
                conn.execute("UPDATE goals SET saved_amount=? WHERE id=? AND user_id=?", (saved_amount, goal_id, user_id))
                conn.commit()
                flash("Savings progress updated successfully.", "success")
            except sqlite3.Error as se:
                conn.rollback()
                app.logger.error(f"Goal update DB error: {se}")
                flash("Database error. Failed to update savings.", "error")
            finally:
                conn.close()
                
        return redirect(url_for('goals'))
    except Exception as e:
        app.logger.error(f"Goals update error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('goals'))

@app.route('/learn')
def learn():
    try:
        if not is_user_onboarded():
            return redirect(url_for('onboarding'))
        profile = get_user_profile()
        return render_template('learn.html', username=profile['username'], user_role=profile['user_role'])
    except Exception as e:
        app.logger.error(f"Learn page error: {e}")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print("Starting MoneyMan Web Server on Localhost...")
    print(f"Open http://127.0.0.1:{port}/ to view the app.")
    app.run(debug=True, port=port)
