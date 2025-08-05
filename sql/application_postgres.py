import psycopg2
from datetime import datetime, timedelta

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="dispute",
    user="postgres",
    password="123456",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Drop tables if they exist for a clean start
cursor.execute("DROP TABLE IF EXISTS litiges CASCADE")
cursor.execute("DROP TABLE IF EXISTS invoices CASCADE")
cursor.execute("DROP TABLE IF EXISTS clients CASCADE")
cursor.execute("DROP TABLE IF EXISTS notifications CASCADE")
cursor.execute("DROP TABLE IF EXISTS users CASCADE")

# Create clients table
cursor.execute("""
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
""")

# Create users table
cursor.execute("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)
""")

# Create invoices table
cursor.execute("""
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    invoice_number TEXT NOT NULL UNIQUE,
    montant NUMERIC(10, 2) NOT NULL,
    amount_paid NUMERIC(10, 2) DEFAULT 0,
    due_date DATE NOT NULL,
    invoices_status TEXT NOT NULL CHECK (invoices_status IN ('pending', 'paid', 'overdue', 'disputed')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT
)
""")

# Create litiges (disputes) table
cursor.execute("""
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
)
""")
cursor.execute("""
CREATE TABLE litiges (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    clientId INTEGER NOT NULL,
    litige_number TEXT,
    status TEXT NOT NULL CHECK (status IN ('open', 'investigating', 'in_court', 'resolved')),
    description TEXT NOT NULL,
    due_date DATE NOT NULL,
    opened_at TIMESTAMP,
    updated_at TIMESTAMP,
    resolution_date TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE RESTRICT,
    FOREIGN KEY (clientId) REFERENCES clients(id) ON DELETE RESTRICT
)
""")

# Insert sample clients
now = datetime.now()
clients = [
    ('Acme Corp', 'acme@example.com', '1234567890', '123 Main St', now - timedelta(days=30), now - timedelta(days=25)),
    ('Globex Inc', 'globex@example.com', '0987654321', '456 Elm St', now - timedelta(days=20), now - timedelta(days=15)),
    ('Soylent Corp', 'soylent@example.com', '5555555555', '789 Oak St', now - timedelta(days=10), now - timedelta(days=5)),
    ('Umbrella LLC', 'umbrella@example.com', '2223334444', '321 Maple Ave', now - timedelta(days=40), now - timedelta(days=35)),
    ('Wayne Enterprises', 'wayne@example.com', '7778889999', '1007 Mountain Dr', now - timedelta(days=50), now - timedelta(days=45)),
    ('Stark Industries', 'stark@example.com', '1112223333', '10880 Malibu Point', now - timedelta(days=60), now - timedelta(days=55)),
    ('Wonka Inc', 'wonka@example.com', '6665554444', '1 Chocolate Factory', now - timedelta(days=70), now - timedelta(days=65))
]
cursor.executemany("INSERT INTO clients (name, email, phone, address, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)", clients)

# Insert sample users
users = [
    ('mah', '1'),
]
cursor.executemany("INSERT INTO users (username, password) VALUES (%s, %s)", users)

# Insert sample invoices (now with due_date only)
invoices = [
    (1, 'INV-001', 1000.00, 250.00, '2024-06-30', 'pending', now - timedelta(days=29), now - timedelta(days=28)),
    (1, 'INV-002', 1500.50, 1500.50, '2024-07-15', 'paid', now - timedelta(days=19), now - timedelta(days=18)),
    (2, 'INV-003', 2000.00, 500.00, '2024-07-20', 'overdue', now - timedelta(days=9), now - timedelta(days=8)),
    (3, 'INV-004', 500.00, 0, '2024-07-25', 'disputed', now - timedelta(days=4), now - timedelta(days=2)),
    (2, 'INV-005', 800.00, 200.00, '2024-07-30', 'disputed', now - timedelta(days=3), now - timedelta(days=2)),
    (2, 'INV-006', 800.00, 800.00, '2024-08-05', 'disputed', now - timedelta(days=9), now - timedelta(days=5)),
    (1, 'INV-007', 1200.00, 0, '2024-08-10', 'disputed', now - timedelta(days=1), now),
    (3, 'INV-008', 950.00, 950.00, '2024-08-15', 'paid', now, now),
    (4, 'INV-009', 600.00, 100.00, '2024-08-20', 'overdue', now - timedelta(days=12), now - timedelta(days=10)),
    (5, 'INV-010', 1100.00, 0, '2024-08-25', 'overdue', now - timedelta(days=7), now - timedelta(days=6)),
    (6, 'INV-011', 1300.00, 0, '2024-08-30', 'overdue', now - timedelta(days=5), now - timedelta(days=4)),
    (7, 'INV-012', 700.00, 0, '2024-09-04', 'overdue', now - timedelta(days=3), now - timedelta(days=2)),
    (7, 'INV-013', 2100.00, 500.00, '2024-09-09', 'overdue', now - timedelta(days=2), now - timedelta(days=1))
]
cursor.executemany("""
INSERT INTO invoices (client_id, invoice_number, montant, amount_paid, due_date, invoices_status, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", invoices)

# Insert sample litiges (now with litige_number)
litiges = [
    (4, 3, 'DISP_001', 'in_court', 'Legal action initiated for unpaid invoice.', (now + timedelta(days=30)).date(), (now - timedelta(days=8)).date(), (now - timedelta(days=14)).date(), None),
    (5, 2, 'DISP_002', 'open', 'Client disputes the amount charged.', (now + timedelta(days=10)).date(), (now - timedelta(days=3)).date(), (now - timedelta(days=2)).date(), None),
    (7, 1, 'DISP_003', 'investigating', 'Awaiting more documents from client.', (now + timedelta(days=5)).date(), (now - timedelta(days=1)).date(), now.date(), None),
    (6, 2, 'DISP_004', 'resolved', 'Dispute resolved, payment received.', (now + timedelta(days=5)).date(), (now - timedelta(days=1)).date(), (now - timedelta(days=1)).date(), now),
    (3, 2, 'DISP_005', 'investigating', 'Client claims invoice was paid but not registered.', (now + timedelta(days=7)).date(), (now - timedelta(days=5)).date(), (now - timedelta(days=4)).date(), None),
    (2, 1, 'DISP_006', 'open', 'Duplicate opened_at date for testing.', (now + timedelta(days=5)).date(), (now - timedelta(days=1)).date(), now.date(), None)
]


# Insert sample notifications
notifications = [
    (1, 'System update completed.', True),
    (2, 'New dispute opened for review.', True),
    (3, 'Payment received for invoice INV-008.', True),
    (4, 'Reminder: Check overdue invoices.', True)
]
cursor.executemany("""
INSERT INTO notifications (invoice_id, message, read)
VALUES (%s, %s, %s)
""", notifications)
 
cursor.executemany("""
INSERT INTO litiges (invoice_id, clientId, litige_number, status, description, due_date, opened_at, updated_at, resolution_date)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", litiges)

conn.commit()
conn.close()
