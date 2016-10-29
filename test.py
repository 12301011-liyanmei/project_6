from flask import Flask,request,render_template
import sqlite3
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

DB_SQLITE_NAME = "test.db"
db_conn = None
cursor = None

def __init__():
   try:
      db_conn = sqlite3.connect(DB_SQLITE_NAME)
   except sqlite3.Error as e:
      return
   
   cursor = db_conn.cursor()
   sql_del = "DROP TABLE IF EXISTS users;"
   try:
      cursor.execute(sql_del)
   except sqlite3.Error as e:
      print('ERROR')
   return
   db_conn.commit()

   sql_add = '''CREATE TABLE users(ID INTEGER PRIMARY KEY,
                                   name VARCHAR(32),
                                   password VARCHAR(32),
                                   salt VARCHAR(32));'''
   try:
      cursor.execute(sql_add)
   except sqlite3.Error as e:
      print('ERROR')
   db_conn.commit()
   return

@app.route('/register',methods=['GET','POST'])
def register():
   if request.method == 'GET':
      return render_template("register.html")  
   if request.method == 'POST':
      u = request.form.get('username')
      p = request.form.get('password')
      #p,s = encrypt_password(request.form.get['password'])
      cursor.execute('INSERT INTO users (name,password) VALUES (%s,%s)',(u,p))
      db_conn.commit()
      return redirect(url_for('signin'))

@app.route('/signin',methods = ['GET','POST'])
def signin():
   if request.method == 'GET':
      referer = request.args.get('next','/')  
      return render_template("login.html",next=referer)
   if request.method == 'POST':
      u = request.form.get('username')
      p = request.form.get('password')
      n = request.form.get('next')
      try:
         cursor.execute('SELECT name FROM users WHERE name=%s',(u,))
         if not cursor.fetchone():
            raise Exception(u"Wrong username or password") 
         cursor.execute('SELECT salt,password FROM users WHERE name= %s',(u,))
         salt,password = cursor.fetchone()
         if encrypt_passowrd(p,salt)[0] == password:
            session['logged_in'] = u
            return redirect(next)
         else:
            raise loginError(u'Wrong username or password')
      except Exception as e:
         return render_template('login.html',next=next)   

@app.route('/signout',methods=['POST'])
def signout():
   session.pop('logged_in',None)
   return redirect(url_form('home'))

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8080,debug=True)         
