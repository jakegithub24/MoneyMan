import os
import unittest
import tempfile
import sqlite3

# Set the environment variable for testing database before importing db or app
dummy_fd, dummy_path = tempfile.mkstemp()
os.environ['DATABASE_PATH'] = dummy_path
os.close(dummy_fd)

from db import init_db, get_db_connection, verify_pin
from app import app

class MoneyManTestCase(unittest.TestCase):

    def setUp(self):
        # Create a new temp file for the db
        self.db_fd, self.temp_db_path = tempfile.mkstemp()
        os.environ['DATABASE_PATH'] = self.temp_db_path
        
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Reset the database for each test
        conn = get_db_connection()
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute("DROP TABLE IF EXISTS transactions")
        conn.execute("DROP TABLE IF EXISTS budgets")
        conn.execute("DROP TABLE IF EXISTS emis")
        conn.execute("DROP TABLE IF EXISTS goals")
        conn.commit()
        conn.close()
        
        init_db()

    def tearDown(self):
        # Clear database connection and delete file
        os.close(self.db_fd)
        try:
            os.unlink(self.temp_db_path)
        except OSError:
            pass

    def test_database_initialization(self):
        """Test database table structures and default seeding."""
        conn = get_db_connection()
        
        # Verify tables exist
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t['name'] for t in tables]
        self.assertIn('users', table_names)
        self.assertIn('transactions', table_names)
        self.assertIn('budgets', table_names)
        self.assertIn('emis', table_names)
        self.assertIn('goals', table_names)
        
        # Verify seed user (Ramesh Kumar, retired)
        user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
        self.assertEqual(user['username'], 'Ramesh Kumar')
        self.assertEqual(user['persona'], 'retired')
        self.assertTrue(verify_pin('1234', user['pin']))
        self.assertEqual(user['is_onboarded'], 1)
        conn.close()

    def test_unonboarded_redirection(self):
        """Test that unonboarded user redirects to onboarding."""
        # De-onboard the seeded user first
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_onboarded = 0")
        conn.commit()
        conn.close()
        
        # Visit index
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/onboarding', response.headers['Location'])
        
        # Visit dashboard (should also redirect)
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/onboarding', response.headers['Location'])

    def test_onboarding_submission(self):
        """Test user onboarding form submission."""
        # Clear users first
        conn = get_db_connection()
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        
        # Submit onboarding
        response = self.client.post('/onboarding', data={
            'persona': 'student',
            'pin': '9876'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav Mehta', response.data) # Default student name
        
        # Verify db entry
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'Aarav Mehta')
        self.assertEqual(user['persona'], 'student')
        self.assertTrue(verify_pin('9876', user['pin']))
        self.assertEqual(user['is_onboarded'], 1)
        conn.close()

    def test_add_transaction(self):
        """Test transaction creation and listing."""
        response = self.client.post('/transaction/add', data={
            'type': 'expense',
            'amount': '450.50',
            'category': 'food',
            'date': '2026-07-13',
            'note': 'Lunch at university canteen',
            'recurring': 'false'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify transaction is in database
        conn = get_db_connection()
        tx = conn.execute("SELECT * FROM transactions WHERE category='food' AND amount=450.50").fetchone()
        self.assertIsNotNone(tx)
        self.assertEqual(tx['note'], 'Lunch at university canteen')
        self.assertEqual(tx['type'], 'expense')
        conn.close()

    def test_create_budget(self):
        """Test budget creation."""
        response = self.client.post('/budgets/create', data={
            'category': 'entertainment',
            'limit': '1500.00',
            'alert_80': 'true'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify budget is in database
        conn = get_db_connection()
        budget = conn.execute("SELECT * FROM budgets WHERE category='entertainment'").fetchone()
        self.assertIsNotNone(budget)
        self.assertEqual(budget['limit_amount'], 1500.00)
        self.assertEqual(budget['alert_threshold'], 80)
        conn.close()

    def test_savings_goals(self):
        """Test goal creation and progress update."""
        # Create Goal
        response = self.client.post('/goals/create', data={
            'name': 'Trip to Goa',
            'target': '12000.00',
            'tag': 'Travel',
            'target_date': '2026-12-31'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify goal is in DB
        conn = get_db_connection()
        goal = conn.execute("SELECT * FROM goals WHERE name='Trip to Goa'").fetchone()
        self.assertIsNotNone(goal)
        self.assertEqual(goal['target_amount'], 12000.00)
        self.assertEqual(goal['saved_amount'], 0.0)
        goal_id = goal['id']
        conn.close()
        
        # Update Goal
        response = self.client.post('/goals/update', data={
            'goal_id': str(goal_id),
            'saved_amount': '2500.00'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify updated progress
        conn = get_db_connection()
        goal = conn.execute("SELECT * FROM goals WHERE id=?", (goal_id,)).fetchone()
        self.assertEqual(goal['saved_amount'], 2500.00)
        conn.close()

    def test_emi_tracker(self):
        """Test EMI addition."""
        response = self.client.post('/emi/create', data={
            'name': 'iPad Installments',
            'bank': 'ICICI Bank',
            'amount': '3500.00',
            'total_months': '6'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify EMI in DB
        conn = get_db_connection()
        emi = conn.execute("SELECT * FROM emis WHERE name='iPad Installments'").fetchone()
        self.assertIsNotNone(emi)
        self.assertEqual(emi['bank'], 'ICICI Bank')
        self.assertEqual(emi['amount'], 3500.00)
        self.assertEqual(emi['total_months'], 6)
        self.assertEqual(emi['remaining_months'], 6)
        conn.close()

    def test_list_transactions(self):
        """Test listing transactions with type/category filters."""
        conn = get_db_connection()
        conn.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('income', 1000.0, 'other', '2026-07-01', 'Gift')")
        conn.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('expense', 200.0, 'food', '2026-07-02', 'Snack')")
        conn.commit()
        conn.close()
        
        response = self.client.get('/transactions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gift', response.data)
        self.assertIn(b'Snack', response.data)
        
        response = self.client.get('/transactions?type=income')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gift', response.data)
        self.assertNotIn(b'Snack', response.data)

    def test_edit_transaction(self):
        """Test editing an existing transaction."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('expense', 500.0, 'other', '2026-07-01', 'Old Note')")
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        response = self.client.get(f'/transaction/edit/{tx_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Old Note', response.data)
        
        response = self.client.post(f'/transaction/edit/{tx_id}', data={
            'type': 'expense',
            'amount': '600.00',
            'category': 'shopping',
            'date': '2026-07-02',
            'note': 'Updated Note',
            'recurring': 'true'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        conn = get_db_connection()
        tx = conn.execute("SELECT * FROM transactions WHERE id=?", (tx_id,)).fetchone()
        self.assertEqual(tx['amount'], 600.00)
        self.assertEqual(tx['category'], 'shopping')
        self.assertEqual(tx['note'], 'Updated Note')
        self.assertEqual(tx['recurring'], 1)
        conn.close()

    def test_delete_transaction(self):
        """Test deleting a transaction."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('expense', 100.0, 'other', '2026-07-01', 'To Delete')")
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        response = self.client.post(f'/transaction/delete/{tx_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        conn = get_db_connection()
        tx = conn.execute("SELECT * FROM transactions WHERE id=?", (tx_id,)).fetchone()
        self.assertIsNone(tx)
        conn.close()

    def test_ai_analysis_view(self):
        """Test AI analysis page rendering and fallback report generation."""
        conn = get_db_connection()
        conn.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('income', 10000.0, 'other', '2026-07-01', 'Salary')")
        conn.execute("INSERT INTO transactions (type, amount, category, date, note) VALUES ('expense', 4000.0, 'food', '2026-07-02', 'Groceries')")
        conn.commit()
        conn.close()
        
        response = self.client.get('/ai-analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Savings Rate', response.data)
        self.assertIn(b'51%', response.data)
        self.assertIn(b'Food', response.data)

if __name__ == '__main__':
    unittest.main()
