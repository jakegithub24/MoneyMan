import sqlite3
import os
import hashlib
import uuid
from argon2 import PasswordHasher

DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moneyman.db'))

def hash_pin(pin):
    try:
        ph = PasswordHasher()
        return ph.hash(pin)
    except Exception as e:
        # Fallback to simple hash in case of error (e.g. system resource exhaustion or format)
        salt = os.urandom(16).hex()
        hashed = hashlib.sha256(salt.encode() + pin.encode()).hexdigest()
        return f"{salt}:{hashed}"

def verify_pin(pin, stored_val):
    try:
        ph = PasswordHasher()
        try:
            ph.verify(stored_val, pin)
            return True
        except Exception:
            # Fallback to legacy salted sha256 to avoid breaking existing users or unit tests
            salt, hashed = stored_val.split(':')
            return hashlib.sha256(salt.encode() + pin.encode()).hexdigest() == hashed
    except Exception:
        return False

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Safe migration: drop users table if it lacks user_id or is_logged_out
        try:
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if columns and ('user_id' not in columns or 'is_logged_out' not in columns):
                cursor.execute("DROP TABLE IF EXISTS users")
        except Exception:
            pass
            
        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL DEFAULT 'MoneyMan User',
                username TEXT NOT NULL,
                persona TEXT NOT NULL,
                pin TEXT NOT NULL,
                password TEXT,
                profile_pic TEXT,
                is_onboarded INTEGER DEFAULT 0,
                sync_enabled INTEGER DEFAULT 0,
                is_logged_out INTEGER DEFAULT 0
            )
        ''')
        
        # Safe migration: drop tables if they don't have user_id
        for table in ['transactions', 'budgets', 'emis', 'goals']:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                if columns and 'user_id' not in columns:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except Exception:
                pass

        # Create Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                note TEXT,
                recurring INTEGER DEFAULT 0
            )
        ''')
        
        # Create Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                alert_threshold INTEGER DEFAULT 80,
                UNIQUE(user_id, category)
            )
        ''')
        
        # Create EMIs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                bank TEXT NOT NULL,
                amount REAL NOT NULL,
                remaining_months INTEGER NOT NULL,
                total_months INTEGER NOT NULL,
                icon TEXT DEFAULT 'calculate',
                color TEXT DEFAULT 'bg-primary'
            )
        ''')
        
        # Create Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                tag TEXT NOT NULL,
                saved_amount REAL NOT NULL,
                target_amount REAL NOT NULL,
                target_date TEXT,
                icon TEXT DEFAULT 'flag',
                icon_bg TEXT,
                bg_decor TEXT
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def seed_data(conn):
    try:
        cursor = conn.cursor()
        
        # Clear any old data
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM budgets")
        cursor.execute("DELETE FROM emis")
        cursor.execute("DELETE FROM goals")
        
        # Seed User (Default is not onboarded, so they go through onboarding, but seeded for convenience)
        cursor.execute('''
            INSERT INTO users (user_id, name, username, persona, pin, password, profile_pic, is_onboarded)
            VALUES ('1', 'Ramesh Kumar', 'ramesh123', 'retired', ?, NULL, NULL, 1)
        ''', (hash_pin('1234'),))
        
        user_id = '1'

        # Seed Transactions (Expense / Income)
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, category, date, note, recurring)
            VALUES 
            (?, 'income', 15000.0, 'salary', '2026-07-01', 'Monthly pension credit', 1),
            (?, 'expense', 3000.0, 'food', '2026-07-10', 'Groceries and vegetables', 0),
            (?, 'expense', 1800.0, 'transport', '2026-07-11', 'Auto and cab fares', 0),
            (?, 'expense', 1200.0, 'shopping', '2026-07-12', 'Medicines & pharmacy', 0),
            (?, 'expense', 2200.0, 'other', '2026-07-05', 'Electricity bill pay', 1)
        ''', (user_id, user_id, user_id, user_id, user_id))
        
        # Seed Budgets
        cursor.execute('''
            INSERT INTO budgets (user_id, category, limit_amount, alert_threshold)
            VALUES 
            (?, 'food', 4000.0, 80),
            (?, 'transport', 2000.0, 80),
            (?, 'shopping', 1000.0, 80)
        ''', (user_id, user_id, user_id))
        
        # Seed EMIs
        cursor.execute('''
            INSERT INTO emis (user_id, name, bank, amount, remaining_months, total_months, icon, color)
            VALUES 
            (?, 'Home Loan', 'SBI Bank', 24500.0, 120, 180, 'home', 'bg-tertiary-container'),
            (?, 'Phone EMI', 'HDFC Credit Card', 4200.0, 4, 24, 'smartphone', 'bg-primary')
        ''', (user_id, user_id))
        
        # Seed Goals
        cursor.execute('''
            INSERT INTO goals (user_id, name, tag, saved_amount, target_amount, target_date, icon, icon_bg, bg_decor)
            VALUES 
            (?, 'Emergency Fund', 'Safety Net', 5000.0, 10000.0, '2026-12-31', 'health_and_safety', 'bg-income-green-subtle text-primary dark:bg-primary/20 dark:text-primary-fixed', 'bg-income-green-subtle dark:bg-primary/10'),
            (?, 'New Laptop', 'Tech', 15000.0, 45000.0, '2026-10-31', 'laptop_mac', 'bg-surface-container-high text-tertiary dark:bg-tertiary/20 dark:text-tertiary-fixed-dim', 'bg-secondary-fixed-dim dark:bg-secondary/10')
        ''', (user_id, user_id))
        
        conn.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.rollback()
        raise

if __name__ == '__main__':
    try:
        print("Initializing Database...")
        init_db()
        print("Database Initialized at:", DATABASE_PATH)
    except Exception as e:
        print(f"Failed to initialize database: {e}")
