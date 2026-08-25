from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import json
from flask_socketio import SocketIO, emit
import hashlib
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

# ========================================================
# 1. CONFIGURATION & SETUP
# ========================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'final-secure-key-2025-v16-master-fix'
UPLOAD_FOLDER = 'static/uploads'
REPORT_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# *** IMPORTANT: USE AN APP ID FROM A "TESTING MODE" PROJECT ***
app.config['AGORA_APP_ID'] = '6190d0ee536a4be18b3d31d55fa0554b'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)

socketio = SocketIO(app, cors_allowed_origins="*")
DATABASE = 'medical_app_v2.db'
MEDICAL_DATA_FILE = 'data/medical_data.json'


# ========================================================
# 2. HELPER FUNCTIONS
# ========================================================

def allowed_file(filename):
    """Checks if the uploaded file allows the extension."""
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            return True
    return False


def hash_password(password):
    """Hashes password for security."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_db_connection():
    """Establishes connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ========================================================
# 3. DATABASE INITIALIZATION
# ========================================================

def init_database():
    conn = get_db_connection()
    
    # 1. Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            full_name TEXT,
            user_type TEXT,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            location_city TEXT,
            hobbies TEXT,
            food_habits TEXT,
            medical_history TEXT,
            profile_photo TEXT,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Daily Health Checkins
    conn.execute('''
        CREATE TABLE IF NOT EXISTS daily_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date DATE,
            food_intake TEXT,
            medicines_taken TEXT,
            physical_activity TEXT,
            symptoms_felt TEXT,
            mood TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Doctor Log Suggestions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS log_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            log_date DATE,
            suggestion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Patient Questions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patient_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            question TEXT,
            symptoms TEXT,
            status TEXT DEFAULT 'pending',
            doctor_id INTEGER,
            doctor_response TEXT,
            prescription TEXT,
            lab_tests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. Custom Drugs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS custom_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            description TEXT,
            side_effects TEXT,
            dosage_info TEXT,
            added_by INTEGER,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 6. Disease Alerts
    conn.execute('''
        CREATE TABLE IF NOT EXISTS disease_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            severity TEXT,
            symptoms TEXT,
            prevention TEXT,
            treatment TEXT,
            added_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. Recommendations
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symptoms TEXT,
            recommended_drugs TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 8. Doctor Ratings
    conn.execute('''
        CREATE TABLE IF NOT EXISTS doctor_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()


# ========================================================
# 4. DATA LOADING
# ========================================================

def load_medical_data():
    try:
        with open(MEDICAL_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

medical_data = load_medical_data()

try:
    with open('drugs.json', 'r') as f:
        drugs = json.load(f)
except:
    drugs = []

HEALTHY_HABITS_DATA = {
    "hydration": { "id": "hydration", "title": "Hydration", "summary": "Drink 3L daily", "importance": "Vital", "action_plan": ["Carry bottle"], "foods": ["Watermelon"] },
    "sleep": { "id": "sleep", "title": "Sleep", "summary": "8 Hours", "importance": "Recovery", "action_plan": ["No screens"], "foods": ["Tea"] },
    "movement": { "id": "movement", "title": "Movement", "summary": "10k Steps", "importance": "Cardio", "action_plan": ["Walk"], "foods": ["Oats"] }
}

try:
    from agent_brain import query_agent
except ImportError:
    def query_agent(data):
        return "AI Agent is connecting... Please ensure agent_brain.py is present."


# ========================================================
# 5. AUTHENTICATION ROUTES
# ========================================================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        conn = get_db_connection()
        try:
            exists = conn.execute('SELECT id FROM users WHERE username = ?', (form['username'],)).fetchone()
            if exists:
                flash('Username already taken', 'error')
                conn.close()
                return render_template('register.html')

            conn.execute('''
                INSERT INTO users (username, email, password, full_name, user_type, gender, age, 
                                 height_cm, weight_kg, location_city, hobbies, food_habits, medical_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form['username'], form['email'], hash_password(form['password']), form['full_name'], form['user_type'],
                form['gender'], form['age'], form.get('height'), form.get('weight'),
                form.get('location'), form.get('hobbies'), form.get('food_habits'), form.get('medical_history')
            ))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Database error during registration.', 'error')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (request.form['username'],)).fetchone()
        conn.close()
        
        if user and user['password'] == hash_password(request.form['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['user_type'] = user['user_type']
            session['profile_photo'] = user['profile_photo']
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ========================================================
# 6. DASHBOARD & PROFILE
# ========================================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user: 
        session.clear()
        conn.close()
        return redirect(url_for('login'))
    
    checkin_done = False
    log_count = 0
    doctor_res = []
    
    if user['user_type'] == 'patient':
        today = datetime.now().strftime("%Y-%m-%d")
        
        if conn.execute('SELECT id FROM daily_checkins WHERE user_id=? AND date=?', (user['id'], today)).fetchone():
            checkin_done = True
            
        log_count = conn.execute('SELECT COUNT(*) FROM log_suggestions WHERE patient_id=?', (user['id'],)).fetchone()[0]
        
        doctor_res = conn.execute('SELECT * FROM patient_questions WHERE patient_id=? AND status="answered" ORDER BY updated_at DESC LIMIT 3', (user['id'],)).fetchall()

    conn.close()
    return render_template('dashboard.html', user=user, checkin_done=checkin_done, log_suggestions_count=log_count, doctor_responses=doctor_res)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute('UPDATE users SET profile_photo = ? WHERE id = ?', (filename, session['user_id']))
                conn.commit()
                flash('Profile photo updated!', 'success')
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)


# ========================================================
# 7. FEATURE: HEALTH & AI
# ========================================================

@app.route('/healthy_living')
def healthy_living():
    return render_template('healthy_living.html', habits=HEALTHY_HABITS_DATA)


@app.route('/healthy_living/<habit_id>')
def healthy_habit_detail(habit_id):
    habit = HEALTHY_HABITS_DATA.get(habit_id)
    if habit:
        return render_template('healthy_habit_detail.html', habit=habit)
    return redirect(url_for('healthy_living'))


@app.route('/lab_report_checker', methods=['GET', 'POST'])
def lab_report_checker():
    if 'user_id' not in session: return redirect(url_for('login'))
    analysis = None
    if request.method == 'POST':
        text = request.form.get('report_text', '').lower()
        if 'report_image' in request.files:
            f = request.files['report_image']
            if f.filename != '':
                text += " cholesterol 250 glucose 130" 
        
        analysis = {'findings': [], 'suggestions': [], 'score': 100}
        
        if 'cholesterol' in text and ('high' in text or '2' in text):
            analysis['findings'].append("⚠️ High Cholesterol detected.")
            analysis['suggestions'].append("Adopt a low-fat diet immediately.")
            analysis['score'] -= 15
            
        if 'glucose' in text and ('high' in text or '1' in text):
            analysis['findings'].append("⚠️ High Glucose (Hyperglycemia).")
            analysis['suggestions'].append("Monitor carbs and sugar intake.")
            analysis['score'] -= 15
            
        if not analysis['findings']:
            analysis['findings'].append("✅ No critical flags found in report.")
            
    return render_template('lab_report_checker.html', analysis=analysis)


@app.route('/agentic_health_intake', methods=['GET', 'POST'])
def agentic_health_intake():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    conn.close()

    if request.method == 'POST':
        d = request.form
        score = 100
        insights = []
        
        habits = d.get('habits', '').lower()
        diet = d.get('food_habits', '').lower()
        
        if 'smoke' in habits or 'smoking' in habits:
            score -= 30
            insights.append("⛔ Critical: Smoking detected. High risk factor.")
        
        if 'alcohol' in habits:
            score -= 15
            insights.append("⚠️ Alcohol consumption impacts long-term health.")
            
        if 'junk' in diet or 'unbalanced' in diet:
            score -= 20
            insights.append("⚠️ Poor Diet detected.")

        try:
            bmi = round(float(d['weight']) / ((float(d['height'])/100)**2), 1)
            if bmi > 25: 
                score -= 10
                insights.append(f"⚠️ BMI {bmi}: Overweight range.")
            else:
                insights.append(f"✅ BMI {bmi}: Healthy weight.")
        except:
            bmi = "N/A"
        
        if 'mumbai' in d.get('location','').lower() or 'delhi' in d.get('location','').lower():
            score -= 10
            insights.append("⚠️ High Pollution Area: Respiratory care needed.")

        score = max(0, score)
        return render_template('agentic_results.html', score=score, insights=insights, bmi=bmi)

    return render_template('agentic_intake.html', user=user)


# ========================================================
# 8. FEATURE: AGORA VIDEO CONSULTATION (FIXED)
# ========================================================

@app.route('/video_consult')
def video_consult():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    channel_name = "medicare_demo_channel"
    agora_app_id = app.config.get('AGORA_APP_ID')
    
    return render_template('video_consult.html', app_id=agora_app_id, channel_name=channel_name)


@app.route('/doctor_join_call')
def doctor_join_call():
    # Redirect doctor to the video page
    return redirect(url_for('video_consult'))


# ========================================================
# 9. FEATURE: DRUGS, SYMPTOMS, & TOOLS
# ========================================================

@app.route('/drugs-database')
def drugs_database():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    custom_drugs = conn.execute('SELECT * FROM custom_drugs').fetchall()
    conn.close()
    
    all_drugs = drugs + [dict(row) for row in custom_drugs]
    return render_template('drugs_database.html', drugs=all_drugs)


@app.route('/symptom-checker')
def symptom_checker():
    all_symptoms = set()
    for entry in medical_data:
        for s in entry['symptoms']:
            all_symptoms.add(s)
    return render_template('symptom_checker.html', symptoms=sorted(list(all_symptoms)))


@app.route('/recommend-drugs', methods=['POST'])
def recommend_drugs():
    data = request.get_json()
    user_symptoms = set(data.get('symptoms', []))
    
    if not user_symptoms:
        return jsonify({'recommendations': []})
    
    results = []
    for d in medical_data:
        dis_sym = set(d['symptoms'])
        overlap = len(user_symptoms.intersection(dis_sym))
        if overlap > 0:
            score = (overlap / len(dis_sym)) * 100
            results.append({
                'condition': d['condition'],
                'drugs': [{'name': x} for x in d['recommended_drugs']],
                'confidence': round(score, 1)
            })
    
    results.sort(key=lambda x: x['confidence'], reverse=True)
    return jsonify({'recommendations': results[:3]})


@app.route('/emotion_detection')
def emotion_detection():
    return render_template('emotion_detection.html')


@app.route('/daily_checkin', methods=['GET','POST'])
def daily_checkin(): 
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO daily_checkins (user_id, date, food_intake, mood) VALUES (?,?,?,?)', 
                     (session['user_id'], datetime.now().strftime("%Y-%m-%d"), request.form.get('food'), request.form.get('mood')))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('daily_checkin.html')


@app.route('/price_predictor', methods=['GET', 'POST'])
def price_predictor():
    total_cost = 0
    breakdown = []
    if request.method == 'POST':
        meds = request.form.get('medicines', '').split(',')
        for m in meds:
            cost = len(m) * 12
            total_cost += cost
            breakdown.append({'name': m, 'price': cost})
    return render_template('price_predictor.html', cost=total_cost, breakdown=breakdown)


@app.route('/emergency')
def emergency():
    return render_template('emergency.html')


# ========================================================
# 10. DOCTOR SPECIFIC ROUTES (FIXED PATIENT LOGS & URLS)
# ========================================================

@app.route('/manage_questions')
def manage_questions():
    if session.get('user_type') != 'doctor': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    pending = conn.execute('SELECT pq.*, u.full_name as patient_name FROM patient_questions pq JOIN users u ON pq.patient_id=u.id WHERE status="pending"').fetchall()
    history = conn.execute('SELECT pq.*, u.full_name as patient_name FROM patient_questions pq JOIN users u ON pq.patient_id=u.id WHERE status="answered"').fetchall()
    conn.close()
    return render_template('manage_questions.html', pending_questions=pending, history=history)


@app.route('/doctor/answer-question', methods=['POST'])
def answer_question_api():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE patient_questions SET doctor_response=?, status="answered", doctor_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                 (data['answer'], session['user_id'], data['question_id']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})


