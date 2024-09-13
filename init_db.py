import sqlite3

def init_db():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()

    # Kreiranje tabele za osnovne informacije o pacijentima
    c.execute('''CREATE TABLE IF NOT EXISTS pacijenti (
                 health_card_id INTEGER PRIMARY KEY,
                 first_name TEXT NOT NULL,
                 last_name TEXT NOT NULL)''')

    # Kreiranje tabele za podatke o pacijentima
    c.execute('''CREATE TABLE IF NOT EXISTS pacijent_podaci (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 health_card_id INTEGER,
                 heart_rate INTEGER,
                 gsr REAL,
                 datetime TEXT,
                 comment TEXT,
                 FOREIGN KEY (health_card_id) REFERENCES pacijenti (health_card_id))''')

    conn.commit()
    conn.close()
    print("Database and tables initialized successfully.")

if __name__ == '__main__':
    init_db()
