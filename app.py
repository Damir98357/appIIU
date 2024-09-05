from flask import Flask, render_template, request, redirect, url_for
import random
import sqlite3

app = Flask(__name__)

# Postavite serijski port za Arduino (zameni 'COM3' sa odgovarajućim portom)
try:
    import serial
    ser = serial.Serial('COM3', 9600)  # Zameni sa odgovarajućim portom
    arduino_connected = True
except Exception as e:
    print(f"Arduino connection error: {e}")
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

# Stranica za dodavanje novih pacijenata koja takođe prikazuje trenutne pacijente
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        heart_rate = request.form['heart_rate']
        gsr = request.form['gsr']
        comment = request.form['comment']

        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('INSERT INTO patients (heart_rate, gsr, comment) VALUES (?, ?, ?)', (heart_rate, gsr, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('add'))  # Ostanite na istoj stranici nakon dodavanja pacijenta

    # Prikaz trenutnih pacijenata na stranici za dodavanje
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patients')
    patients = c.fetchall()
    conn.close()
    return render_template('add.html', patients=patients)

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        heart_rate = random.randint(90, 120)
        gsr = random.uniform(10, 100)
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('INSERT INTO patients (heart_rate, gsr) VALUES (?, ?)', (heart_rate, gsr))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('simulate.html')

@app.route('/arduino', methods=['GET', 'POST'])
def arduino():
    if request.method == 'POST':
        try:
            line = ser.readline().decode('utf-8').strip()
            heart_rate, gsr = map(float, line.split(','))
        except:
            heart_rate, gsr = None, None
        
        if heart_rate is not None and gsr is not None:
            conn = sqlite3.connect('patients.db')
            c = conn.cursor()
            c.execute('INSERT INTO patients (heart_rate, gsr) VALUES (?, ?)', (heart_rate, gsr))
            conn.commit()
            conn.close()
        return redirect(url_for('index'))
    
    return render_template('arduino.html')



@app.route('/delete/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    try:
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
        conn.commit()
        conn.close()
        return '', 204  # Return status 204 No Content as there's no response body
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return '', 500  # Return status 500 Internal Server Error in case of any error


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
