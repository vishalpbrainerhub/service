from fastapi import FastAPI, WebSocket, HTTPException
import aiofiles
import asyncio
import uvicorn
import uuid
from pydub import AudioSegment
import requests
from concurrent.futures import ThreadPoolExecutor
import os
import logging

app = FastAPI()

# Configure logging to facilitate easier debugging and operational monitoring.
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# Preparing the environment for audio processing.
audio_sessions_folder = "audio_sessions"
os.makedirs(audio_sessions_folder, exist_ok=True)

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket, language: str = "en"):
    """
    WebSocket endpoint for real-time audio transcription.
    Accepts audio data via WebSocket, transcribes it, and sends the transcription back through the WebSocket.
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    audio_file_path = f"{audio_sessions_folder}/current_audio_{session_id}.wav"
    start_time = 0
    segment = 3000  # Process audio chunks of 3000 milliseconds each.

    async with aiofiles.open(audio_file_path, "ab") as audio_file:
        while True:
            data = await websocket.receive_bytes()
            await audio_file.write(data)

            transcription = await transcribe_audio_chunk_async(audio_file_path, start_time, segment, language)
            await websocket.send_text(transcription)

            start_time += segment
            

async def transcribe_audio_chunk_async(audio_file_path, start_time, segment, language):
    """
    Wraps the synchronous chunk transcription in an asynchronous call.
    This allows it to be called without blocking the async loop.
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        transcription = await loop.run_in_executor(
            pool,
            transcribe_audio_chunk,
            audio_file_path,
            start_time,
            segment,
            language
        )
    return transcription

def transcribe_audio_chunk(audio_file_path, start_time, segment, language):
    """
    Synchronously transcribes a chunk of audio.
    This function is designed to be run in a thread to avoid blocking.
    """
    try:
        audio = AudioSegment.from_file(audio_file_path)
        chunk = audio[start_time:start_time+segment]

        temp_audio_path = f"{audio_sessions_folder}/temp_{uuid.uuid4()}.wav"
        chunk.export(temp_audio_path, format="wav")

        if len(chunk) < segment:
            os.remove(temp_audio_path)
            return "End of audio or audio is too short for transcription."

        # Call to an external service for transcription. Adjust the URL as necessary.
        url = 'http://localhost:3000/transcribe_file'
        with open(temp_audio_path, 'rb') as audio_file:
            files = {'audio_data': (temp_audio_path, audio_file, 'audio/wav')}
            response = requests.post(url, files=files, data={"language": language})
            transcription_result = response.json()
            transcription_text = transcription_result.get('transcription', 'Error: Transcription not found')

        os.remove(temp_audio_path)
        return transcription_text

    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return "Error in transcription"

if __name__ == "__main__":
    # Configuration for Uvicorn server, with environment variables for customization.
    port = os.environ.get("PORT", "8000")
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=int(port))
