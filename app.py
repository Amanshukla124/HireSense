from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from config import Config
from core.analyzer import analyze_resume
from core.parser import extract_text_from_pdf
from core.db import init_db, save_analysis, get_analyses_for_user, get_analysis_by_id_for_user, save_tailored_resumes
from core.user import User
from core.tailor import generate_tailored_resumes

app = Flask(__name__)
app.config.from_object(Config)

# ── Flask-Login ──────────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# ── Google OAuth (Authlib) ───────────────────────────────────────────────────
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# ── DB init ──────────────────────────────────────────────────────────────────
with app.app_context():
    init_db()

# ── Main routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
@login_required
def history():
    past_analyses = get_analyses_for_user(current_user.id)
    return render_template('history.html', analyses=past_analyses)

@app.route('/history/<int:analysis_id>')
@login_required
def history_detail(analysis_id):
    analysis = get_analysis_by_id_for_user(analysis_id, current_user.id)
    if not analysis:
        abort(404)
    return render_template('detailed_history.html', analysis=analysis)

# ── Email / Password Auth ─────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email      = request.form.get('email', '').strip().lower()
        password   = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return redirect(url_for('signup'))

        try:
            user = User.create_with_password(email, password, first_name, last_name)
            login_user(user, remember=True)
            flash(f'Welcome, {user.display_name}! Your account has been created.', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ── Google OAuth routes ───────────────────────────────────────────────────────
@app.route('/auth/google')
def auth_google():
    redirect_uri = app.config['GOOGLE_REDIRECT_URI']
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def auth_google_callback():
    try:
        token     = google.authorize_access_token()
        userinfo  = token.get('userinfo') or google.userinfo()

        google_id  = userinfo.get('sub')
        email      = userinfo.get('email', '').lower()
        first_name = userinfo.get('given_name', '')
        last_name  = userinfo.get('family_name', '')
        avatar_url = userinfo.get('picture', '')

        if not email or not google_id:
            flash('Could not retrieve your Google account details. Please try again.', 'error')
            return redirect(url_for('login'))

        user = User.create_or_update_from_google(google_id, email, first_name, last_name, avatar_url)
        login_user(user, remember=True)
        flash(f'Welcome, {user.display_name}!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'error')
        return redirect(url_for('login'))


# ── Analyze API ───────────────────────────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():
    job_desc    = ''
    resume_text = ''
    target_role = ''

    if request.content_type and 'multipart/form-data' in request.content_type:
        job_desc    = request.form.get('job_desc', '').strip()
        resume_file = request.files.get('resume_file')

        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file.stream)
            if not resume_text:
                return jsonify({"error": "Could not extract text from the uploaded PDF. Try pasting the text instead."}), 400
        else:
            resume_text = request.form.get('resume', '').strip()

        target_role = request.form.get('target_role', '').strip()
    else:
        data        = request.json or {}
        resume_text = data.get('resume', '').strip()
        job_desc    = data.get('job_desc', '').strip()
        target_role = data.get('target_role', '').strip()

    if not resume_text or not job_desc:
        return jsonify({"error": "Resume and Job Description are required."}), 400

    result = analyze_resume(
        resume_text, job_desc,
        app.config['OPENROUTER_API_KEY'],
        app.config['OPENROUTER_MODEL'],
        target_role
    )

    if "error" not in result or result.get("score") is not None:
        user_id = current_user.id if current_user.is_authenticated else None
        analysis_id = save_analysis(job_desc, resume_text, result, target_role, user_id=user_id)
        result["analysis_id"] = analysis_id

    return jsonify(result)


@app.route('/api/tailor', methods=['POST'])
def tailor_resume():
    if not current_user.is_authenticated:
        return jsonify({"error": "You must be logged in to use Auto-Tailor."}), 401

    data = request.json or {}
    analysis_id = data.get('analysis_id')

    if not analysis_id:
        return jsonify({"error": "Analysis ID is required."}), 400

    analysis = get_analysis_by_id_for_user(analysis_id, current_user.id)
    if not analysis:
        return jsonify({"error": "Analysis not found or permission denied."}), 404

    # Generate tailored options
    options = generate_tailored_resumes(
        analysis['resume'],
        analysis['job_desc'],
        app.config['OPENROUTER_API_KEY'],
        app.config['OPENROUTER_MODEL'],
        analysis['target_role']
    )

    if "error" not in options:
        save_tailored_resumes(analysis_id, options)

    return jsonify(options)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
