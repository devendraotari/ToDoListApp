from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sendemail import EmailSender
from passwordgenrator import generateRandomPassword

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'qazxswedcvfr'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythondb'


mysql = MySQL(app)

# @app.route('/favicon.ico')
# def favicon():
#     return url_for('static',filename='favicon.ico')

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
        # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userloginDetails WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect('/home')
            # return f"<h1>Welcome {account['username']}</h1>"
            # Redirect to home page
        else:
           # Account doesnt exist or username/password incorrect
           msg = 'Incorrect username/password!'
           return render_template('index.html', msg=msg)
    else:
        return render_template('index.html', msg=msg)

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not username and not password:
            msg = 'Please fill out the form!'
            return render_template('register.html', msg=msg)
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userloginDetails WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO userloginDetails VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'    
        
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/forgotpassword', methods = ['GET','POST'])
def forgotpassword():
    msg = ''
    note = 'temporary password will be sent to your email'
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userloginDetails WHERE email = %s', (email,))
        
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            new_password = generateRandomPassword(10)
            cursor.execute('UPDATE userloginDetails set password = %s WHERE id = %s', (new_password,account['id'],))
            mysql.connection.commit()
            emailSender = EmailSender(new_password,account['email'])
            emailSender.sendEmail()
            msg = "check email for temporary password and login with it "
        return render_template("index.html",msg = msg)
    else:
        return render_template("forgotpassword.html",msg = note)


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session["__invalidate__"] = True
    return redirect('/')

@app.route('/home')
def home():
    if "id" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usertasks WHERE id = %s', (session['id'],))
        tasks = cursor.fetchall()
        for task in tasks:
            print(f"TASK->{task['task']} status->{task['status']}")
        return render_template('home.html',tasks=tasks,msg=session['username'])
    else:
        return redirect('/')

@app.route('/add',methods=['POST'])
def add():
    task = request.form['todoitem']
    print(f"TASK FROM FORM->{task}")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT into usertasks values (NULL,%s,0,%s)",(session['id'],task,))
    mysql.connection.commit()
    return redirect('/home')

@app.route('/task/<taskname>/<taskstatus>')
def change_task_status(taskname,taskstatus):
    i_taskstatus = int(taskstatus)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if i_taskstatus==1:
        cursor.execute('UPDATE usertasks set status=0 WHERE id = %s and task= %s', (session['id'],taskname,))
    elif i_taskstatus==0:
        cursor.execute('UPDATE usertasks set status=1 WHERE id = %s and task= %s', (session['id'],taskname,))
    mysql.connection.commit()     
    return redirect("/home")


@app.route("/delete/<task>")
def deletetask(task):
    del_task=task
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE from usertasks where id = %s and task = %s",(session['id'],del_task,))
    mysql.connection.commit()
    return redirect("/home")