import os
import threading # NEW: Needed for background emails
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime
from werkzeug.security import check_password_hash
from sqlalchemy import text

app = Flask(__name__)

# --- CONFIGURATION ---

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'local-secret-key-only')

# CORS: Allow all origins
CORS(app, supports_credentials=True, origins=["*"])

# DATABASE
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///choir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465             # CHANGED: 587 -> 465
app.config['MAIL_USE_TLS'] = False        # CHANGED: True -> False
app.config['MAIL_USE_SSL'] = True         # CHANGED: False -> True
app.config['MAIL_USERNAME'] = 'cayatapapia@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'cayatapapia@gmail.com'

mail = Mail(app)

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

class SiteContent(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)

class NewsPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20))
    content = db.Column(db.Text)
    image = db.Column(db.Text)

with app.app_context():
    db.create_all()

# --- HELPER FUNCTIONS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ EMAIL SUCCESS: Sent to {msg.recipients}", flush=True)
        except Exception as e:
            # This will print the exact error from Google to your Render logs
            print(f"❌ EMAIL FAILED: {str(e)}", flush=True)

# --- ROUTES ---

@app.route('/')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return "AHM Backend Active & DB Connected."
    except Exception as e:
        return f"DB Error: {str(e)}"

@app.route('/api/login', methods=['POST'], strict_slashes=False)
def login():
    data = request.json
    if ADMIN_HASH != 'no-hash-provided' and check_password_hash(ADMIN_HASH, data.get('password')):
        return jsonify({"status": "success", "token": "ahm_aruba_2024"})
    return jsonify({"status": "error"}), 401

# --- EVENTS ---
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
        'time':e.time, 'description':e.description, 'type':e.type,
        'is_canceled':e.is_canceled
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
        event.title = data.get('title', event.title)
        event.date = data.get('date', event.date)
        event.time = data.get('time', event.time)
        event.location = data.get('location', event.location)
        event.description = data.get('description', event.description)
        event.type = data.get('type', event.type)
        if 'is_canceled' in data:
            event.is_canceled = data['is_canceled']
    db.session.commit()
    return jsonify({"status": "success"})

# --- NEWS ---
@app.route('/api/news', methods=['GET'], strict_slashes=False)
def get_news():
    news = NewsPost.query.order_by(NewsPost.date.desc()).all()
    return jsonify([{
        'id': n.id, 'title': n.title, 'date': n.date,
        'content': n.content, 'image': n.image
    } for n in news])

@app.route('/api/admin/news', methods=['POST'], strict_slashes=False)
@login_required
def add_news():
    data = request.json
    new_post = NewsPost(
        title=data['title'], date=data['date'],
        content=data['content'], image=data.get('image')
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/news/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_news(id):
    post = NewsPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"status": "success"})

# --- SETTINGS ---
@app.route('/api/content', methods=['GET'], strict_slashes=False)
def get_content():
    content = SiteContent.query.all()
    return jsonify({item.key: item.value for item in content})

@app.route('/api/content', methods=['POST'], strict_slashes=False)
@login_required
def save_content():
    data = request.json
    try:
        for key, value in data.items():
            item = SiteContent.query.get(key)
            if item:
                item.value = value
            else:
                new_item = SiteContent(key=key, value=value)
                db.session.add(new_item)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- MESSAGES & CONTACT ---
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
            name=data['name'], email=data['email'],
            company=data.get('company', ''), message=data['message']
        )
        db.session.add(new_msg)
        db.session.commit()

        # 2. Prepare Email
        if app.config['MAIL_PASSWORD']:
            msg = Message(
                subject=f"AHM Website: {data['name']}",
                # IMPORTANT: Sender must match your MAIL_USERNAME exactly
                sender=app.config['MAIL_USERNAME'],
                recipients=['cayatapapia@gmail.com'],
                body=f"Name: {data['name']}\nEmail: {data['email']}\nCompany: {data.get('company', 'N/A')}\n\nMessage:\n{data['message']}"
            )
            # Start background thread
            threading.Thread(target=send_async_email, args=(app, msg)).start()
        else:
            print("⚠️ Email skipped: MAIL_PASSWORD not set in environment.")

        return jsonify({"status": "success", "message": "Mensahe a drenta"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)