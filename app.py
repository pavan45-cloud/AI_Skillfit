from flask import Flask, render_template, request, redirect
import os

from models import db, Candidate, User

from flask_login import LoginManager, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# =========================
# DATABASE CONFIG
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://aiskillfit_user:lP8AMeSqL7eEdOmJcs57uoLGWWlOx1hY@dpg-d7r39jcm0tmc7382ni50-a.oregon-postgres.render.com/aiskillfit"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secretkey"

db.init_app(app)

# =========================
# LOGIN MANAGER
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =========================
# UPLOAD FOLDER
# =========================
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# CREATE TABLES
# =========================
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("DB error:", e)

# =========================
# WHISPER MODEL (LAZY LOAD)
# =========================
# model = None

# def load_model():
#     global model
#     if model is None:
#         import whisper
#         model = whisper.load_model("tiny")
#     return model

# =========================
# HOME PAGE (ONLY ONE ROUTE)
# =========================
@app.route('/')
def index():
    return render_template('index.html')

# =========================
# SIGNUP
# =========================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            password=generate_password_hash(request.form['password']),
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('signup.html')

# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)

            if user.role == "admin":
                return redirect('/admin')
            else:
                return redirect('/dashboard')

        return "Invalid login credentials"

    return render_template('login.html')

# =========================
# USER DASHBOARD
# =========================
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != "user":
        return "Access denied"

    data = Candidate.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', data=data)

# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin')
@login_required
def admin():
    if current_user.role != "admin":
        return "Access denied"

    users = User.query.all()
    data = Candidate.query.all()

    return render_template('admin.html', users=users, data=data)

# =========================
# UPLOAD VIDEO
# =========================
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['video']

    path = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}.webm")
    file.save(path)

    m = load_model()
    text = m.transcribe(path)["text"]

    skill = 5
    confidence = min(len(text) / 100, 100)

    new_data = Candidate(
        user_id=current_user.id,
        name=current_user.name,
        transcript=text,
        skill_score=skill,
        confidence_score=confidence
    )

    db.session.add(new_data)
    db.session.commit()

    return redirect('/dashboard')

# =========================
# RESULTS PAGE
# =========================
@app.route('/results')
@login_required
def results():
    data = Candidate.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', data=data)

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)