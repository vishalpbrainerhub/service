from flask import Flask, request, jsonify
import os
import time
import random
import base64
import logging
from faster_whisper import WhisperModel
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

class AudioTranscriptionService:
    
    def __init__(self):
        self.model_size = os.environ.get("MODEL_SIZE", "base")
        self.device = "cpu"
        self.compute_type = "float32"
        # Initialize Whisper and Seamless models
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)


    def generate_file_name(self):
        """Generates a unique file name for storing audio files."""
        return f"audio_sessions/audio_file{random.randint(1, 100000)}.wav"


    async def transcribe_audio_file(self, audio_file):
        """Transcribe audio file data and return the transcription."""
        try:
            start_time = time.time()
            file_name = self.generate_file_name()
            audio_file.save(file_name)  # Save the received audio data to a file

            # Transcribe the audio file
            data = self.transcribing_chunk(file_name)

            # Attempt to remove the temporary audio file
            try:
                os.remove(file_name)
            except Exception as e:
                logging.error(f"Error during file removing: {e}")

            logging.info(f"Transcription took {time.time() - start_time:.2f} seconds")
            return jsonify({"transcription": data}), 200

        except Exception as e:
            logging.error(f"Error during decoding and conversion: {e}")
            return jsonify({"error": "Error during decoding and conversion"}), 500


    async def transcribe_base64(self, audio_data_base64):
        """Transcribe base64-encoded audio data and return the transcription."""
        try:
            audio_file_name = self.generate_file_name()
            audio_data = base64.b64decode(audio_data_base64)
            with open(audio_file_name, "wb") as file:
                file.write(audio_data)

            # Transcribe the audio file
            data = self.transcribing_chunk(audio_file_name)

            # Attempt to remove the temporary audio file
            try:
                os.remove(audio_file_name)
            except Exception as e:
                logging.error(f"Error during file removing: {e}")

            return jsonify({"transcription": data}), 200

        except Exception as e:
            logging.error(f"Error during decoding and conversion: {e}")
            return jsonify({"error": "Error during decoding and conversion"}), 500



    def transcribing_chunk(self, temp_audio_path):
        """Transcribe a chunk of audio using the Whisper model."""
        try:
            # Perform transcription using the Whisper model
            segments, info = self.model.transcribe(temp_audio_path, beam_size=5)
            transcription = " ".join([segment.text for segment in segments])
            logging.info(f"Transcription: {transcription}")
            return transcription
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return ""
        

# Instantiate the service
audio_transcription_service = AudioTranscriptionService()


@app.route('/transcribe_file', methods=['POST'])
async def transcribe_audio_file_route():
    audio_file = request.files['audio_data']
    return await audio_transcription_service.transcribe_audio_file(audio_file)




@app.route('/transcribe_base64', methods=['POST'])
async def transcribe_base64_route():
    audio_data_base64 = request.json.get('audio_data', None)
    if not audio_data_base64:
        return jsonify({"error": "No audio data provided"}), 400
    return await audio_transcription_service.transcribe_base64(audio_data_base64)


@app.route('/', methods=['GET'])
def home():
    return "Real Time Transcription Service Running"



if __name__ == '__main__':
    port = os.environ.get("PORT", "3000")
    # Read model size from environment variable (used if needed elsewhere)
    model_size = os.environ.get("MODEL_SIZE", "base")
    app.run(debug=True, host="0.0.0.0", port=int(port))