from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re

app = Flask(__name__)

app.secret_key = "secret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'phpmyadmin'
app.config['MYSQL_PASSWORD'] = 'hackerman'
app.config['MYSQL_DB'] = 'shopDB'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Products')
    data = cur.fetchall()
    cur.close()
    return render_template('homepage.html', data=data)

@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # Display producs and price
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Products')
        products = cur.fetchall()
        return render_template('home.html', username=session['username'], products=products)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    ##id = [0]
    ##username = [1]
    ##password = [2]
    ##email = [3]
    msg =''
    #Check if POST and if username and password is filled in.
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        #Check if in DB
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cur.fetchone()
        #If account exists:
        if account:
            session['loggedin'] = True
            session['id'] = account[0] #ID
            session['username'] = account[1] #Username
            #redirect to homepage
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username or password'

    return render_template('index.html', msg=msg)

@app.route('/pythonlogin/logout')
def logout():
    #remove session data to clear user
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    #redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #check if account exists in MySQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cur.fetchone()
        #error handling:
        if account:
            msg = 'Account already exist!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            #Account doesend exist and the form data is valid. insert new account to DB
            cur.execute('INSERT INTO accounts VALUES (NULL,%s,%s,%s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        #empty form
        msg = 'Please fill out the form!'
    #display register-page
    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        print(session['id'])
        account = cur.fetchone()
        print(account)
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/home/iPhone_11_max', methods=['GET', 'POST'])
def iPhone_11_max():
    id = 1001
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Products WHERE ProductID = %s', [id])
    product = cur.fetchone()
    print(product)
    cur.execute('SELECT * FROM Comments WHERE ProductID = %s', [id])
    coms = cur.fetchall()
    cur.close()
    if request.method == 'POST' and 'comment' in request.form:
        comment = request.form['comment']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Comments VALUES (%s,%s,%s)', (id, session['username'], comment))
        mysql.connection.commit()
        print(session['id'])
        cur.close()
    return render_template('iPhone_11_max.html', product=product, coms=coms)

if __name__ == '__main__':
    app.run(debug=True)
