import os
import time
import random
import base64
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
import torch
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

class AudioTranscriptionService:
    
    def __init__(self):
        self.model_size = os.environ.get("MODEL_SIZE", "base")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float32"
        self.audio_sessions_folder = "audio_sessions"  # Define the folder name
        
        # Check if 'audio_sessions' folder exists, if not, create it
        if not os.path.exists(self.audio_sessions_folder):
            os.makedirs(self.audio_sessions_folder)

        # Initialize Whisper model
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def generate_file_name(self):
        """Generates a unique file name for storing audio files."""
        return f"{self.audio_sessions_folder}/audio_file{random.randint(1, 100000)}.wav"

    async def transcribe_audio_file(self, audio_file):
        """Transcribe audio file data and return the transcription."""
        try:
            start_time = time.time()
            file_name = self.generate_file_name()
            with open(file_name, "wb") as file_object:
                file_object.write(audio_file.file.read())  # Save the received audio data to a file

            # Transcribe the audio file
            data = await self.transcribing_chunk(file_name)

            # Attempt to remove the temporary audio file
            try:
                os.remove(file_name)
            except Exception as e:
                logging.error(f"Error during file removing: {e}")

            logging.info(f"Transcription took {time.time() - start_time:.2f} seconds")
            return {"transcription": data}

        except Exception as e:
            logging.error(f"Error during decoding and conversion: {e}")
            raise HTTPException(status_code=500, detail="Error during decoding and conversion")

    async def transcribe_base64(self, audio_data_base64):
        """Transcribe base64-encoded audio data and return the transcription."""
        try:
            audio_file_name = self.generate_file_name()
            audio_data = base64.b64decode(audio_data_base64)
            with open(audio_file_name, "wb") as file:
                file.write(audio_data)

            # Transcribe the audio file
            data = await self.transcribing_chunk(audio_file_name)

            # Attempt to remove the temporary audio file
            try:
                os.remove(audio_file_name)
            except Exception as e:
                logging.error(f"Error during file removing: {e}")

            return {"transcription": data}

        except Exception as e:
            logging.error(f"Error during decoding and conversion: {e}")
            raise HTTPException(status_code=500, detail="Error during decoding and conversion")

    async def transcribing_chunk(self, temp_audio_path):
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

@app.post('/transcribe_file')
async def transcribe_audio_file_route(audio_data: UploadFile = File(...)):
    return await audio_transcription_service.transcribe_audio_file(audio_data)

@app.post('/transcribe_base64')
async def transcribe_base64_route(audio_data_base64: str):
    return await audio_transcription_service.transcribe_base64(audio_data_base64)

@app.get('/')
async def home():
    return "Real Time Transcription Service Running fastapi"

if __name__ == '__main__':
    port = os.environ.get("PORT", "3000")
    uvicorn.run(app, host="0.0.0.0", port=int(port))  
