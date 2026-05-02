from flask import Flask, render_template, request
import os
from models import db, Candidate

app = Flask(__name__)

# ✅ PostgreSQL (Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://aiskillfit_user:lP8AMeSqL7eEdOmJcs57uoLGWWlOx1hY@dpg-d7r39jcm0tmc7382ni50-a.oregon-postgres.render.com/aiskillfit"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize DB
db.init_app(app)

# ❌ DO NOT use db.create_all() directly on Render startup
# safer way:
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("DB init skipped:", e)

# ❌ REMOVE whisper load at startup (causes memory crash)
model = None

# Try loading whisper only when needed
def load_model():
    global model
    if model is None:
        import whisper
        model = whisper.load_model("tiny")  # ✅ lighter model for Render
    return model


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['video']

    path = os.path.join(app.config['UPLOAD_FOLDER'], "video.webm")
    file.save(path)

    # Load whisper only here
    m = load_model()
    text = m.transcribe(path)["text"]

    skill, confidence = evaluate(text)

    new_data = Candidate(
        name="User",
        transcript=text,
        skill_score=skill,
        confidence_score=confidence
    )

    db.session.add(new_data)
    db.session.commit()

    return "Saved successfully"


def evaluate(text):
    score = 0

    if len(text) > 20:
        score += 5
    if "skill" in text.lower():
        score += 2
    if "experience" in text.lower():
        score += 3

    confidence = min(len(text) / 100, 1.0) * 100
    return score, confidence


@app.route('/results')
def results():
    data = Candidate.query.all()
    return render_template('results.html', data=data)


# ✅ REQUIRED for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)