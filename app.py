import os
import subprocess
from threading import Thread
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager

# Initialize Flask app for serving the frontend
app = Flask(__name__, static_folder="frontend", template_folder="frontend")

app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this to a secure key!
jwt = JWTManager(app)

# Serve the frontend
@app.route("/")
def serve_frontend():
    return send_from_directory("frontend", "index.html")

# Start the Flask backend (runs `backend/app.py`)
def start_backend():
    subprocess.run(["python", "backend/app.py"])

# Start the backend in a separate thread
if __name__ == "__main__":
    backend_thread = Thread(target=start_backend)
    backend_thread.start()
    app.run(debug=True, host="0.0.0.0", port=8000)
