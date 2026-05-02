from flask import Flask, render_template, request
import os
import whisper
from models import db, Candidate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Hemapavan182%40@localhost/skillfit'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize DB
db.init_app(app)

with app.app_context():
    db.create_all()

# Load Whisper model once
model = whisper.load_model("base")

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['video']

    # ✅ use webm (important)
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'video.webm')
    file.save(path)

    # Convert to text
    text = convert_to_text(path)

    # Evaluate
    skill, confidence = evaluate(text)

    # Save to DB
    new_data = Candidate(
        name="User",
        transcript=text,
        skill_score=skill,
        confidence_score=confidence
    )

    db.session.add(new_data)
    db.session.commit()

    return "Saved"

# Convert video to text
def convert_to_text(video_path):
    result = model.transcribe(video_path)
    return result["text"]

# Simple scoring
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

# Results page
@app.route('/results')
def results():
    data = Candidate.query.all()
    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)