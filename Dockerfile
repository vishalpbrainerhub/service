FROM python:3.11.7-slim
WORKDIR /app

# Accept build-time arguments for port and model size
ARG PORT=3000
ARG MODEL_SIZE=base

# Set environment variables
ENV PORT=${PORT}
ENV MODEL_SIZE=${MODEL_SIZE}

COPY . /app
RUN pip install -r requirements.txt

# Expose the port specified by the PORT argument
EXPOSE $PORT

CMD ["python", "./app.py"]
