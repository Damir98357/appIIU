from flask import Flask, render_template, request, redirect, url_for
import random
import sqlite3
import threading
import time

app = Flask(__name__)

# Postavite serijski port za Arduino (zameni 'COM3' sa odgovarajućim portom)
try:
    import serial
    ser = serial.Serial('COM3', 9600)  # Zameni sa odgovarajućim portom
    arduino_connected = True
except:
    arduino_connected = False

# Inicijalizacija baze podataka
def init_db():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                 id INTEGER PRIMARY KEY,
                 heart_rate INTEGER,
                 gsr REAL,
                 comment TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patients')
    patients = c.fetchall()
    conn.close()
    return render_template('index.html', patients=patients)

@app.route('/add', methods=['POST'])
def add():
    heart_rate = request.form['heart_rate']
    gsr = request.form['gsr']
    comment = request.form['comment']

    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('INSERT INTO patients (heart_rate, gsr, comment) VALUES (?, ?, ?)', (heart_rate, gsr, comment))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Funkcija za simulaciju čitanja sa senzora
def simulate_sensor_data():
    heart_rate = random.randint(90, 120)
    gsr = random.uniform(10, 100)
    return heart_rate, gsr

# Funkcija za čitanje podataka sa Arduina
def read_arduino_data():
    try:
        line = ser.readline().decode('utf-8').strip()
        heart_rate, gsr = map(float, line.split(','))
        return heart_rate, gsr
    except:
        return None, None

@app.route('/simulate')
def simulate():
    heart_rate, gsr = simulate_sensor_data()
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('INSERT INTO patients (heart_rate, gsr) VALUES (?, ?)', (heart_rate, gsr))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/arduino')
def arduino():
    if arduino_connected:
        heart_rate, gsr = read_arduino_data()
        if heart_rate is not None and gsr is not None:
            conn = sqlite3.connect('patients.db')
            c = conn.cursor()
            c.execute('INSERT INTO patients (heart_rate, gsr) VALUES (?, ?)', (heart_rate, gsr))
            conn.commit()
            conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
