import os
from os import write
from flask import Flask, render_template, redirect, request
import csv
from werkzeug.utils import redirect
from . import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db


app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_endpoint():
    return '200 OK'

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    ## TODO: Return a register page
    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200 
        else:
            return error, 418
    
    ## TODO: Return a login page
    return render_template('login.html')



"""
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/works.html')
def works():
    return render_template('works.html')

@app.route('/work.html')
def work():
    return render_template('work.html')
"""

@app.route('/contactform', methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            form_data(data)
            message_form = "Thank you for contacting me. I will get in touch with you shortly."
            return render_template('submission.html', message=message_form)
        except:
            message_form = "Database writing error!"
            return render_template('submission.html', message=message_form)
    else:
        message_form = "Form not submitted. Try again!"
        return render_template('submission.html', message=message_form)

@app.route('/<string:page_name>')
def page_direct(page_name='/'):
    try:
        return render_template(page_name)
    except:
        return redirect('/')

def form_data(data):
    email = data['email']
    subject = data['subject']
    message = data['message']
    with open('database.csv', 'w', newline='') as csvfile:
        form_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        form_writer.writerow([email, subject, message])