# Use the official Python image
FROM python:3.9.2

# Install FFmpeg from static build (new version)
RUN apt-get update && apt-get install -y wget xz-utils && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xvf ffmpeg-release-amd64-static.tar.xz && \
    cd ffmpeg-*-amd64-static && \
    cp ffmpeg ffprobe /usr/local/bin/ && \
    cd .. && \
    rm -rf ffmpeg-release*

# Set the working directory to /app
WORKDIR /app

# Copy the contents of the local repository to the container
COPY . .

#resolve cookies issue

COPY cookies.txt /app/cookies.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]