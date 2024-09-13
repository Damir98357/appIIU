from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import string
import serial
from datetime import datetime

app = Flask(__name__)

@app.route('/index')
def index():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT health_card_id, first_name, last_name FROM pacijenti')
    patients = c.fetchall()
    conn.close()
    return render_template('index.html', patients=patients)


@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        health_card_id = request.form['health_card_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('''INSERT INTO pacijenti (health_card_id, first_name, last_name) 
                     VALUES (?, ?, ?)''',
                  (health_card_id, first_name, last_name))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/add_patient_data', methods=['GET', 'POST'])
def add_patient_data():
    if request.method == 'POST':
        health_card_id = request.form['health_card_id']
        heart_rate = request.form['heart_rate']
        gsr = request.form['gsr']
        datetime = request.form['datetime']
        comment = request.form['comment']

        # Unos podataka u pacijent_podaci tabelu
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('''INSERT INTO pacijent_podaci 
                     (health_card_id, heart_rate, gsr, datetime, comment) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (health_card_id, heart_rate, gsr, datetime, comment))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Selektovanje svih pacijenata za dropdown
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT health_card_id, first_name, last_name FROM pacijenti')
    patients = c.fetchall()
    conn.close()

    return render_template('add_patient_data.html', patients=patients)


@app.route('/pacijenti_detalji/<int:patient_id>', methods=['GET'])
def patient_data(patient_id):
    # Povezivanje sa bazom
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()

    # Dohvatanje pacijenta iz tabele pacijenti
    c.execute('SELECT first_name, last_name FROM pacijenti WHERE health_card_id = ?', (patient_id,))
    patient = c.fetchone()

    # Dohvatanje podataka iz tabele pacijent_podaci
    c.execute('SELECT heart_rate, gsr, datetime, comment FROM pacijent_podaci WHERE health_card_id = ?', (patient_id,))
    patient_data = c.fetchall()

    conn.close()

    # Proveri da li pacijent postoji
    if patient is None:
        return "Pacijent nije pronađen", 404

    # Prikaz stranice sa podacima o pacijentu
    return render_template('pacijenti_detalji.html', patient=patient, patient_data=patient_data)



if __name__ == '__main__':
    
    app.run(debug=True)
