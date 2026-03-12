# Use the latest Python 3.13 image
FROM python:3.13-slim

# Install FFmpeg (essential for yt-dlp to process audio)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Ensure the cache directory exists so the script doesn't crash
RUN mkdir -p static/cache

# Start the app
CMD ["python", "main.py"]
