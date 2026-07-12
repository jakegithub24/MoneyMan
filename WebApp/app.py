import os
from flask import Flask, render_template

app = Flask(__name__)

# Basic routing for all pages
@app.route('/')
def index():
    # Redirect to onboarding or dashboard
    return render_template('onboarding.html')

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    return render_template('onboarding.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username="Ramesh Kumar", user_role="Retired Profile")

@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    return render_template('add_transaction.html')

@app.route('/budgets')
def budgets():
    return render_template('budgets.html')

@app.route('/emi')
def emi():
    return render_template('emi.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

if __name__ == '__main__':
    print("Starting MoneyMan Web UI Server...")
    print("Open http://127.0.0.1:5000/ in your browser.")
    app.run(debug=True, port=5000)
