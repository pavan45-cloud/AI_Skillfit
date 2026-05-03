from flask import Flask, render_template, request, redirect, send_from_directory
import os, random

from models import db, User, Candidate
from flask_login import LoginManager, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ================= DATABASE (POSTGRESQL) =================
db_url = "postgresql://aiskillfit_user:lP8AMeSqL7eEdOmJcs57uoLGWWlOx1hY@dpg-d7r39jcm0tmc7382ni50-a.oregon-postgres.render.com/aiskillfit"

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secret"

db.init_app(app)

# ================= LOGIN =================
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= UPLOAD =================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ================= CREATE TABLES =================
with app.app_context():
    db.create_all()

# ================= HOME =================
@app.route('/')
def index():
    return render_template('index.html')

# ================= SIGNUP =================
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('signup.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)

            # ADMIN
            if user.role == "admin":
                return redirect('/admin')

            # USER → PROFILE CHECK
            if not user.dob or not user.skill:
                return redirect('/profile')

            return redirect('/dashboard')

        return "Invalid login"

    return render_template('login.html')

# ================= PROFILE =================
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':

        # RESUME UPLOAD
        file = request.files.get('resume')
        if file and file.filename != "":
            filename = f"{current_user.id}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.resume = filepath

        # SAVE DETAILS
        current_user.name = request.form['name']
        current_user.phone = request.form['phone']
        current_user.email = request.form['email']
        current_user.dob = request.form['dob']

        current_user.district = request.form['district']
        current_user.state = request.form['state']
        current_user.address = request.form['address']

        current_user.education = request.form['education']
        current_user.field = request.form['field']

        current_user.skill = request.form['skill']
        current_user.experience = request.form['experience']

        current_user.language = request.form['language']

        db.session.commit()
        return redirect('/dashboard')

    return render_template('profile.html')

# ================= USER DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    data = Candidate.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', data=data)

# ================= ADMIN DASHBOARD =================
@app.route('/admin')
@login_required
def admin():
    if current_user.role != "admin":
        return "Access denied"

    skill = request.args.get('skill')
    trust = request.args.get('trust')

    query = Candidate.query

    if skill:
        query = query.filter(Candidate.skill_score >= int(skill))

    if trust:
        query = query.filter(Candidate.trust_score >= int(trust))

    data = query.all()
    users = User.query.all()

    return render_template('admin.html', data=data, users=users)

# ================= VIDEO UPLOAD =================
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['video']

    filename = f"{current_user.id}_{random.randint(1000,9999)}.webm"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    # AI SIMULATION
    text = "Candidate speaks about technical skills"

    skill = random.randint(4, 10)
    confidence = random.randint(50, 95)
    trust = random.randint(60, 100)

    if skill >= 8 and confidence >= 75 and trust >= 75:
        status = "Job Ready"
        rec = "Eligible for job"
    elif skill >= 5:
        status = "Needs Training"
        rec = "Recommended ITI training"
    else:
        status = "Manual Review"
        rec = "Needs verification"

    new = Candidate(
        user_id=current_user.id,
        name=current_user.name,
        transcript=text,
        skill_score=skill,
        confidence_score=confidence,
        trust_score=trust,
        status=status,
        recommendation=rec
    )

    db.session.add(new)
    db.session.commit()

    return redirect('/results')

# ================= RESULTS =================
@app.route('/results')
@login_required
def results():
    data = Candidate.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', data=data)

# ================= SERVE RESUME =================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)