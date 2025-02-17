import sqlite3
import os
from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/mydatabase.db'

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './templates/')
app = Flask(__name__, template_folder=template_path)
app.config.from_object(__name__)

def connect_to_db():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_db()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def run_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def default():
    run_query("""CREATE TABLE IF NOT EXISTS users (Username text,Password text,firstname text, lastname text, email text, address text,  count integer)""")
    return render_template('login.html')


@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = run_query("""SELECT firstname,lastname,email, address, count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password))
        if result:
            for row in result:
                return profile(row[0], row[1], row[2], row[3], row[4])
        else:
            message = 'User not dounf'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('login.html', message = message)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        address = str(request.form['address'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = null
            word_count = null
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = run_query("""SELECT *  FROM users WHERE Username  = (?)""", (username,))
        if result:
            message = 'User has already registered!'
        else:
            result1 = run_query("""INSERT INTO users (username, password, firstname, lastname, email, address, count) values (?, ?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, address, word_count,))
            commit()
            result2 = run_query("""SELECT firstname,lastname,email, address, count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password))
            if result2:
                for row in result2:
                    return profile(row[0], row[1], row[2], row[3], row[4])
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('register.html', message = message)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

def profile(firstname, lastname, email, address, count):
    return render_template('profile.html', user={'firstName':firstname, 'lastName':lastname, 'email':email, 'address': address, 'count':count})

@app.route("/viewdb")
def viewdb():
    rows = run_query("""SELECT * FROM users""")
    return '<br>'.join(str(row) for row in rows)
if __name__ == '__main__':
    app.run()