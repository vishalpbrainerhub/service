# Real-Time Transcription Service

## Description

This project is a real-time transcription service built using FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.7+. It utilizes a pre-trained model called Whisper for efficient speech recognition. The service allows users to transcribe audio files or base64-encoded audio data into text.

---

## Setup Instructions

### Clone the repo

- https://github.com/vishalpbrainerhub/service

### 1. Install Dependencies

- Ensure you have Python 3.7+ installed on your system.
- Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Run the Service Locally

- Execute the following command to start the server:
    ```bash
    gunicorn main:app --workers 5  --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:3000
    ```
- The service will be default accessible at `http://localhost:3000`

- RUN server.py 
- Copy client.html path
- Start the service




### 3. Using Docker (Optional)

- You can also run the service using Docker for easier deployment.
- Build the Docker image with the desired configurations:
    ```bash
    docker build -t transcription-service .
    ```
- Run the Docker container:
    ```bash
    docker run -p 3000:3000 transcription-service
    ```
- The service will be available at `http://localhost:3000`.

---

## Endpoints

1. **Transcribe Audio File:**

    - **Endpoint:** `/transcribe_file`
    - **Method:** POST
    - **Request Body:** Form-data with key `audio_data` containing the audio file to be transcribed.
    - **Response:** JSON object containing the transcription result.


2. **Using Odoo16:**

    - switch to the ```dma_reports_whisper_mahendra``` branch
    - Use the realtime service by starting ```Record```
    - Auto - detecting language.

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


---


## Test it

 ```bash
    cd Testing_data

```

 ```bash
    python transcribe.py

```

---