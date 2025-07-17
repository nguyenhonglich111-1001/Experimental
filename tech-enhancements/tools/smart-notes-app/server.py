import os
import json
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure the Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# In-memory "database" for simplicity
DB_FILE = 'db.json'

def read_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- API Routes ---

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = read_db()
    return jsonify(list(notes.values()))

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400
    
    notes = read_db()
    note_id = str(uuid.uuid4())
    notes[note_id] = {
        "id": note_id,
        "title": data['title'],
        "content": data['content']
    }
    write_db(notes)
    return jsonify(notes[note_id]), 201

@app.route('/api/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400

    notes = read_db()
    if note_id not in notes:
        return jsonify({"error": "Note not found"}), 404
    
    notes[note_id]['title'] = data['title']
    notes[note_id]['content'] = data['content']
    write_db(notes)
    return jsonify(notes[note_id])

@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    notes = read_db()
    if note_id not in notes:
        return jsonify({"error": "Note not found"}), 404
    
    del notes[note_id]
    write_db(notes)
    return '', 204

@app.route('/api/notes/summarize', methods=['POST'])
def summarize_note():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required for summarization"}), 400

    if not api_key:
        return jsonify({"summary": "Error: GOOGLE_API_KEY not configured."}), 500

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Summarize the following text in one or two sentences:\n\n{data['content']}"
        response = model.generate_content(prompt)
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"summary": f"Error during summarization: {str(e)}"}), 500

# --- Frontend Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
