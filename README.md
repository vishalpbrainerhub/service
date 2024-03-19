# Real-Time Transcription Service

---

## Description

This project is a real-time transcription service built using Flask, a lightweight WSGI web application framework. It allows users to transcribe audio files or base64-encoded audio data into text. The transcription is performed using a pre-trained model called Whisper, which is optimized for fast and efficient speech recognition. The service exposes two endpoints: one for transcribing audio files and another for transcribing base64-encoded audio data.

---

## Setup Instructions

### 1. Install Dependencies

- Ensure you have Python installed on your system.
- Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```


### 2. Run the Service

- Execute the `app.py` script to start the Flask server:
    ```bash
    python app.py
    ```
- The service will now be accessible at `http://localhost:5000`.

---

## Endpoints

1. **Transcribe Audio File:**

    - **Endpoint:** `/transcribe_file`
    - **Method:** POST
    - **Request Body:** Form-data with key `audio_data` containing the audio file to be transcribed.
    - **Response:** JSON object containing the transcription result.

2. **Transcribe Base64 Data:**

    - **Endpoint:** `/transcribe_base64`
    - **Method:** POST
    - **Request Body:** JSON object with key `audio_data` containing the base64-encoded audio data.
    - **Response:** JSON object containing the transcription result.

---

## Sample Usage

1. **Transcribe Audio File:**

    - **Request:**
        ```http
        POST /transcribe_file
        Content-Type: multipart/form-data
        
        [Audio File]
        ```
    - **Response:**
        ```json
        {
            "transcription": "Transcribed text here..."
        }
        ```

2. **Transcribe Base64 Data:**

    - **Request:**
        ```http
        POST /transcribe_base64
        Content-Type: application/json
        
        {
            "audio_data": "base64_encoded_audio_data_here"
        }
        ```
    - **Response:**
        ```json
        {
            "transcription": "Transcribed text here..."
        }
        ```

---
