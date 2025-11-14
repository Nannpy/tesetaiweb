# 1. Base Image: Use a Python image that includes essential development tools
FROM python:3.10-slim

# 2. Set Environment Variables (Fixed warnings: changed 'key value' to 'key=value')
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV APP_HOME=/usr/src/app

# 3. Create the application directory and set it as working directory
WORKDIR $APP_HOME

# 4. Install Dependencies
# Copy requirements file first (leverages Docker caching)
COPY requirements.txt .

# Install system dependencies needed for python packages (like pillow/opencv)
# Install pip dependencies (including pytorch, ultralytics, flask, gunicorn)
# Note: For production and to minimize image size, you might remove the build dependencies later in a multi-stage build.
# Install System Dependencies (Needed for OpenCV/Ultralytics) and perform initial cleanup
# We separate the system install from the pip install for better reliability and debugging.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Install Python Dependencies (including gunicorn, ultralytics, and torch)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the Application Code
# Copy the app files and the templates folder
COPY app.py .
# COPY index.html .
COPY templates/ templates/

# 6. Pre-load the YOLO model
# Running a simple command to trigger the YOLO model download during the build process, 
# preventing the user from waiting during the first runtime execution.
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# 7. Create necessary folders for uploads/output data at runtime
# We create them here so they are owned by the root user, and we ensure they exist.
RUN mkdir -p uploads static/output

# 8. Expose the port the Flask app runs on
EXPOSE 5003

# 9. Run the application using Gunicorn for production readiness
# Gunicorn is a robust HTTP server for running Python web applications.
# It listens on 0.0.0.0 (all interfaces) on port 5003 and runs the Flask app 'app:app'.
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5003", "app:app"]