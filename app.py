# Import Flask to create the web application
# jsonify converts Python dictionaries into JSON responses
# request lets us read data sent to the API
from flask import Flask, jsonify, request
# Import os so we can read environment variables
import os

# Create the Flask application
app = Flask(__name__)

# Store the current version of the application

APP_VERSION = "1.0.1"


# Health endpoint
# Used to check whether the application is running successfully
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "UP"}), 200


# Version endpoint
# Returns the current version of the application
@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": APP_VERSION}), 200


# Echo endpoint
# Accepts JSON data using a POST request and sends the same data back
@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    return jsonify({"echo": data}), 200

# Environment endpoint
# Reads the environment name from an environment variable
@app.route("/environment", methods=["GET"])
def environment():
    # Read the ENVIRONMENT variable
    # If it has not been set, use "development" as the defau
    environment_name = os.getenv("ENVIRONMENT", "development")
    
    return jsonify({"environment": environment_name}), 200


# Run the Flask application
if __name__ == "__main__":
    # Run the application on port 5000
    # 0.0.0.0 allows the application to be accessed outside the local process,
    app.run(host="0.0.0.0", port=5000)