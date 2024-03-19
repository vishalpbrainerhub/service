import asyncio
import atexit
import base64
import json
import logging
import random
import threading
from urllib.parse import urlparse, parse_qs
import concurrent.futures
import assemblyai as aai
import websockets
import uuid
from faster_whisper import WhisperModel
from pydub import AudioSegment
import os
from transformers import AutoProcessor, SeamlessM4TForSpeechToText



_logger = logging.getLogger(__name__)


class RealtimeWhisher:


    def __init__(self):
        self._initialized = True
        self.model_size = "base"
        self.device = "cpu"
        self.compute_type = "float32"
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        self.segment = 3072
        self.start_time = 0
        self.end_time = self.segment
        self.processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
        self.seamless_model = SeamlessM4TForSpeechToText.from_pretrained("facebook/hf-seamless-m4t-medium")
        self.transcribe_model = "deepgram"


    async def checking(self, websocket, language_param):
        """Handles incoming audio data over websocket, decodes, transcribes, and sends back transcription."""
        session_id = str(uuid.uuid4())
        file_path = self._initialize_session_file(session_id)

        async for audio_chunk_base64 in websocket:

            print("audio_chunk_base64:--", audio_chunk_base64[:50],"---------------------------------")
            # base64_encoded_data = audio_chunk_base64.split(",")[1]
            try:
                audio_chunk = audio_chunk_base64
                self._append_to_session_file(session_id, audio_chunk)
                transcription_data = await self.divide_audio(file_path)
                await websocket.send(transcription_data)
            except Exception as e:
                _logger.error(f"Error during decoding and conversion: {e}")



    def divide_audio(self, audio_file):
        """Determines the appropriate transcription function based on the model and transcribes the audio."""
        function_handler = self.real_transcribe_chunk_fasterWhisper
       
        transcription = function_handler(audio_file)
        print("transcription:--", transcription,"---------------------------------")
        return transcription



    def real_transcribe_chunk_fasterWhisper(self, chunk_file):
        """Transcribes audio using the Faster Whisper model."""
        audio = AudioSegment.from_file(chunk_file)
        temp_audio_path = self._create_temp_audio_file(audio)

        test_audio = AudioSegment.from_file(temp_audio_path)
        if self._is_audio_short(test_audio):
            os.remove(temp_audio_path)
            return ""

        transcription = ""
        try:
            segments, info = self.model.transcribe(temp_audio_path, beam_size=5)
            transcription = " ".join([segment.text for segment in segments])

            print(transcription,"--------------------------------")
        except Exception as e:
            _logger.error(f"Error during transcription: {e}")
        finally:
            _logger.info("Removing temporary audio file")
            os.remove(temp_audio_path)
        return transcription



    def _initialize_session_file(self, session_id):
        """Initializes and returns the file path for the audio session."""
        dir_path = "audio_sessions"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_path = f"{dir_path}/{session_id}.wav"
        open(file_path, 'wb').close()
        return file_path



    def _append_to_session_file(self, session_id, audio_chunk):
        """Appends an audio chunk to the session file."""
        file_path = f"audio_sessions/{session_id}.wav"
        with open(file_path, 'ab') as file:
            file.write(audio_chunk)



    def _create_temp_audio_file(self, audio):
        """Creates a temporary audio file and returns its path."""
        temp_audio_path = f"audio_sessions/temp_audio_{random.randint(0, 10000)}.wav"
        audio[self.start_time:self.end_time].export(temp_audio_path, format="wav")
        return temp_audio_path



    def _is_audio_short(self, test_audio):
        """Checks if the audio segment is shorter than expected and logs accordingly."""
        if len(test_audio) < self.segment:
            _logger.info("Audio segment is shorter than expected, skipping transcription.")
            return True
        return False



    def _update_audio_segment_times(self):
        """Updates the start and end times for audio processing."""
        self.start_time += self.segment
        self.end_time += self.segment


realtime_whisher = RealtimeWhisher()
data = realtime_whisher.divide_audio("test.wav")
print(data)