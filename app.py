
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import os
import sqlite3
import re
import pickle

model_path = os.path.join(os.getcwd(), "model.pkl")
model = pickle.load(open(model_path, "rb"))

# 🟢 DATABASE CONNECTION
import os

def get_db():
    db_path = os.path.join(os.getcwd(), "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 🟢 CREATE TABLES
def create_tables():
    conn = get_db()

    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        result TEXT,
                        score TEXT,
                        date TEXT
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        message TEXT,
                        date TEXT
                    )''')

    conn.commit()
    conn.close()


# 🟢 RUN TABLE CREATE
create_tables()

# 🔍 URL CHECK
def check_url(url):
    url = url.lower()

    if not url.startswith("http"):
        return "Phishing"

    if "login" in url or "verify" in url:
        return "Suspicious"

    if "go0gle" in url or "paypa1" in url:
        return "Phishing"

    if re.search(r'\d', url):
        return "Suspicious"

    if "https" in url:
        return "Safe"

    return "Phishing"


# 🔐 LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session['user'] = username
            return redirect('/')

        return "Invalid Login"

    return render_template('login.html')


# 📝 REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?,?)",
                         (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect('/login')

    return render_template('register.html')


# 🏠 HOME
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')


# 🔍 CHECK URL
@app.route('/check', methods=['POST'])
def check():
    if 'user' not in session:
        return redirect('/login')

    url = request.form['url']
    result = check_url(url)

    score = "20%" if result=="Safe" else "60%" if result=="Suspicious" else "90%"

    conn = get_db()
    conn.execute("INSERT INTO history (url,result,score,date) VALUES (?,?,?,?)",
                 (url, result, score, datetime.now().strftime("%d-%m-%Y %H:%M")))
    conn.commit()
    conn.close()

    return render_template('result.html', url=url, result=result, score=score)


# 📜 HISTORY
@app.route('/history')
def history_page():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    data = conn.execute("SELECT * FROM history").fetchall()
    conn.close()

    return render_template('history.html', history=data)


# 📩 CONTACT
@app.route('/contact', methods=['GET','POST'])
def contact():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db()
        conn.execute("INSERT INTO messages (name,email,message,date) VALUES (?,?,?,?)",
                     (name, email, message, datetime.now().strftime("%d-%m-%Y %H:%M")))
        conn.commit()
        conn.close()

        return render_template('contact.html', success=True)

    return render_template('contact.html', success=False)


# 📩 MESSAGES
@app.route('/messages')
def messages_page():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    data = conn.execute("SELECT * FROM messages").fetchall()
    conn.close()

    return render_template('messages.html', messages=data)


# 💡 TIPS
@app.route('/tips')
def tips():
    return render_template('tips.html')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# 🚀 RUN
if __name__ == '__main__':
    app.run()
