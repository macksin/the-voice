from flask import Flask, render_template, request, jsonify
import edge_tts
import asyncio
import os
from datetime import datetime

app = Flask(__name__)
AUDIO_FOLDER = 'static/audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_voices')
async def get_voices():
    voices = await edge_tts.list_voices()
    return jsonify(voices)

@app.route('/synthesize', methods=['POST'])
async def synthesize():
    text = request.form.get('text')
    voice = request.form.get('voice')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)
    
    return jsonify({
        'audio_url': f'/static/audio/{filename}',
        'text': text,
        'voice': voice
    })

if __name__ == '__main__':
    app.run(debug=True)