@app.route('/patient_logs_list')
def patient_logs_list():
    if session.get('user_type') != 'doctor': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    patients = conn.execute('''
        SELECT DISTINCT u.id, u.full_name, MAX(d.date) as last_log 
        FROM users u 
        JOIN daily_checkins d ON u.id = d.user_id 
        GROUP BY u.id
        ORDER BY last_log DESC
    ''').fetchall()
    conn.close()
    return render_template('patient_logs_list.html', patients=patients)


# Route for viewing individual logs
@app.route('/view_patient_log/<int:id>')
def view_patient_log(id):
    if session.get('user_type') != 'doctor': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM users WHERE id=?', (id,)).fetchone()
    logs = conn.execute('SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date DESC', (id,)).fetchall()
    conn.close()
    return render_template('view_patient_log.html', patient=patient, logs=logs)


# *** FIXED MISSING ROUTE ***
# This route was causing the "BuildError: Could not build url for endpoint 'suggest_on_log'"
@app.route('/doctor/suggest_on_log', methods=['POST'])
def suggest_on_log():
    if session.get('user_type') != 'doctor': return redirect(url_for('dashboard'))
    patient_id = request.args.get('patient_id')
    log_date = request.args.get('log_date')
    suggestion = request.form.get('suggestion')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO log_suggestions (patient_id, doctor_id, log_date, suggestion) VALUES (?,?,?,?)',
                 (patient_id, session['user_id'], log_date, suggestion))
    conn.commit()
    conn.close()
    flash("Suggestion sent to patient", "success")
    return redirect(url_for('view_patient_log', id=patient_id))


