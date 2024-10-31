from flask import Flask, render_template, request, jsonify, send_from_directory
import edge_tts
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
import glob
import atexit

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

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/get_voices')
async def get_voices():
    voices = await edge_tts.list_voices()
    return jsonify(voices)

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
