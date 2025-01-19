#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management

# Database setup
def init_db():
    conn = sqlite3.connect('xss_lab.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, title TEXT, content TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, post_id INTEGER, name TEXT, email TEXT, comment TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO users (id, username, password, role) VALUES 
        (1, 'admin', 'password', 'admin'),
        (2, 'user', 'password', 'user')''')  # Default admin and user accounts
    cursor.execute('''INSERT OR IGNORE INTO posts (id, title, content) VALUES 
        (1, 'Best Games of 2024', '2024te yılın oyunları şunlar seçildi: A, B, C. Sizin düşünceleriniz neler?'),
        (2, 'Huge Discounts on Fans!', 'PC soğutma için harika indirimler. Hangi ürünleri önerirsiniz?'),
        (3, 'New XSS Vulnerability Discovered', 'Yeni bir XSS açığı bulundu. Mitigasyon stratejileriniz neler?')''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('xss_lab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    conn.close()
    username = session.get('username')
    return render_template_string('''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Forum</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        nav { background-color: #333; color: white; padding: 10px; text-align: left; }
        nav a { color: white; margin: 0 10px; text-decoration: none; }
        nav a:hover { text-decoration: underline; }
        nav .user-info { float: right; }
        .post { border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; }
        .post h2 a { text-decoration: none; color: #333; }
        .post h2 a:hover { color: #007BFF; }
    </style>
</head>
<body>
    <nav>
        <a href='/'>Ana Sayfa</a>
        {% if username %}
            <span class='user-info'>{{ username }} | <a href='/logout'>Logout</a></span>
        {% else %}
            <a href='/login' class='user-info'>Login</a>
        {% endif %}
    </nav>
    <h1>Forum Gönderileri</h1>
    {% for post in posts %}
    <div class='post'>
        <h2><a href='/post/{{ post[0] }}'>{{ post[1] }}</a></h2>
        <p>{{ post[2] }}</p>
    </div>
    {% endfor %}
</body>
</html>
''', posts=posts, username=username)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    conn = sqlite3.connect('xss_lab.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comment = request.form['comment']
        
        # Simple input validation to prevent XSS attacks
        # Uncomment the following lines to enable input validation:
        # if '<' in name or '>' in name or '<' in comment or '>' in comment:
        #     return "Invalid input detected!", 400
        
        cursor.execute('INSERT INTO comments (post_id, name, email, comment) VALUES (?, ?, ?, ?)', (post_id, name, email, comment))
        conn.commit()

    cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()

    cursor.execute('SELECT name, email, comment FROM comments WHERE post_id = ?', (post_id,))
    comments = cursor.fetchall()
    conn.close()

    return render_template_string('''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>{{ post[1] }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        nav { background-color: #333; color: white; padding: 10px; text-align: left; }
        nav a { color: white; margin: 0 10px; text-decoration: none; }
        nav a:hover { text-decoration: underline; }
        nav .user-info { float: right; }
        .comment { border-top: 1px solid #ddd; padding-top: 5px; margin-top: 5px; font-size: 14px; }
        form input, form textarea { display: block; margin: 10px 0; width: 60%; padding: 8px; }
        form textarea { height: 150px; }
        form button { padding: 10px 20px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        form button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <nav>
        <a href='/'>Ana Sayfa</a>
        {% if username %}
            <span class='user-info'>{{ username }} | <a href='/logout'>Logout</a></span>
        {% else %}
            <a href='/login' class='user-info'>Login</a>
        {% endif %}
    </nav>
    <h1>{{ post[1] }}</h1>
    <p>{{ post[2] }}</p>

    <h2>Comments</h2>
    {% for comment in comments %}
    <div class='comment'>
        <p><strong>{{ comment[0] }}</strong> ({{ comment[1] }}): {{ comment[2]|safe }}</p>
    </div>
    {% endfor %}

    <h3>Leave a Comment</h3>
    <form method='POST'>
        <input type='text' name='name' placeholder='Name' required>
        <input type='email' name='email' placeholder='Email' required>
        <textarea name='comment' placeholder='Your comment here' required></textarea>
        <button type='submit'>Submit</button>
    </form>

</body>
</html>
''', post=post, comments=comments, username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('xss_lab.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user[3]
            return redirect(url_for('home'))
        return render_template_string('<p>Invalid credentials</p>')
    return render_template_string('''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        form { background: #f4f4f4; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        form input { display: block; margin: 10px 0; padding: 10px; width: 100%; }
        form button { padding: 10px 20px; background-color: #007BFF; color: white; border: none; cursor: pointer; width: 100%; }
        form button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <form method="POST">
        <input name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
''')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    