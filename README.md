# 🧬 Medicare AI: Autonomous Healthcare & Telemedicine System

## 📌 Project Overview
**Medicare AI** is a next-generation healthcare platform designed to bridge the gap between patients and medical professionals. Unlike standard telemedicine apps, it utilizes **Agentic AI** to autonomously quantify health, analyze medical reports, and detect emotional states before a doctor even steps in.

The system operates on a dual-interface architecture:
* **For Patients:** An intelligent health companion that calculates a real-time **Health Score**, scans facial emotions for mental health screening, and provides instant symptom analysis.
* **For Doctors:** A clinical dashboard to monitor patient logs, manage the drug database, and conduct secure, low-latency **Video Consultations**.

---

## 🚀 Key Features

### 🏥 Patient Modules
* **🧠 Agentic AI Health Score:** A logic-driven inference engine that calculates a dynamic health score (0-100) based on diet, smoking habits, BMI, and location.
* **📹 Secure Video Consultation:** Real-time, high-definition video calls powered by **Agora.io** (Low Latency SD-RTN).
* **😊 AI Emotion Detection:** Uses **face-api.js (TensorFlow.js)** to scan facial micro-expressions via webcam and assess mental well-being.
* **💊 Smart Drug Database:** Search, filter, and compare medications with real-time safety information and ratings.
* **📝 Longitudinal Health Log:** Track daily food intake, medicines, and physical activity to build a comprehensive history for the doctor.
* **🚨 Emergency Support:** One-click access to critical support hotlines and first-aid protocols.

### 👨‍⚕️ Doctor Modules
* **📊 Clinical Dashboard:** A centralized view of patient history, daily logs, and AI-generated risk alerts.
* **📞 Telemedicine Portal:** Initiate secure video calls directly from the patient list with a single click.
* **📂 Patient Management:** Review and respond to asynchronous medical queries ("Ask a Doctor").
* **🧪 Lab Report Analyzer:** (Prototype) OCR-based module to parse uploaded medical reports for key biomarkers.

---

## 🛠️ Tech Stack

### Backend
* **Language:** Python 3.x
* **Framework:** Flask (Micro-framework)
* **Database:** SQLite (Relational DB for Users/Logs)
* **Real-Time Engine:** Flask-SocketIO

### Frontend
* **UI/UX:** HTML5, CSS3 (Glassmorphism Design), Bootstrap 5
* **Scripting:** JavaScript (ES6+)
* **AI Engine:** TensorFlow.js (Client-side Emotion Detection)

### External APIs
* **Video Streaming:** **Agora.io** (App ID Authentication)
* **AI Logic:** Custom Rule-Based Expert System (Agentic Brain)

---

## 📂 Project Structure

```text
Medicare-AI/
├── app.py                  # 🚀 Main Application Controller (Run this!)
├── agent_brain.py          # 🧠 AI Logic Module for Health Scoring
├── medical_app_v2.db       # 🗄️ SQLite Database (Auto-generated)
├── req.txt                 # 📦 Python Dependencies List
├── drugs.json              # 💊 Static Drug Database
├── data/
│   └── medical_data.json   # 🏥 Dataset for Symptom Checker
├── templates/              # 🎨 HTML Frontend Files
│   ├── dashboard.html
│   ├── video_consult.html  # Agora Video Interface
│   ├── drugs_database.html # Updated Drug List
│   └── ...
└── static/                 # 🖼️ CSS, Images, and JS assets
    ├── css/
    ├── js/
    └── uploads/
⚙️ Installation & Setup Guide
Follow these steps to get the project running on your local machine.

1.Prerequisites
Python (Version 3.8 or higher)

Git (To clone the repository)

A working Webcam (For Emotion AI and Video Calls)

2.Clone the Repository
Open your terminal or command prompt and run:

git clone [https://github.com/YourUsername/Medicare-AI.git](https://github.com/YourUsername/Medicare-AI.git)
cd Medicare-AI

3. Create a Virtual Environment (Optional but Recommended)

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
Note: The requirements file is named req.txt

pip install -r req.txt

5. Initialize the Database
The system features Auto-Migration. You do not need to create the database manually. Simply running the app for the first time will create medical_app_v2.db and all necessary tables (users, daily_checkins, log_suggestions, etc)

6. Run the Application

python app.py

7. Access the App
Open your web browser (Chrome/Edge recommended) and navigate to: 👉 http://127.0.0.1:5000/

🧪 Demo AccountsThe system auto-generates these credentials on the first run for testing purposes:RoleUsernamePassword
👨‍⚕️ Doctordemo_doctordemo123
👤 Patientdemo_patientdemo123

🔮 Future Enhancements:


🔗 Blockchain Integration: To store immutable Electronic Health Records (EHR) for maximum privacy.
⌚ Wearable Sync: Integration with Fitbit/Apple Watch APIs to fetch real-time heart rate and sleep data.
🤖 LLM Chatbot: Replacing the rule-based chat with a fine-tuned Llama-3 model for complex medical Q&A.
📱 Mobile App: Developing a React Native version for iOS and Android.

📜 License & Disclaimer
This project is a final-year engineering prototype developed for educational purposes. The medical recommendations provided by the AI models are for demonstration only and should not replace professional medical advice.

Developed with ❤️ by Dhanush.R