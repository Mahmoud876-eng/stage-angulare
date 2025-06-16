from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from flask_session import Session
import sqlite3
#flask configuration
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:4200"])
#sert secret key for session management
app.config["SECRET_KEY"] = "your_secret_key_here"
#session 
#app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
Session = Session(app)
#end of flask configuration
#database connection
def con():
    conn = sqlite3.connect('clients_litiges.db')
    cursor = conn.cursor()
    return cursor
#to transfer sql into json
def disc(cursor, rows):
    columns= [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


@app.route('/litige/all')
def show_all_litige():
    cursor=con()
    cursor.execute('SELECT * FROM litiges ')
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    cursor.execute('SELECT * FROM clients ')
    client = cursor.fetchall()
    clients = disc(cursor, client)
    return jsonify({"litiges" : litiges,"client": clients }), 200
@app.route('/litige')
def show_litige():
    cursor=con()
    cursor.execute('SELECT * FROM litiges')
    litige = cursor.fetchmany(1)
    litiges = disc(cursor, litige)
    cursor.execute('SELECT * FROM clients ')
    client = cursor.fetchmany(1)
    client = disc(cursor, client)
    cursor.execute('SELECT * FROM clients ')
    clienty = cursor.fetchall()
    clients = disc(cursor, clienty)
    return jsonify({"litiges" : litiges,"client": client,"clients": clients }), 200
@app.route('/litige/<string:name>')
def show_litige_by_name(name):
    cursor=con()
    
    cursor.execute('SELECT * FROM clients WHERE name = ?', (name,))
    client = cursor.fetchmany(1)
    clients = disc(cursor, client)
    cursor.execute('SELECT id FROM clients WHERE name = ?', (name,))
    id = cursor.fetchone()
    print(id)
    cursor.execute('SELECT * FROM litiges WHERE clientId = ?', id)
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    return jsonify({"client": clients, "litiges": litiges }), 200
@app.route('/pie/<int:id>')
def show_number_dispute(id):#want u to try later with not a functio n with this line curssor.execute('SELECT description, count(*) FROM litiges group by description')
    #do a function to seperate the disputes it will be lesser lines and easier to read
    curssor = con()
    return jsonify

@app.route('/line')
def show_number_dispute_day():
    #later find a wat to send all the days cause the form is a bit weird when u sent it
    
    curssor = con()
    curssor.execute('SELECT dateDepot, count(*) FROM litiges group by description, dateDepot order by dateDepot ')
    types = curssor.fetchall() 
    return jsonify({"dispute": types}), 200
@app.route('/test')
def test():
    curssor = con()
    curssor.execute('SELECT description, count(*) FROM litiges group by description')
    types = curssor.fetchall()
    return jsonify({"dispute": types}), 200
@app.route('/insert')
def insert_sample_litiges():
    return jsonify({"message": "just to close the data so the fct dont work"}), 200
    cursor = con()
    data = [
        (
            "Jean Dupont", 2, 1, "2025-05-28", "Produit reçu endommagé.", 10, 350.0,
            "damaged_goods", "987654321", "photo_domage.jpg", "moyenne", "",
            "en cours", "qualité"
        ),
        (
            "Marie Curie", 3, 0, "2025-06-01", "Produit reçu endommagé.", 11, 120.0,
            "damaged_goods", "123456789", "photo_domage2.jpg", "haute", "",
            "ouvert", "qualité"
        ),
        (
            "Paul Martin", 4, 1, "2025-06-05", "Produit reçu endommagé.", 12, 200.0,
            "damaged_goods", "555555555", "photo_domage3.jpg", "basse", "",
            "résolu", "qualité"
        )
    ]
    cursor.executemany("""
        INSERT INTO litiges (
            agentTraitant, clientId, confirmer, dateDepot, description, id, montant,
            motif, numeroCommande, pieceJointe, priorite, resolution, statut, typeLitige
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    cursor.connection.commit()
    return jsonify({"message": "Sample litiges inserted"}), 201
@app.route('/litige/<int:id>/<string:name>')#make it send it to the client fot it  to make the autosearch the id is of the client
def show_litige_by_name_id(id,name):
    cursor = con()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (id,))
    client = cursor.fetchall()
    clients = disc(cursor, client)
    cursor.execute('SELECT * FROM litiges WHERE description = ?', (name,))
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    return jsonify({"client": clients, "litiges": litiges}), 200
@app.route('/litige/<int:id>')#make it send it to the client fot it  to make the autosearch the id is of the client
def show_litige_by_id(id):
    cursor = con()
    cursor.execute('SELECT * FROM litiges WHERE clientid = ?', (id,))
    litigey = cursor.fetchall()
    litiges = disc(cursor, litigey)
    cursor.execute('SELECT * FROM litiges WHERE clientid = ?', (id,))
    litigez = cursor.fetchmany(1)
    litige = disc(cursor, litigez)
    cursor.execute('SELECT * FROM clients WHERE id = ?', (id,))
    client = cursor.fetchall()
    clients = disc(cursor, client)
    return jsonify({"clients": litiges, "client":clients,"litiges": litige}), 200


if __name__ == '__main__':
    app.run(debug=True)

