import os
import threading
import json
import urllib.request
import gspread
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

# --- GOOGLE SHEETS SETUP ---
# This connects to Google using the secret file you put next to app.py (or in Render Secret Files)
try:
    gc = gspread.service_account(filename='google_credentials.json')
    db_sheet = gc.open('Choir_Database')
    print("✅ Successfully connected to Google Sheets!")
except Exception as e:
    print(f"❌ Failed to connect to Google Sheets. Check your credentials file and sharing permissions! Error: {e}")

# We define the column headers for each tab so Python knows how to format the data when rewriting
HEADERS = {
    'Event': ['id', 'title', 'location', 'date', 'time', 'description', 'type', 'is_canceled'],
    'NewsPost': ['id', 'title', 'date', 'content', 'image'],
    'SiteContent': ['key', 'value'],
    'ContactMessage': ['id', 'name', 'email', 'company', 'message', 'timestamp']
}


def read_table(tab_name):
    """Reads a tab and returns a list of dictionaries."""
    try:
        worksheet = db_sheet.worksheet(tab_name)
        return worksheet.get_all_records()
    except Exception as e:
        print(f"Error reading {tab_name}: {e}")
        return []


def write_table(tab_name, data_list):
    """Clears the tab and rewrites all the data (useful for edits and deletes)."""
    try:
        worksheet = db_sheet.worksheet(tab_name)
        headers = HEADERS[tab_name]

        # Convert our list of dictionaries back into a list of lists for Google Sheets
        rows = [headers]
        for item in data_list:
            rows.append([item.get(h, "") for h in headers])

        worksheet.clear()
        worksheet.update(values=rows, range_name="A1")
    except Exception as e:
        print(f"Error writing to {tab_name}: {e}")


def append_to_table(tab_name, new_data_dict):
    """Simply adds one new row to the bottom (faster for new messages/events)."""
    try:
        worksheet = db_sheet.worksheet(tab_name)
        headers = HEADERS[tab_name]
        new_row = [new_data_dict.get(h, "") for h in headers]
        worksheet.append_row(new_row)
    except Exception as e:
        print(f"Error appending to {tab_name}: {e}")


def generate_id(table_data):
    """Finds the highest ID and adds 1."""
    if not table_data:
        return 1
    # Convert IDs to integers just in case Google Sheets reads them as strings
    return max((int(item.get('id', 0)) for item in table_data if str(item.get('id')).isdigit()), default=0) + 1


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
            return
        req = urllib.request.Request(
            GOOGLE_SCRIPT_URL,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"❌ Email Relay Failed: {e}")


# --- ROUTES ---

@app.route('/')
def health_check():
    return "AHM Backend Active & Google Sheets Connected."


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
    future_events = [e for e in events if str(e.get('date', '')) >= today]
    future_events.sort(key=lambda x: str(x.get('date', '')))
    return jsonify(future_events)


@app.route('/api/admin/all-events', methods=['GET'], strict_slashes=False)
@login_required
def get_all_events():
    events = read_table('Event')
    events.sort(key=lambda x: str(x.get('date', '')), reverse=True)
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
    append_to_table('Event', new_event)
    return jsonify({"status": "success"})


@app.route('/api/admin/events/<int:id>', methods=['DELETE', 'PUT'], strict_slashes=False)
@login_required
def manage_event(id):
    events = read_table('Event')
    event_index = next((index for (index, d) in enumerate(events) if str(d.get("id")) == str(id)), None)

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
    news.sort(key=lambda x: str(x.get('date', '')), reverse=True)
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
    append_to_table('NewsPost', new_post)
    return jsonify({"status": "success"})


@app.route('/api/admin/news/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_news(id):
    news = read_table('NewsPost')
    news = [n for n in news if str(n.get('id')) != str(id)]
    write_table('NewsPost', news)
    return jsonify({"status": "success"})


@app.route('/api/content', methods=['GET'], strict_slashes=False)
def get_content():
    content = read_table('SiteContent')
    content_dict = {item['key']: item['value'] for item in content if 'key' in item}
    return jsonify(content_dict)


@app.route('/api/content', methods=['POST'], strict_slashes=False)
@login_required
def save_content():
    data = request.json
    try:
        content = read_table('SiteContent')

        for key, value in data.items():
            existing_item = next((item for item in content if item.get('key') == key), None)
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
    msgs.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
    return jsonify(msgs)


@app.route('/api/admin/messages/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_message(id):
    msgs = read_table('ContactMessage')
    msgs = [m for m in msgs if str(m.get('id')) != str(id)]
    write_table('ContactMessage', msgs)
    return jsonify({"status": "success"})


# --- CONTACT ROUTE ---
@app.route('/api/contact', methods=['POST'], strict_slashes=False)
def contact():
    data = request.json
    try:
        # Save to Google Sheets directly via append_to_table (super fast!)
        new_msg = {
            "id": str(int(datetime.now().timestamp())),
            "name": data.get('name'),
            "email": data.get('email'),
            "company": data.get('company', ''),
            "message": data.get('message'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        append_to_table('ContactMessage', new_msg)

        # Relay email in background
        threading.Thread(target=send_google_script_email, args=(data,)).start()

        return jsonify({"status": "success", "message": "Mensahe a drenta"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)