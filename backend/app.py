


from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import uuid
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Simplified CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type"],
        "support_credentials": False
    }
})

# Debug logging
@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path} from {request.origin}")
    print(f"Headers: {request.headers}")

# Load environment variables
load_dotenv()

# MongoDB connection
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client["device_tracker_new"]
    users_collection = db["users"]
    client.server_info()  # Test connection
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Login endpoint
@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        print("Handling OPTIONS request for /api/login")
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = request.origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,Accept"
        return response, 200

    data = request.get_json()
    print(f"POST data: {data}")
    username = data.get("username")
    device_id = data.get("device_id") or str(uuid.uuid4())

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Find or create user
    user = users_collection.find_one({"username": username})
    if not user:
        user = {"username": username, "devices": []}
        users_collection.insert_one(user)
        user = users_collection.find_one({"username": username})

    # Update or add device
    device_exists = any(device["device_id"] == device_id for device in user["devices"])
    if not device_exists:
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$push": {
                    "devices": {
                        "device_id": device_id,
                        "last_login": datetime.utcnow(),
                        "login_count": 1,
                    }
                }
            },
        )
    else:
        users_collection.update_one(
            {"_id": user["_id"], "devices.device_id": device_id},
            {
                "$set": {"devices.$.last_login": datetime.utcnow()},
                "$inc": {"devices.$.login_count": 1},
            },
        )

    return jsonify({"message": "Login successful", "device_id": device_id}), 200

# Get device history
@app.route("/api/devices/<username>", methods=["GET", "OPTIONS"])
def get_devices(username):
    if request.method == "OPTIONS":
        print("Handling OPTIONS request for /api/devices")
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = request.origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,Accept"
        return response, 200

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"username": username, "devices": user.get("devices", [])}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")