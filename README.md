📅 Agentic AI – Smart Timetable & Event Scheduler

An AI-powered productivity system that intelligently manages schedules, events, assignments, and goals using automation, AI assistance, and Google Calendar integration.

🚀 Overview

Agentic AI – Smart Timetable & Event Scheduler is a full-stack AI productivity assistant designed to help users organize their daily life efficiently. It automates scheduling decisions, tracks tasks, and provides insights to improve productivity.

It integrates AI logic + Google Calendar + smart dashboard analytics into one seamless system.

✨ Key Features
🧠 AI Scheduling Assistant
Automatically suggests optimal time slots for tasks
Helps reduce scheduling conflicts
Intelligent prioritization of events and goals
📅 Event Management
Create, update, and delete events
Sync with Google Calendar
Organized daily/weekly/monthly views
🎯 Goals & Assignments Tracker
Track academic or personal goals
Break tasks into manageable steps
Monitor completion status
🔔 Smart Notifications
Reminders for upcoming events
Deadline alerts for assignments
Daily motivational prompts
📊 Analytics Dashboard
Productivity tracking
Task completion insights
Visual performance summary
🔐 Secure Authentication
Login / Signup system
Google OAuth integration
Session-based access control
🛠️ Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	Python
AI Engine	Agentic AI / Groq API
Authentication	Google OAuth 2.0
Calendar API	Google Calendar API
Storage	Local / Database (optional)
📁 Project Structure
Agentic-AI-FINAL/
│
├── app.py                  # Main application entry point
├── auth.py                 # User authentication system
├── calender_connection.py  # Google Calendar integration
├── requirements.txt        # Project dependencies
├── .gitignore              # Ignored files & secrets
├── README.md               # Project documentation
│
├── pages/
│   ├── dashboard.py
│   ├── events.py
│   ├── goals.py
│   ├── settings.py
│
├── utils/
│   ├── ai_scheduler.py
│   ├── notifications.py
│
└── assets/
    └── images/
⚙️ Installation Guide
1️⃣ Clone the Repository
git clone https://github.com/EADALARAMYA31/AGENTIC-AI-FINAL.git
cd AGENTIC-AI-FINAL
2️⃣ Create Virtual Environment
python -m venv venv
3️⃣ Activate Environment

Windows:

venv\Scripts\activate
4️⃣ Install Dependencies
pip install -r requirements.txt
5️⃣ Run Application
streamlit run app.py
🔐 Google OAuth Setup

To enable calendar integration:

Create a project in Google Cloud Console
Enable Google Calendar API
Create OAuth credentials
Download client_secret.json

Add redirect URI:

http://localhost:8501
Keep credentials secure (DO NOT upload to GitHub)
🚫 Security Rules (Important)

Never push the following:

token_1.pickle
client_secret.json
.env
Any API keys or secrets

These are already protected using .gitignore.

📈 Future Enhancements
🤖 Advanced AI-based timetable optimization engine
📱 Mobile-friendly responsive UI
🔔 Push notification system (browser/mobile)
🌐 Cloud deployment (Streamlit Cloud / AWS / Render)
📊 Advanced analytics with graphs & insights
🧩 Multi-user collaboration system
