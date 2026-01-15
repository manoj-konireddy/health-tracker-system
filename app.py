from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database initialization
DATABASE = 'health_tracker.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DATABASE):
        db = get_db()
        cursor = db.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Workouts table
        cursor.execute('''
            CREATE TABLE workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workout_type TEXT NOT NULL,
                minutes INTEGER NOT NULL,
                calories_burned INTEGER,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Nutrition logs table
        cursor.execute('''
            CREATE TABLE nutrition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein REAL,
                carbs REAL,
                fat REAL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Reminders table
        cursor.execute('''
            CREATE TABLE reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reminder_type TEXT NOT NULL,
                message TEXT NOT NULL,
                scheduled_time TIME,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        db.commit()
        db.close()
        print("Database initialized successfully!")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password, age, gender)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, generate_password_hash(password), age, gender))
            db.commit()
            db.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username or email already exists')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    
    # Get user info
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get today's workouts
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM workouts WHERE user_id = ? AND date = ?
    ''', (session['user_id'], today))
    today_workouts = cursor.fetchall()
    
    # Get today's nutrition
    cursor.execute('''
        SELECT * FROM nutrition_logs WHERE user_id = ? AND date = ?
    ''', (session['user_id'], today))
    today_nutrition = cursor.fetchall()
    
    # Calculate totals
    total_calories_burned = sum(w['calories_burned'] or 0 for w in today_workouts)
    total_calories_consumed = sum(n['calories'] for n in today_nutrition)
    total_workout_minutes = sum(w['minutes'] for w in today_workouts)
    
    db.close()
    
    return render_template('dashboard.html', user=user, 
                         today_workouts=today_workouts,
                         today_nutrition=today_nutrition,
                         total_calories_burned=total_calories_burned,
                         total_calories_consumed=total_calories_consumed,
                         total_workout_minutes=total_workout_minutes)

@app.route('/add-workout', methods=['GET', 'POST'])
@login_required
def add_workout():
    if request.method == 'POST':
        workout_type = request.form.get('workout_type')
        minutes = request.form.get('minutes')
        calories = request.form.get('calories')
        date = request.form.get('date')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO workouts (user_id, workout_type, minutes, calories_burned, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], workout_type, minutes, calories or 0, date))
        db.commit()
        db.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add-workout.html')

@app.route('/add-nutrition', methods=['GET', 'POST'])
@login_required
def add_nutrition():
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        carbs = request.form.get('carbs')
        fat = request.form.get('fat')
        date = request.form.get('date')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO nutrition_logs (user_id, food_name, calories, protein, carbs, fat, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], food_name, calories, protein or 0, carbs or 0, fat or 0, date))
        db.commit()
        db.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add-nutrition.html')

@app.route('/progress')
@login_required
def progress():
    db = get_db()
    cursor = db.cursor()
    
    # Get user info
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get workouts for the last 7 days
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT workout_type, SUM(minutes) as total_minutes, COUNT(*) as count
        FROM workouts 
        WHERE user_id = ? AND date >= ?
        GROUP BY workout_type
        ORDER BY total_minutes DESC
    ''', (session['user_id'], seven_days_ago))
    workout_data = cursor.fetchall()
    
    # Get daily totals for the last 7 days
    cursor.execute('''
        SELECT date, SUM(minutes) as total_minutes, SUM(calories_burned) as total_calories
        FROM workouts 
        WHERE user_id = ? AND date >= ?
        GROUP BY date
        ORDER BY date
    ''', (session['user_id'], seven_days_ago))
    daily_data = cursor.fetchall()
    
    # Prepare data for chart
    workout_types = [row['workout_type'] for row in workout_data]
    workout_minutes = [row['total_minutes'] for row in workout_data]
    
    daily_dates = [row['date'] for row in daily_data]
    daily_minutes = [row['total_minutes'] or 0 for row in daily_data]
    daily_calories = [row['total_calories'] or 0 for row in daily_data]
    
    db.close()
    
    return render_template('progress.html', user=user,
                         workout_types=workout_types,
                         workout_minutes=workout_minutes,
                         daily_dates=daily_dates,
                         daily_minutes=daily_minutes,
                         daily_calories=daily_calories)

@app.route('/api/workout-data')
@login_required
def workout_data():
    db = get_db()
    cursor = db.cursor()
    
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT workout_type, SUM(minutes) as total_minutes
        FROM workouts 
        WHERE user_id = ? AND date >= ?
        GROUP BY workout_type
    ''', (session['user_id'], seven_days_ago))
    
    data = cursor.fetchall()
    db.close()
    
    return jsonify({
        'types': [row['workout_type'] for row in data],
        'minutes': [row['total_minutes'] for row in data]
    })

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    db.close()
    
    return render_template('profile.html', user=user)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    age = request.form.get('age')
    height = request.form.get('height')
    weight = request.form.get('weight')
    gender = request.form.get('gender')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE users SET age = ?, height = ?, weight = ?, gender = ?
        WHERE id = ?
    ''', (age, height, weight, gender, session['user_id']))
    db.commit()
    db.close()
    
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
