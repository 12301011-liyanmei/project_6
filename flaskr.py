# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~
    A microblog example application written as Flask tutorial with
    Flask and sqlite3.
    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
import hashlib
import psutil
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# create our little application :)
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

# Load default config and override config from an environment variable


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('sqlite.db')
    cursor = rv.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")
    rv.commit()
    
    try:
        cursor.execute("CREATE TABLE users(ID integer primary key autoincrement,                                           name varchar(32) not null,                                                      password varchar(32) not null);")           
    except sqlite3.Error as e:
        print("ERROR")
    rv.commit()
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    db = sqlite3.connect('sqlite.db')
    return db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
  
def encrypt_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).encode('hex') # length 32
    result = password
    for i in range(3):
        result = hashlib.sha256(password + salt).hexdigest()[::2] #length 32
    return result, salt
  
class loginError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


@app.route('/show_info')
def show_info():
#   db = get_db()
#   cur = db.execute('select title, text from entries order by id desc')
#   entries = cur.fetchall()
    mem = psutil.virtual_memory()
    total = mem.total/(1024*1024)
    used = mem.used/(1024*1024)
    usedPer = '%.2f' % (used/total * 100) + '%'
    cpuPer = (str)(psutil.cpu_percent(0))+'%'
    return render_template('show_info.html',usedPer=usedPer)


@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    db = connect_db()
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        u = request.form.get('username') 
        p = request.form.get('password')
        rp = request.form.get('confirm-password')
        if p != rp:
            error = 'password does not match'
            return render_template('register.html',error=error)
#        p,s=encrypt_password(p)
        db.execute("insert into users (name, password) values (?,?)",(u,p))
        db.commit()
        flash('New entry was successfully posted')
        db.close()
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        referrer = request.args.get('login','/')
        return render_template("login.html",next=referrer)
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
#        n = request.form('login')
        try:
            cursor.execute("SELECT name FROM users WHERE name = ?",[u])
            if not cursor.fetchone():
                print("!!!!!!!!!!!!!!!!!!name"+u)
                raise loginError(u'错误的用户名或者密码!,name=')
            cursor.execute("SELECT password FROM users WHERE name = ?",[u])
            password = cursor.fetchone()
            print("!!!!!!!!!!!!!!!!!!!!password"+str(password[0]))
            if p == str(password[0]):
                session['logged_in'] = u
                return redirect(url_for('show_info'))
            else:
                print("!!!!!!!!!!!!!!!!!pass="+p)
                raise loginError(u'错误的用户名或者密码!')
        except loginError as e:
            return render_template('login.html', next=next,error=e.value)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_info'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
