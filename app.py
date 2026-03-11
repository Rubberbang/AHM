import os
import threading
import json
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime
from werkzeug.security import check_password_hash

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'local-secret-key-only')
CORS(app, supports_credentials=True, origins=["*"])

GOOGLE_SCRIPT_URL = os.environ.get('GOOGLE_SCRIPT_URL')
ADMIN_HASH = os.environ.get('ADMIN_HASH', 'no-hash-provided')

# --- JSON DATABASE SETUP ---
DB_DIR = 'Database'
os.makedirs(DB_DIR, exist_ok=True)  # Creates the folder if it doesn't exist
db_lock = threading.Lock()  # Prevents file corruption if 2 users save at exactly the same time


def get_file_path(table_name):
    return os.path.join(DB_DIR, f"{table_name}.json")


def read_table(table_name):
    """Reads a JSON file and returns it as a list of dictionaries."""
    path = get_file_path(table_name)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_table(table_name, data):
    """Writes a list of dictionaries back to a JSON file."""
    with db_lock:
        with open(get_file_path(table_name), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


def generate_id(table_data):
    """Finds the highest ID in the table and adds 1 (like Auto-Increment in SQL)."""
    if not table_data:
        return 1
    return max((item.get('id', 0) for item in table_data), default=0) + 1


# --- HELPER FUNCTIONS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def send_google_script_email(data):
    try:
        if not GOOGLE_SCRIPT_URL or "script.google.com" not in GOOGLE_SCRIPT_URL:
            print("❌ Email skipped: GOOGLE_SCRIPT_URL not set.")
            return

        req = urllib.request.Request(
            GOOGLE_SCRIPT_URL,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            print(f"✅ Email Relay Response: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Email Relay Failed: {e}")


# --- ROUTES ---

@app.route('/')
def health_check():
    return "AHM Backend Active & JSON Files Connected."


@app.route('/api/login', methods=['POST'], strict_slashes=False)
def login():
    data = request.json
    if ADMIN_HASH != 'no-hash-provided' and check_password_hash(ADMIN_HASH, data.get('password')):
        return jsonify({"status": "success", "token": "ahm_aruba_2024"})
    return jsonify({"status": "error"}), 401


@app.route('/api/events', methods=['GET'], strict_slashes=False)
def get_events():
    today = datetime.now().strftime('%Y-%m-%d')
    events = read_table('Event')
    # Filter for future events and sort by date
    future_events = [e for e in events if e.get('date', '') >= today]
    future_events.sort(key=lambda x: x.get('date', ''))
    return jsonify(future_events)


@app.route('/api/admin/all-events', methods=['GET'], strict_slashes=False)
@login_required
def get_all_events():
    events = read_table('Event')
    events.sort(key=lambda x: x.get('date', ''), reverse=True)
    return jsonify(events)


@app.route('/api/admin/events', methods=['POST'], strict_slashes=False)
@login_required
def add_event():
    data = request.json
    events = read_table('Event')
    new_event = {
        "id": generate_id(events),
        "title": data.get('title'),
        "location": data.get('location'),
        "date": data.get('date'),
        "time": data.get('time'),
        "description": data.get('description'),
        "type": data.get('type'),
        "is_canceled": False
    }
    events.append(new_event)
    write_table('Event', events)
    return jsonify({"status": "success"})


@app.route('/api/admin/events/<int:id>', methods=['DELETE', 'PUT'], strict_slashes=False)
@login_required
def manage_event(id):
    events = read_table('Event')
    event_index = next((index for (index, d) in enumerate(events) if d["id"] == id), None)

    if event_index is None:
        return jsonify({"status": "error", "message": "Event not found"}), 404

    if request.method == 'DELETE':
        events.pop(event_index)
        write_table('Event', events)

    elif request.method == 'PUT':
        data = request.json
        event = events[event_index]
        event['title'] = data.get('title', event.get('title'))
        event['date'] = data.get('date', event.get('date'))
        event['time'] = data.get('time', event.get('time'))
        event['location'] = data.get('location', event.get('location'))
        event['description'] = data.get('description', event.get('description'))
        event['type'] = data.get('type', event.get('type'))
        if 'is_canceled' in data:
            event['is_canceled'] = data['is_canceled']
        write_table('Event', events)

    return jsonify({"status": "success"})


@app.route('/api/news', methods=['GET'], strict_slashes=False)
def get_news():
    news = read_table('NewsPost')
    news.sort(key=lambda x: x.get('date', ''), reverse=True)
    return jsonify(news)


@app.route('/api/admin/news', methods=['POST'], strict_slashes=False)
@login_required
def add_news():
    data = request.json
    news = read_table('NewsPost')
    new_post = {
        "id": generate_id(news),
        "title": data.get('title'),
        "date": data.get('date'),
        "content": data.get('content'),
        "image": data.get('image')
    }
    news.append(new_post)
    write_table('NewsPost', news)
    return jsonify({"status": "success"})


@app.route('/api/admin/news/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_news(id):
    news = read_table('NewsPost')
    news = [n for n in news if n.get('id') != id]  # Keep all EXCEPT the one to delete
    write_table('NewsPost', news)
    return jsonify({"status": "success"})


@app.route('/api/content', methods=['GET'], strict_slashes=False)
def get_content():
    content = read_table('SiteContent')
    # Convert list of dicts [{"key": "about", "value": "text"}] to {"about": "text"}
    content_dict = {item['key']: item['value'] for item in content}
    return jsonify(content_dict)


@app.route('/api/content', methods=['POST'], strict_slashes=False)
@login_required
def save_content():
    data = request.json
    try:
        content = read_table('SiteContent')

        for key, value in data.items():
            # Find if key exists
            existing_item = next((item for item in content if item['key'] == key), None)
            if existing_item:
                existing_item['value'] = value
            else:
                content.append({"key": key, "value": value})

        write_table('SiteContent', content)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/messages', methods=['GET'], strict_slashes=False)
@login_required
def get_messages():
    msgs = read_table('ContactMessage')
    msgs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify(msgs)


@app.route('/api/admin/messages/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_message(id):
    msgs = read_table('ContactMessage')
    msgs = [m for m in msgs if m.get('id') != id]
    write_table('ContactMessage', msgs)
    return jsonify({"status": "success"})


# --- CONTACT ROUTE ---
@app.route('/api/contact', methods=['POST'], strict_slashes=False)
def contact():
    data = request.json
    try:
        # 1. Save to JSON Database
        msgs = read_table('ContactMessage')
        new_msg = {
            "id": generate_id(msgs),
            "name": data.get('name'),
            "email": data.get('email'),
            "company": data.get('company', ''),
            "message": data.get('message'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        msgs.append(new_msg)
        write_table('ContactMessage', msgs)

        # 2. Send via Google Script Relay (Background)
        threading.Thread(target=send_google_script_email, args=(data,)).start()

        return jsonify({"status": "success", "message": "Mensahe a drenta"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)