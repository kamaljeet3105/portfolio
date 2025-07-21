from flask import Flask, render_template_string, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key
DATABASE = 'contact.db'

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_table():
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        subject TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()

create_table()

# Admin login page
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple hardcoded login (change username/password as needed)
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
    return render_template_string(LOGIN_TEMPLATE)

# Admin panel (show submissions)
@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    db = get_db()
    cur = db.execute('SELECT * FROM contacts ORDER BY created_at DESC')
    contacts = cur.fetchall()
    return render_template_string(ADMIN_TEMPLATE, contacts=contacts)

# Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# API endpoint for contact form
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    db = get_db()
    db.execute('INSERT INTO contacts (name, email, subject, message) VALUES (?, ?, ?, ?)',
               (name, email, subject, message))
    db.commit()
    return render_template_string(SUCCESS_TEMPLATE)
SUCCESS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Contact Submitted</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .popup {
            background: #4BB543;
            color: white;
            padding: 20px 30px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            font-size: 18px;
            opacity: 1;
            transition: opacity 0.5s ease-out;
            margin-bottom: 20px;
        }
        .back-btn {
            background: #007BFF;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .back-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
<div class="popup" id="popup">
    ✅ Your message has been submitted successfully!
</div>
<a class="back-btn" href="javascript:history.back()">← Back</a>

<script>
    setTimeout(function(){
        var popup = document.getElementById('popup');
        popup.style.opacity = '0';
        setTimeout(function(){ popup.style.display = 'none'; }, 500);
    }, 3000);
</script>
</body>
</html>
'''



LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 6px 0 12px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #007BFF;
            border: none;
            color: white;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        .error {
            color: red;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="login-container">
    <h2>Admin Login</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
</div>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            padding: 20px;
        }
        .panel-container {
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            color: #333;
        }
        a.logout {
            display: inline-block;
            margin-bottom: 20px;
            color: #007BFF;
            text-decoration: none;
            font-weight: bold;
        }
        a.logout:hover {
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        th {
            background: #007BFF;
            color: white;
        }
        tr:hover {
            background: #f1f1f1;
        }
        @media (max-width: 768px) {
            table, thead, tbody, th, td, tr {
                display: block;
            }
            th {
                position: absolute;
                top: -9999px;
                left: -9999px;
            }
            td {
                position: relative;
                padding-left: 50%;
            }
            td:before {
                position: absolute;
                top: 10px;
                left: 10px;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                font-weight: bold;
            }
            td:nth-of-type(1):before { content: "ID"; }
            td:nth-of-type(2):before { content: "Name"; }
            td:nth-of-type(3):before { content: "Email"; }
            td:nth-of-type(4):before { content: "Subject"; }
            td:nth-of-type(5):before { content: "Message"; }
            td:nth-of-type(6):before { content: "Date"; }
        }
    </style>
</head>
<body>
<div class="panel-container">
    <h2>Contact Submissions</h2>
    <a class="logout" href="/admin/logout">Logout</a>
    <table>
        <thead>
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Date</th></tr>
        </thead>
        <tbody>
        {% for c in contacts %}
        <tr>
            <td>{{ c[0] }}</td>
            <td>{{ c[1] }}</td>
            <td>{{ c[2] }}</td>
            <td>{{ c[3] }}</td>
            <td>{{ c[4] }}</td>
            <td>{{ c[5] }}</td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
</div>
</body>
</html>
'''


if __name__ == '__main__':
    app.run(debug=True)