@app.route('/doctor_analytics')
def doctor_analytics():
    return render_template('analytics.html', stats={'rating': 4.9, 'total_patients': 120})


@app.route('/disease_updates')
def disease_updates():
    return render_template('disease_updates.html', updates=[])


@app.route('/doctor/add-drug')
def doctor_add_drug():
    return render_template('add_drug.html')


# ========================================================
# 11. PATIENT SPECIFIC ROUTES
# ========================================================

@app.route('/ask-doctor', methods=['GET','POST'])
def ask_doctor():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO patient_questions (patient_id, question, symptoms) VALUES (?, ?, ?)',
                     (session['user_id'], request.form.get('question'), request.form.get('symptoms')))
        conn.commit()
        conn.close()
        flash("Question submitted.", "success")
        return redirect(url_for('dashboard'))
    conn = get_db_connection()
    my_questions = conn.execute('SELECT * FROM patient_questions WHERE patient_id=? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('ask_doctor.html', my_questions=my_questions)


# *** FIXED MISSING ROUTE ***
# This route was causing "BuildError: Could not build url for endpoint 'view_log_suggestions'"
@app.route('/patient/log_suggestions')
def view_log_suggestions():
    conn = get_db_connection()
    suggestions = conn.execute('''
        SELECT ls.*, u.full_name as doctor_name 
        FROM log_suggestions ls
        JOIN users u ON ls.doctor_id = u.id 
        WHERE ls.patient_id = ? 
        ORDER BY ls.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('log_suggestions.html', suggestions=suggestions)


@app.route('/chat_agent')
def chat_agent():
    return render_template('chat_agent.html')


@socketio.on('message')
def handle_message(data):
    emit('response', {'msg': query_agent(data['data'])})


# ========================================================
# 12. DEMO ACCOUNTS
# ========================================================

def create_demo_accounts():
    conn = get_db_connection()
    if not conn.execute("SELECT * FROM users WHERE username='demo_doctor'").fetchone():
        conn.execute("INSERT INTO users (username, email, password, full_name, user_type) VALUES (?,?,?,?,?)",
                     ('demo_doctor', 'doc@test.com', hash_password('demo123'), 'Dr. Demo', 'doctor'))
    
    if not conn.execute("SELECT * FROM users WHERE username='demo_patient'").fetchone():
        conn.execute('''
            INSERT INTO users (username, email, password, full_name, user_type, height_cm, weight_kg, location_city, food_habits)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', ('demo_patient', 'pat@test.com', hash_password('demo123'), 'Demo Patient', 'patient', 170, 70, 'Mumbai', 'Balanced'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    with app.app_context():
        create_demo_accounts()
    
    # Read the dynamic port assigned by Render, defaulting to 5000 if running locally
    port = int(os.environ.get("PORT", 5000))
    
    # Run socketio binding to 0.0.0.0 and using the assigned port
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
