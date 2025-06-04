from flask import Flask, render_template, request, jsonify, send_from_directory
import edge_tts
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
import glob
import atexit
import re

app = Flask(__name__)

# Create temporary directory
TEMP_DIR = tempfile.mkdtemp()
print(f"Temporary directory created at: {TEMP_DIR}")

def cleanup_old_files():
    """Remove files older than 1 hour"""
    threshold = datetime.now() - timedelta(hours=1)
    for file in glob.glob(os.path.join(TEMP_DIR, "*.mp3")):
        try:
            file_time = datetime.fromtimestamp(os.path.getctime(file))
            if file_time < threshold:
                os.remove(file)
        except OSError:
            pass

def fix_linebreaks(text):
    """Fix unnecessary linebreaks in paragraphs"""
    # Replace single newlines but keep paragraph breaks
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Normalize multiple newlines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def fix_hyphenation(text):
    """Fix hyphenated words split across lines"""
    return re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

def normalize_spaces(text):
    """Normalize multiple spaces and remove trailing/leading spaces"""
    return ' '.join(text.split())

async def get_ava_voice():
    """Get the exact Ava voice name from the available voices"""
    voices = await edge_tts.list_voices()
    for voice in voices:
        if 'Ava' in voice['ShortName'] and voice['Locale'] == 'en-US':
            return voice['Name']
    return None

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/get_voices')
async def get_voices():
    voices = await edge_tts.list_voices()
    default_voice = await get_ava_voice()
    return jsonify({
        'voices': voices,
        'default_voice': default_voice
    })

@app.route('/synthesize', methods=['POST'])
async def synthesize():
    cleanup_old_files()
    text = request.form.get('text')
    voice = request.form.get('voice')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.mp3"
    filepath = os.path.join(TEMP_DIR, filename)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)
    
    # Serve file through a temporary route
    temp_url = f'/temp_audio/{filename}'
    
    return jsonify({
        'audio_url': temp_url,
        'text': text,
        'voice': voice
    })

@app.route('/fix_text', methods=['POST'])
def fix_text():
    text = request.json.get('text', '')
    fix_type = request.json.get('fix_type', 'all')
    
    if fix_type == 'linebreaks':
        text = fix_linebreaks(text)
    elif fix_type == 'hyphenation':
        text = fix_hyphenation(text)
    elif fix_type == 'spaces':
        text = normalize_spaces(text)
    elif fix_type == 'all':
        # When fixing everything, apply hyphenation fix before removing
        # line breaks so that words split across lines are joined correctly.
        text = fix_hyphenation(text)
        text = fix_linebreaks(text)
        text = normalize_spaces(text)
    
    return jsonify({'fixed_text': text})

@app.route('/temp_audio/<filename>')
def serve_temp_audio(filename):
    return send_from_directory(TEMP_DIR, filename)

# Cleanup function for application shutdown
def cleanup_temp_folder():
    import shutil
    try:
        shutil.rmtree(TEMP_DIR)
        print(f"Temporary directory removed: {TEMP_DIR}")
    except Exception as e:
        print(f"Error removing temporary directory: {e}")

# Register cleanup function
atexit.register(cleanup_temp_folder)

if __name__ == '__main__':
    app.run(debug=True)
