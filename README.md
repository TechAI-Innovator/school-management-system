# 🎓 School Management System with LLM Voice Integration

A web-based School Management System designed to manage student records, process results, and generate reports. It also features **voice-enabled automation using Large Language Models (LLMs)** for easy interaction.

## 📸 Screenshots

- ![Login Page](images/login_screenshot.png)
- ![Dashboard](images/dashboard_screenshot.png)
- ![Score Entry](images/score_entry.png)
- ![Report Output](images/report.png)

---

## 🎥 Demo Video

> _A short walkthrough video will be available soon._

[![Watch Demo](https://img.youtube.com/vi/your_video_id_here/0.jpg)](https://www.youtube.com/watch?v=your_video_id_here)

---

## 🚀 Features

- 🔐 **Role-Based Login System**
  - 👨‍🎓 **Students** – View personal records and reports only
  - 👩‍🏫 **Staff** – Enter student scores and access assigned classes
  - 🧑‍💼 **Admins** – Full access to manage students, staff, and generate reports
- 📝 **Score Entry & Auto Calculations** – Teachers/staff can enter scores; the system automatically calculates totals, grades, and positions.
- 📊 **Report Generation** – Export student reports in Excel format using a pre-defined template.
- 🎤 **Voice Assistant (LLM-Integrated)** – Use voice commands to trigger actions like checking results or generating reports.
- 💬 **Real-time Speech Recognition** – Converts voice to text for LLM-based interpretation.

---

## 🧠 Tech Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: MySQL, SQLite  
- **Voice & AI**: Web Speech API + LLM (e.g., GPT)  
- **Deployment**: Vercel + PythonAnywhere  

---

## 🗂️ Project Structure

├── app.py # Main Flask app
├── engine.py # Core database and logic functions
├── init_db.py # Initializes the database
├── schema.sql # SQL file for table setup
├── school_system.db # SQLite database
├── voice_handler.py # Voice processing logic
├── requirements.txt # Project dependencies
├── static/ # Static files (e.g., Excel template)
├── templates/ # HTML pages
├── vercel.json # Vercel configuration
└── LICENSE # License file
