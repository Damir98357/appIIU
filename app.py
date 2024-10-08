from flask import Flask, render_template, request, redirect, url_for ,jsonify
import sqlite3
import random
import string
import serial
from datetime import datetime,timedelta

app = Flask(__name__)

@app.route('/')
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

from datetime import datetime

@app.route('/add_patient_data', methods=['GET', 'POST'])
def add_patient_data():
    if request.method == 'POST':
        health_card_id = request.form['health_card_id']
        heart_rate = request.form['heart_rate']
        gsr = request.form['gsr']
        datetime_str = request.form['datetime']
        comment = request.form['comment']

        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

       
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('''INSERT INTO pacijent_podaci 
                     (health_card_id, heart_rate, gsr, datetime, comment) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (health_card_id, heart_rate, gsr, formatted_datetime, comment))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))


    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT health_card_id, first_name, last_name FROM pacijenti')
    patients = c.fetchall()
    conn.close()

    return render_template('add_patient_data.html', patients=patients)

@app.route('/pacijenti_detalji/<int:health_card_id>')
def pacijenti_detalji(health_card_id):
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    
    
    c.execute('SELECT first_name, last_name FROM pacijenti WHERE health_card_id = ?', (health_card_id,))
    patient = c.fetchone()
    
   
    c.execute('SELECT heart_rate, gsr, datetime, comment FROM pacijent_podaci WHERE health_card_id = ?', (health_card_id,))
    patient_data = c.fetchall()
    
    conn.close()
    
    return render_template('pacijenti_detalji.html', patient=patient, patient_data=patient_data, health_card_id=health_card_id)


@app.route('/get_patient_data/<int:health_card_id>')
def get_patient_data(health_card_id):
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    
    
    c.execute('SELECT heart_rate, gsr, datetime FROM pacijent_podaci WHERE health_card_id = ? ORDER BY datetime ASC', (health_card_id,))
    patient_data = c.fetchall()
    conn.close()

    
    data = {
        'heart_rate': [row[0] for row in patient_data],
        'gsr': [row[1] for row in patient_data],
        'datetime': [row[2] for row in patient_data]
    }
    
    return jsonify(data)



@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        health_card_id = request.form['health_card_id']

       
        num_records = 4  
        now = datetime.now()

        conn = sqlite3.connect('patients.db')
        c = conn.cursor()

        for _ in range(num_records):
            heart_rate = random.randint(60, 100) 
            gsr = random.randint(1,100)  
            date_time = now - timedelta(days=random.randint(1, 30)) 
            comment = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  

            c.execute('''INSERT INTO pacijent_podaci 
                         (health_card_id, heart_rate, gsr, datetime, comment) 
                         VALUES (?, ?, ?, ?, ?)''',
                      (health_card_id, heart_rate, gsr, date_time.strftime('%Y-%m-%d %H:%M:%S'), comment))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT health_card_id, first_name, last_name FROM pacijenti')
    patients = c.fetchall()
    conn.close()

    return render_template('simulate.html', patients=patients)


if __name__ == '__main__':
    
    app.run(debug=True)
