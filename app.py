import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# SECURITY: Get from Render, fallback to a dummy string for local testing only
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'local-secret-key-only')

# CORS Configuration
CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://rubberbang.github.io",
    "https://ahmkoor.com",
    "https://www.ahmkoor.com"
])

# DATABASE CONFIG
db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Fix for Render providing 'postgres://' instead of 'postgresql://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///choir.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cayatapapia@gmail.com'
# SECURITY: This is now pulled safely from Render settings
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# SECURITY: Get the hash from Render
# If Render environment variable is missing, it uses a dummy hash that won't work
ADMIN_HASH = os.environ.get('ADMIN_HASH', 'no-hash-provided')

# --- MODELS ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    is_canceled = db.Column(db.Boolean, default=False)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    company = db.Column(db.String(100))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

# --- SECURITY DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---

@app.route('/')
def health_check():
    return "AHM Backend is Running Successfully!"

@app.route('/api/login', methods=['POST'], strict_slashes=False)
def login():
    data = request.json
    if ADMIN_HASH != 'no-hash-provided' and check_password_hash(ADMIN_HASH, data.get('password')):
        return jsonify({"status": "success", "token": "ahm_aruba_2024"})
    return jsonify({"status": "error"}), 401

@app.route('/api/events', methods=['GET'], strict_slashes=False)
def get_events():
    today = datetime.now().strftime('%Y-%m-%d')
    events = Event.query.filter(Event.date >= today).order_by(Event.date.asc()).all()
    return jsonify([{
        'id': e.id, 'title': e.title, 'location': e.location, 'date': e.date,
        'time': e.time, 'description': e.description, 'type': e.type,
        'is_canceled': e.is_canceled
    } for e in events])

@app.route('/api/admin/all-events', methods=['GET'], strict_slashes=False)
@login_required
def get_all_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return jsonify([{
        'id':e.id, 'title':e.title, 'location':e.location, 'date':e.date,
        'time':e.time, 'is_canceled':e.is_canceled
    } for e in events])

@app.route('/api/admin/events', methods=['POST'], strict_slashes=False)
@login_required
def add_event():
    data = request.json
    new_event = Event(title=data['title'], location=data['location'], date=data['date'],
                      time=data['time'], description=data['description'], type=data['type'])
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/events/<int:id>', methods=['DELETE', 'PUT'], strict_slashes=False)
@login_required
def manage_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(event)
    elif request.method == 'PUT':
        data = request.json
        event.is_canceled = data.get('is_canceled', event.is_canceled)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/messages', methods=['GET'], strict_slashes=False)
@login_required
def get_messages():
    msgs = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()
    return jsonify([{'id': m.id, 'name': m.name, 'email': m.email, 'company': m.company, 'message': m.message} for m in msgs])

@app.route('/api/admin/messages/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_message(id):
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/contact', methods=['POST'], strict_slashes=False)
def contact():
    data = request.json
    try:
        # 1. Save to Database
        new_msg = ContactMessage(
            name=data['name'],
            email=data['email'],
            company=data.get('company', ''),
            message=data['message']
        )
        db.session.add(new_msg)
        db.session.commit()

        # 2. Attempt to send email quietly
        try:
            # Only attempt if password is provided in environment
            if app.config['MAIL_PASSWORD']:
                msg = Message(
                    subject=f"AHM Website: {data['name']}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=['cayatapapia@gmail.com'],
                    body=f"Name: {data['name']}\nEmail: {data['email']}\nCompany: {data.get('company', 'N/A')}\n\nMessage:\n{data['message']}"
                )
                mail.send(msg)
                print("Email sent successfully!")
        except Exception as mail_err:
            print(f"Email failed but message saved to DB: {mail_err}")

        return jsonify({"status": "success", "message": "Mensahe a drenta"}), 200

    except Exception as db_err:
        print(f"Critical Database Error: {db_err}")
        return jsonify({"status": "error", "message": "Server Error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)