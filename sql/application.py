import sqlite3
import datetime
from datetime import timedelta

# Register adapters and converters for date and datetime
sqlite3.register_adapter(datetime.date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime.datetime, lambda d: d.isoformat())
sqlite3.register_converter("DATE", lambda s: datetime.date.fromisoformat(s.decode()))
sqlite3.register_converter("TIMESTAMP", lambda s: datetime.datetime.fromisoformat(s.decode()))

# Connect to SQLite database (creates dispute.db if it doesn't exist)
conn = sqlite3.connect(
    'dispute.db',
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
)
cursor = conn.cursor()

# Drop tables if they exist for a clean start
cursor.execute("DROP TABLE IF EXISTS litiges")
cursor.execute("DROP TABLE IF EXISTS invoices")
cursor.execute("DROP TABLE IF EXISTS clients")

# Create clients table
cursor.execute("""
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
""")

# Create invoices table
cursor.execute("""
CREATE TABLE invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    invoice_number TEXT NOT NULL UNIQUE,
    montant DECIMAL(10, 2) NOT NULL,
    issue_date DATE NOT NULL,
    invoices_status TEXT NOT NULL CHECK (invoices_status IN ('pending', 'paid', 'overdue', 'disputed')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE RESTRICT
)
""")

# Create litiges (disputes) table without user_id
cursor.execute("""
CREATE TABLE litiges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    clientId INTEGER NOT NULL,
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

# Insert sample clients with different created_at and updated_at dates
now = datetime.datetime.now()
clients = [
    ('Acme Corp', 'acme@example.com', '1234567890', '123 Main St', now - timedelta(days=30), now - timedelta(days=25)),
    ('Globex Inc', 'globex@example.com', '0987654321', '456 Elm St', now - timedelta(days=20), now - timedelta(days=15)),
    ('Soylent Corp', 'soylent@example.com', '5555555555', '789 Oak St', now - timedelta(days=10), now - timedelta(days=5)),
    ('Umbrella LLC', 'umbrella@example.com', '2223334444', '321 Maple Ave', now - timedelta(days=40), now - timedelta(days=35)),
    ('Wayne Enterprises', 'wayne@example.com', '7778889999', '1007 Mountain Dr', now - timedelta(days=50), now - timedelta(days=45)),
    ('Stark Industries', 'stark@example.com', '1112223333', '10880 Malibu Point', now - timedelta(days=60), now - timedelta(days=55)),
    ('Wonka Inc', 'wonka@example.com', '6665554444', '1 Chocolate Factory', now - timedelta(days=70), now - timedelta(days=65))
]
cursor.executemany("INSERT INTO clients (name, email, phone, address, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", clients)

# Insert sample invoices

# Insert sample invoices with different created_at and updated_at dates
invoices = [
    (1, 'INV-001', 1000.00, '2024-06-01', 'pending', now - timedelta(days=29), now - timedelta(days=28)),
    (1, 'INV-002', 1500.50, '2024-05-15', 'paid', now - timedelta(days=19), now - timedelta(days=18)),
    (2, 'INV-003', 2000.00, '2024-04-20', 'overdue', now - timedelta(days=9), now - timedelta(days=8)),
    (3, 'INV-004', 500.00, '2024-06-10', 'disputed', now - timedelta(days=4), now - timedelta(days=2)),
    (2, 'INV-005', 800.00, '2024-07-01', 'disputed', now - timedelta(days=3), now - timedelta(days=2)),
    (2, 'INV-006', 800.00, '2024-07-10', 'disputed', now - timedelta(days=9), now - timedelta(days=5)),
    (1, 'INV-007', 1200.00, '2024-07-05', 'disputed', now - timedelta(days=1), now),
    (3, 'INV-008', 950.00, '2024-07-08', 'paid', now, now),
    (4, 'INV-009', 600.00, '2024-06-15', 'overdue', now - timedelta(days=12), now - timedelta(days=10)),
    (5, 'INV-010', 1100.00, '2024-06-20', 'overdue', now - timedelta(days=7), now - timedelta(days=6)),
    (6, 'INV-011', 1300.00, '2024-07-01', 'overdue', now - timedelta(days=5), now - timedelta(days=4)),
    (7, 'INV-012', 700.00, '2024-07-03', 'overdue', now - timedelta(days=3), now - timedelta(days=2)),
    (7, 'INV-013', 2100.00, '2024-07-15', 'overdue', now - timedelta(days=2), now - timedelta(days=1))

]
cursor.executemany("""
INSERT INTO invoices (client_id, invoice_number, montant, issue_date, invoices_status, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", invoices)

# Insert sample disputes (litiges) without user_id

# Insert sample litiges with different opened_at and updated_at dates
litiges = [
    (4, 3, 'in_court', 'Legal action initiated for unpaid invoice.', (now + timedelta(days=30)).date(), (now - timedelta(days=8)).date(), (now - timedelta(days=14)).date(), None),
    (5, 2, 'open', 'Client disputes the amount charged.', (now + timedelta(days=10)).date(), (now - timedelta(days=3)).date(), (now - timedelta(days=2)).date(), None),
    (7, 1, 'investigating', 'Awaiting more documents from client.', (now + timedelta(days=5)).date(), (now - timedelta(days=1)).date(), now.date(), None),
    (6, 2, 'resolved', 'Dispute resolved, payment received.', (now + timedelta(days=5)).date(), (now - timedelta(days=1)).date(), (now - timedelta(days=1)).date(), now),
    (3, 2, 'investigating', 'Client claims invoice was paid but not registered.', (now + timedelta(days=7)).date(), (now - timedelta(days=5)).date(), (now - timedelta(days=4)).date(), None)
]
cursor.executemany("""
INSERT INTO litiges (invoice_id, clientId, status, description, due_date, opened_at, updated_at, resolution_date)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", litiges)

conn.commit()
conn.close()
