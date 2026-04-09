HireSense is an AI-powered platform that analyzes, scores, and auto-tailors resumes against job descriptions to maximize ATS success.
Optimize your job hunt with real-time AI feedback, semantic alignment insights, and one-click tailored PDF exports.

---

## 📸 Screenshots

### Dashboard / Resume Analyzer
![Dashboard / Analyzer Placeholder](assets/dashboard.png)

### User Authentication / Login
![Login & Registration](assets/login.png)
---

## ✨ Features

- **Smart ATS Scoring:** Extracts text from PDF or raw input and evaluates it against target job descriptions.
- **Auto-Tailoring:** Uses advanced LLMs via OpenRouter to intelligently recommend and rewrite resume bullets.
- **Detailed Actionable Feedback:** Provides insights into missing keywords, tone improvements, and formatting suggestions.
- **User Authentication:** Secure access utilizing both Email/Password (Flask-Login) and Google OAuth integrations.
- **History Tracking:** Securely logs your previous analyses, job listings, and generated resume templates in a local SQLite database for easy access.

## 🛠 Tech Stack

- **Backend:** Python, Flask, Flask-Login, Authlib
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Premium, Minimalist "Vibe-coded" Aesthetic)
- **AI Integration:** OpenRouter API (Accessing various frontier LLM models)

## 🚀 Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Amanshukla124/HireSense.git
   cd HireSense
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the Environment Variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *Make sure you provide your `OPENROUTER_API_KEY` and Google OAuth credentials in `.env`.*

4. **Run the Application:**
   ```bash
   python app.py
   ```
   The app will automatically initialize the local `schema.sql` database on its first run.

5. **Visit the app:**  
   Open your browser and navigate to `http://127.0.0.1:5001`.
