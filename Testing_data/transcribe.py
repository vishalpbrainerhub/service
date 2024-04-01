import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transcribe_audio(file_path):
    """
    Sends an audio file to a transcription service and logs the response.

    Args:
    file_path (str): The path to the audio file to be transcribed.
    """
    url = 'http://localhost:3000/transcribe_file'
 
    with open(file_path, 'rb') as audio_file:
        files = {'audio_data': (file_path, audio_file, 'audio/wav')}
        try:
            logging.info("Sending audio file for transcription...")
            response = requests.post(url, files=files)
            response.raise_for_status()  # Checks for HTTP errors
            transcription_result = response.json()
            return transcription_result
        
        except requests.exceptions.RequestException as e:
            logging.error(f'Error occurred during transcription request: {e}')
            return None

def transcribe_concurrently(file_path, num_requests=30):
    """
    Simulates concurrent access to the transcription API.

    Args:
    file_path (str): The path to the audio file to be transcribed.
    num_requests (int): Number of concurrent requests to simulate.
    """
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        future_to_request = {executor.submit(transcribe_audio, file_path): i for i in range(num_requests)}
        for future in as_completed(future_to_request):
            request_id = future_to_request[future]
            try:
                data = future.result()
                if data:
                    logging.info(f"Request {request_id}: Transcription Successful")
                    print(f"Request {request_id}: {data['transcription']}")
                else:
                    logging.warning(f"Request {request_id}: Transcription failed or returned empty.")
            except Exception as exc:
                logging.error(f"Request {request_id} generated an exception: {exc}")
    
    duration = time.time() - start_time
    logging.info(f"All transcriptions completed in {duration:.2f} seconds.")

if __name__ == '__main__':
    audio_file_path = './check3.mp3'  # Update this path to your actual audio file path
    transcribe_concurrently(audio_file_path)
