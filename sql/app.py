from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from flask_session import Session
import sqlite3

# flask configuration
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:4200"])
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
Session(app)
# end of flask configuration

# helper function to get a new database connection per request
def get_db_connection():
    conn = sqlite3.connect('clients_litiges.db')
    return conn

@app.route('/litige/all', methods=['POST', 'GET'])
def show_all_litige():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM litiges')
    litiges = cursor.fetchall()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return jsonify({"litiges": litiges, "clients": clients}), 200

if __name__ == '__main__':
    app.run(debug=True)
