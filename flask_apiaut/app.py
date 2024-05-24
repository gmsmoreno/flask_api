#app.py
from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS #pip install -U flask-cors
from datetime import timedelta
 
import psycopg2 #pip install psycopg2 
import psycopg2.extras
 
app = Flask(__name__)
  
app.config['SECRET_KEY'] = 'gabrielcoders'
  
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
CORS(app) 
 
DB_HOST = "localhost"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "postgres"
     
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)  
 
@app.route('/')
def home():
    passhash = generate_password_hash('gabrielcoders')
    print(passhash)
    if 'username' in session:
        username = session['username']
        return jsonify({'message' : 'Você já está logado', 'username' : username})
    else:
        resp = jsonify({'message' : 'Não autorizado'})
        resp.status_code = 401
        return resp
  
@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _username = _json['username']
    _password = _json['password']
    print(_password)
    # validate the received values
    if _username and _password:
        #check user exists          
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
          
        sql = "SELECT * FROM useraccount WHERE username=%s"
        sql_where = (_username,)
          
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        username = row['username']
        password = row['password']
        if row:
            if check_password_hash(password, _password):
                session['username'] = username
                cursor.close()
                return jsonify({'message' : 'Você foi logado com sucesso!'})
            else:
                resp = jsonify({'message' : 'Bad Request - senha inválida'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'message' : 'Bad Request - credencial inválida'})
        resp.status_code = 400
        return resp
          
@app.route('/logout')
def logout():
    if 'username' in session:
        #session.clear()
        session.pop('username', None)
    return jsonify({'message' : 'Você deslogou da conta!'})
          
if __name__ == "__main__":
    app.run()