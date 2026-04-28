import sqlite3
from datetime import datetime, timedelta
import json

DATABASE = 'energy_tracker.db'

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # User profiles table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE,
        family_size TEXT,
        property_type TEXT,
        bill_goal INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Daily usage history table
    c.execute('''CREATE TABLE IF NOT EXISTS daily_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        units REAL,
        bill REAL,
        appliance_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Bills history table
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        month TEXT,
        total_units REAL,
        total_bill REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        target_bill_reduction INTEGER,
        target_date TEXT,
        progress REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def get_or_create_user(user_name="default_user"):
    """Get user or create if doesn't exist"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('SELECT id FROM users WHERE user_name = ?', (user_name,))
    row = c.fetchone()
    
    if row:
        user_id = row[0]
    else:
        c.execute('''INSERT INTO users (user_name) VALUES (?)''', (user_name,))
        user_id = c.lastrowid
        conn.commit()
    
    conn.close()
    return user_id

def save_daily_usage(user_id, units, bill, appliance_data):
    """Save daily usage record"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''INSERT INTO daily_usage (user_id, date, units, bill, appliance_data)
                 VALUES (?, ?, ?, ?, ?)''', 
             (user_id, today, units, bill, json.dumps(appliance_data)))
    conn.commit()
    conn.close()

def get_today_usage(user_id):
    """Get today's usage"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''SELECT units, bill FROM daily_usage WHERE user_id = ? AND date = ?''',
             (user_id, today))
    row = c.fetchone()
    conn.close()
    
    return row or (0, 0)

def get_weekly_usage(user_id):
    """Get usage for last 7 days"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    c.execute('''SELECT date, units, bill FROM daily_usage 
                 WHERE user_id = ? AND date BETWEEN ? AND ?
                 ORDER BY date''',
             (user_id, start_str, end_str))
    rows = c.fetchall()
    conn.close()
    
    return rows

def get_monthly_usage(user_id):
    """Get usage for current month"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    now = datetime.now()
    month_start = now.replace(day=1).strftime('%Y-%m-%d')
    month_end = now.strftime('%Y-%m-%d')
    
    c.execute('''SELECT SUM(units), SUM(bill) FROM daily_usage 
                 WHERE user_id = ? AND date BETWEEN ? AND ?''',
             (user_id, month_start, month_end))
    row = c.fetchone()
    conn.close()
    
    return (row[0] or 0, row[1] or 0) if row else (0, 0)

def get_last_month_comparison(user_id):
    """Compare this month to last month"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    now = datetime.now()
    this_month_start = now.replace(day=1).strftime('%Y-%m-%d')
    this_month_end = now.strftime('%Y-%m-%d')
    
    last_month_end = now.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1).strftime('%Y-%m-%d')
    last_month_end = last_month_end.strftime('%Y-%m-%d')
    
    # This month
    c.execute('''SELECT SUM(bill) FROM daily_usage WHERE user_id = ? AND date BETWEEN ? AND ?''',
             (user_id, this_month_start, this_month_end))
    this_bill = c.fetchone()[0] or 0
    
    # Last month
    c.execute('''SELECT SUM(bill) FROM daily_usage WHERE user_id = ? AND date BETWEEN ? AND ?''',
             (user_id, last_month_start, last_month_end))
    last_bill = c.fetchone()[0] or 0
    
    conn.close()
    
    if last_bill == 0:
        percent_change = 0
    else:
        percent_change = round(((this_bill - last_bill) / last_bill) * 100, 1)
    
    return {'this_month': this_bill, 'last_month': last_bill, 'percent_change': percent_change}

def update_user_profile(user_id, family_size, property_type):
    """Update user profile"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''UPDATE users SET family_size = ?, property_type = ? WHERE id = ?''',
             (family_size, property_type, user_id))
    conn.commit()
    conn.close()

def set_bill_goal(user_id, goal_amount):
    """Set bill reduction goal"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''INSERT INTO goals (user_id, target_bill_reduction) VALUES (?, ?)''',
             (user_id, goal_amount))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    """Get user profile data"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('SELECT user_name, family_size, property_type, bill_goal FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'name': row[0],
            'family_size': row[1],
            'property_type': row[2],
            'bill_goal': row[3]
        }
    return None
