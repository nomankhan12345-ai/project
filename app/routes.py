from flask import render_template, flash, redirect, url_for, request 
from app import app, db, bcrypt, login_manager
from app.models import User, Transaction
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login.html'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    amount = int(request.form['amount'])
    receiver_username = request.form['receiver_username']
    receiver = User.query.filter_by(username=receiver_username).first()

    if not receiver:
        flash('User not found.', 'danger')
        return redirect(url_for('dashboard'))

    if current_user.ogcoin_balance < amount:
        flash('Insufficient OGCOIN balance.', 'danger')
        return redirect(url_for('dashboard'))

    current_user.ogcoin_balance -= amount
    receiver.ogcoin_balance += amount

    transaction = Transaction(sender_id=current_user.id, receiver_username=receiver.username, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    flash(f'Transferred {amount} OGCOIN to {receiver.username}.', 'success')
    return redirect(url_for('dashboard'))
