import sqlite3
import os
import hashlib
import uuid
from argon2 import PasswordHasher

DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moneyman.db'))

def hash_pin(pin):
    ph = PasswordHasher()
    return ph.hash(pin)

def verify_pin(pin, stored_val):
    ph = PasswordHasher()
    try:
        # argon2 verification succeeds if no exception is raised
        ph.verify(stored_val, pin)
        return True
    except Exception:
        # Fallback to legacy salted sha256 to avoid breaking existing users or unit tests
        try:
            salt, hashed = stored_val.split(':')
            return hashlib.sha256(salt.encode() + pin.encode()).hexdigest() == hashed
        except Exception:
            return False

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            persona TEXT NOT NULL,
            pin TEXT NOT NULL,
            is_onboarded INTEGER DEFAULT 0,
            sync_enabled INTEGER DEFAULT 0
        )
    ''')
    
    # Safe migration for existing DBs
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN sync_enabled INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # Create Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            category TEXT UNIQUE NOT NULL,
            limit_amount REAL NOT NULL,
            alert_threshold INTEGER DEFAULT 80
        )
    ''')
    
    # Create EMIs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    
    # Check if we need to seed the data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
        
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    
    # Seed User (Default is not onboarded, so they go through onboarding, but seeded for convenience)
    # We can seed an onboarded profile as our default seed
    cursor.execute('''
        INSERT INTO users (username, persona, pin, is_onboarded)
        VALUES ('Ramesh Kumar', 'retired', ?, 1)
    ''', (hash_pin('1234'),))
    
    # Seed Transactions (Expense / Income)
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, date, note, recurring)
        VALUES 
        ('income', 15000.0, 'salary', '2026-07-01', 'Monthly pension credit', 1),
        ('expense', 3000.0, 'food', '2026-07-10', 'Groceries and vegetables', 0),
        ('expense', 1800.0, 'transport', '2026-07-11', 'Auto and cab fares', 0),
        ('expense', 1200.0, 'shopping', '2026-07-12', 'Medicines & pharmacy', 0),
        ('expense', 2200.0, 'other', '2026-07-05', 'Electricity bill pay', 1)
    ''')
    
    # Seed Budgets
    cursor.execute('''
        INSERT INTO budgets (category, limit_amount, alert_threshold)
        VALUES 
        ('food', 4000.0, 80),
        ('transport', 2000.0, 80),
        ('shopping', 1000.0, 80)
    ''')
    
    # Seed EMIs
    cursor.execute('''
        INSERT INTO emis (name, bank, amount, remaining_months, total_months, icon, color)
        VALUES 
        ('Home Loan', 'SBI Bank', 24500.0, 120, 180, 'home', 'bg-tertiary-container'),
        ('Phone EMI', 'HDFC Credit Card', 4200.0, 4, 24, 'smartphone', 'bg-primary')
    ''')
    
    # Seed Goals
    cursor.execute('''
        INSERT INTO goals (name, tag, saved_amount, target_amount, target_date, icon, icon_bg, bg_decor)
        VALUES 
        ('Emergency Fund', 'Safety Net', 5000.0, 10000.0, '2026-12-31', 'health_and_safety', 'bg-income-green-subtle text-primary dark:bg-primary/20 dark:text-primary-fixed', 'bg-income-green-subtle dark:bg-primary/10'),
        ('New Laptop', 'Tech', 15000.0, 45000.0, '2026-10-31', 'laptop_mac', 'bg-surface-container-high text-tertiary dark:bg-tertiary/20 dark:text-tertiary-fixed-dim', 'bg-secondary-fixed-dim dark:bg-secondary/10')
    ''')
    
    conn.commit()

if __name__ == '__main__':
    print("Initializing Database...")
    init_db()
    print("Database Initialized at:", DATABASE_PATH)
