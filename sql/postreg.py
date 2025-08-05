
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from flask_session import Session
import jwt
import psycopg2
import psycopg2.extras
from dateutil import parser
from datetime import datetime, timedelta
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
#token configuration
SECRET_KEY = "1234" 
#database connection
def coni():
    conn = psycopg2.connect(
        dbname="dispute",
        user="postgres",
        password="123456",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn, cursor
def con():
    conn = psycopg2.connect(
        dbname="dispute",
        user="postgres",
        password="123456",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor
#to transfer sql into json
def disc(cursor, rows):
    return [dict(row) for row in rows]


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
    
    cursor.execute('SELECT * FROM clients WHERE name = %s', (name,))
    client = cursor.fetchmany(1)
    clients = disc(cursor, client)
    cursor.execute('SELECT id FROM clients WHERE name = %s', (name,))
    id = cursor.fetchone()
    print(id)
    cursor.execute('SELECT * FROM litiges WHERE clientId = %s', id)
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    return jsonify({"client": clients, "litiges": litiges }), 200
@app.route('/pie/<int:id>')
def show_number_dispute(id):#want u to try later with not a functio n with this line curssor.execute('SELECT description, count(*) FROM litiges group by description')
    #do a function to seperate the disputes it will be lesser lines and easier to read
    curssor = con()
    curssor.execute('SELECT description, count(*) FROM litiges where clientId = %s  group by description', (id,))
    types = curssor.fetchall()
    return jsonify({"dispute": types}), 200
@app.route('/line')
def show_number_dispute_day():
    #later find a wat to send all the days cause the form is a bit weird when u sent it    
    curssor = con()
    curssor.execute('SELECT TO_CHAR(opened_at, \'YYYY-MM-DD\'), count(*) FROM litiges group by opened_at order by opened_at ')
    types = curssor.fetchall()
    return jsonify({"dispute": types}), 200
@app.route('/test')
def test():
    curssor = con()
    curssor.execute('SELECT description, count(*) FROM litiges group by description')
    types = curssor.fetchall()
    return jsonify({"dispute": types}), 200

@app.route('/litige/<int:id>/<string:name>')#make it send it to the client fot it  to make the autosearch the id is of the client
def show_litige_by_name_id(id,name):
    cursor = con()
    cursor.execute('SELECT * FROM clients WHERE id = %s', (id,))
    client = cursor.fetchall()
    clients = disc(cursor, client)
    cursor.execute('SELECT * FROM litiges WHERE description = %s', (name,))
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    return jsonify({"client": clients, "litiges": litiges}), 200
@app.route('/litige/<int:id>')#make it send it to the client fot it  to make the autosearch the id is of the client
def show_litige_by_id(id):
    cursor = con()
    cursor.execute('SELECT * FROM litiges WHERE clientId = %s', (id,))
    litigey = cursor.fetchall()
    litiges = disc(cursor, litigey)
    cursor.execute('SELECT * FROM litiges WHERE clientId = %s', (id,))
    litigez = cursor.fetchmany(1)
    litige = disc(cursor, litigez)
    cursor.execute('SELECT * FROM clients WHERE id = %s', (id,))
    client = cursor.fetchall()
    clients = disc(cursor, client)
    return jsonify({"clients": litiges, "client":clients,"litiges": litige}), 200
@app.route('/litige/<int:id>/all')
def show_client_litige(id):
    cursor=con()
    cursor.execute('SELECT * FROM litiges where clientId = %s', (id,))
    litige = cursor.fetchall()
    litiges = disc(cursor, litige)
    cursor.execute('SELECT * FROM clients where id = %s', (id,))
    client = cursor.fetchall()
    clients = disc(cursor, client)
    return jsonify({"litiges" : litiges,"client": clients }), 200
@app.route('/line/<int:id>')
def show_client_dispute_day(id):

    cursor = con()
    cursor.execute('SELECT TO_CHAR(opened_at, \'YYYY-MM-DD\'), count(*) FROM litiges where clientId = %s group by description, opened_at order by opened_at', (id,))
    types = cursor.fetchall()
    print(types)
    return jsonify({"dispute": types}), 200
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    mail = data.get('email')
    password = data.get('password')
    curssor = con()
    #it s username cause I wrote it wrongly in the db
    curssor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (mail, password))
    id = curssor.fetchmany()
    #clients = disc(curssor, id)
    print(id)
    if not id:
        return jsonify({"error": "Invalid username or password"}), 401
    
    payload = {
        'mail': mail,
        'exp': datetime.now() + timedelta(hours=1)
    }
    token= jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({"token": token}), 200
        
@app.route('/register/litige', methods=['POST'])
def register_litige():
    data = request.json
    conn, cursor = coni()
    invoice_id = data.get('invoice_id')
    clientId = data.get('clientId')
    status = data.get('status')
    description = data.get('description')
    
    opened_at = data.get('opened_at')
    

    cursor.execute("""
        INSERT INTO litiges (
            invoice_id, clientId, status, description, opened_at
        ) VALUES (%s, %s, %s, %s, %s)
    """, (
        invoice_id, clientId, status, description, opened_at, 
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Litige registered successfully"}), 201
@app.route("/letiges/join")
def join_litige():
    conn, cursor = coni()
    cursor.execute("""
        SELECT *
        FROM clients
        JOIN invoices ON clients.id = invoices.client_id
    """)
    results = cursor.fetchall()
    data=disc(cursor, results)
    cursor.execute("""
        select *
        from clients            
    """)
    results=cursor.fetchall()
    client=disc(cursor,results)
    conn.close()
    return jsonify({"data": data, "clients": client}), 200
@app.route('/letiges/join/group')
def join_litige_group():
    conn, cursor = coni()
    cursor.execute("""
        SELECT *
        FROM clients
        
        JOIN invoices ON clients.id = invoices.client_id
        ORDER BY clients.name
    """)
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        select *
        from clients            
    """)
    results=cursor.fetchall()
    client=disc(cursor,results)
    
    conn.close()
    return jsonify({"data": data,"clients": client}), 200
@app.route('/column')
def column():
    conn, cursor = coni()
    cursor.execute("""
        select name,count(*) as count
        from clients
        join litiges on clients.id = litiges.clientId
        
        group by name
        order by count DESC
    """)
    invoice= cursor.fetchmany(8)
    invoices = disc(cursor, invoice)
    conn.close()
    return jsonify({"invoices": invoices}), 200
@app.route('/column/overdue')
def column_overdue():
    conn, cursor = coni()
    cursor.execute("""
        select name,count(*) as count
        from clients
        join invoices on clients.id = invoices.client_id
        where invoices.invoices_status = 'overdue'
        group by name
        order by count DESC
    """)
    invoice= cursor.fetchmany(8)
    invoices = disc(cursor, invoice)
    conn.close()
    return jsonify({"invoices": invoices}), 200
@app.route('/api/invoices/<int:id>', methods=['PUT'])
def update_invoice(id):
    conn, cursor = coni()
    cursor.execute('SELECT invoices_status FROM invoices WHERE invoice_id = %s', (id,))
    invoice = cursor.fetchone()
    if not invoice:
        conn.close()
        return jsonify({"error": "Invoice not found"}), 404
    
    data = request.json
    status = data.get('invoices_status')
    updated_at = data.get('updated_at')
    montant = data.get('montant')
    cursor.execute("""
        UPDATE invoices
        SET invoices_status = %s, updated_at = %s, montant = %s
        WHERE invoice_id = %s
    """, (status, updated_at, montant, id))
    conn.commit()
    if invoice[0]=="disputed"and status!="disputed":
        cursor.execute("""
            UPDATE litiges
            SET status = 'resolved', resolution_date = %s
            WHERE invoice_id = %s
        """, (updated_at, id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Invoice updated and dispute resolved successfully"}), 200
    if status=="disputed":
        cursor.execute("select * from litiges where invoice_id = %s", (id,))
        litige=cursor.fetchmany(1)
        litiges=disc(cursor, litige)
        conn.close()
        return jsonify({"message": litiges}), 200
    conn.close()
    return jsonify({"message": "Invoice updated successfully"}), 200
@app.route('/autocomplete/<string:name>')
def autocomplete(name):
    conn, cursor = coni()
    name=f"%{name}%"
    cursor.execute("""
        select *
        from clients
        join invoices on clients.id = invoices.client_id
        where clients.name ILIKE %s
    """, (name,))
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        select *
        from clients            
    """)
    results = cursor.fetchall()
    client = disc(cursor, results)
    conn.close()
    return jsonify({"data": data, "clients": client}), 200
@app.route('/client/join')
def join_client():
    conn, cursor = coni()
    cursor.execute("""
        SELECT *
        FROM clients
        JOIN litiges ON clients.id = litiges.clientId
    """)
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        select distinct name
        from clients
        join litiges on clients.id = litiges.clientId
    """)
    results = cursor.fetchall()
    client = disc(cursor, results)
    conn.close()
    return jsonify({"data": data, "clients": client}), 200
@app.route('/client/join/<int:id>')
def join_clients(id):
    conn, cursor = coni()
    cursor.execute("""
        SELECT *
        FROM clients
        JOIN litiges ON clients.id = litiges.clientId
        WHERE clients.id = %s
    """, (id,))
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        SELECT *
        FROM clients            
    """)
    results = cursor.fetchall()
    client = disc(cursor, results)
    conn.close()
    return jsonify({"data": data, "clients": client}), 200
@app.route('/filterbytime')
def filter_by_time():
    conn, cursor =coni()
    max=request.args.get('max')
    min=request.args.get('min')
 
    cursor.execute("""
        SELECT *
        FROM clients
        Join invoices ON clients.id = invoices.client_id
        WHERE invoices.created_at BETWEEN %s AND %s
        """, (min, max))
    results = cursor.fetchall()
    data = disc(cursor, results)
   
    results = cursor.fetchall()
    clients = disc(cursor, results)
    conn.close()
    return jsonify({"data": data}), 200
@app.route('/autocomplete/clients/<string:name>')
def autocomplete_client(name):
    conn, cursor = coni()
    cursor.execute("""
        select *
        from clients
        Left join litiges on clients.id = litiges.clientId
        where clients.name = %s
    """, (name,))
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        select distinct name
        from clients
        join litiges on clients.id = litiges.clientId
    """)

    results = cursor.fetchall()
    client = disc(cursor, results)
    
    conn.close()
    return jsonify({"data": data, "clients": client}), 200
@app.route('/update/all', methods=['patch'])
def update_all():
    conn, cursor = coni()
    data = request.json
    invoice_id = data.get('id')
    date = data.get('date')
    money = data.get('money')
    
    print(invoice_id, date, money)
    cursor.execute("""
        UPDATE invoices
        SET updated_at = %s , invoices_status = 'paid', amount_paid = %s
        WHERE invoice_id = %s
    """, (date, money, invoice_id))

    cursor.execute("""
        UPDATE litiges
        SET status = 'resolved', resolution_date = %s
        WHERE invoice_id = %s
    """, (date, invoice_id))
    conn.commit()
    
    conn.close()
    return jsonify({"yup": "updated"}), 200
@app.route('/notifications')
def notifications():
    conn,cursor= coni()
    cursor.execute("""
        select *
        from notifications
        where read = True
                   
    """
     )
    result= cursor.fetchall()
    notifications=disc(cursor,result)
    conn.close
    return jsonify({"notifications":notifications })
@app.route('/notifications/delete', methods=['PATCH'])
def delete():
    conn,cursor=coni()
    data=request.json
    message=data['message']
    if not message:
        return jsonify({"error": "Message is required"}), 400
    cursor.execute("""
        update notifications
        set read = %s
        where message=%s
    """,(False, message))
    conn.commit()
    conn.close()
    return jsonify({"message": "Notification marked as read"}), 200
@app.route('/notifications/insert', methods=['POST'])
def not_insert():
    conn, cursor = coni()
    data = request.json
    id = data.get('id')
    message="paid invoice"
    if not message:
        return jsonify({"error": "Message is required"}), 400
    cursor.execute("""
        INSERT INTO notifications (message, read)
        VALUES (%s, %s)
    """, (message, True))
    conn.commit()
    conn.close()
    return jsonify({"message": "Notification inserted successfully"}), 201
@app.route('/notifications/<int:id>', methods=['GET'])
def notifications_inv(id):
    conn, cursor = coni()
    cursor.execute("""
        SELECT *
        FROM clients
        JOIN invoices ON clients.id = invoices.client_id
        where invoices.invoice_id = %s
    """, (id,))
    results = cursor.fetchall()
    data=disc(cursor, results)
    conn.close()
    return jsonify({"data": data}), 200 
@app.route('/mail/<string:mail>')
def delete_notification(mail):
    conn, cursor = coni()
    mail=f"%{mail}%"
    cursor.execute("""
        select *
        from clients
        join invoices on clients.id = invoices.client_id
        where clients.email ILIKE %s
    """, (mail,))
    results = cursor.fetchall()
    data = disc(cursor, results)
    cursor.execute("""
        select *
        from clients            
    """)
    results = cursor.fetchall()
    client = disc(cursor, results)
    conn.close()
    
    return jsonify({"data": data, "clients": client}), 200
   
    
if __name__ == '__main__':
    app.run(debug=True)

