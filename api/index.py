from flask import Flask, request, jsonify, abort
import os
import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Initialize the Flask app
app = Flask(__name__)

# --- Configuration and Security ---
# Fetch the Discord Application Public Key from environment variables
# This is CRITICAL for security and verifying the request is from Discord.
DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

if not DISCORD_PUBLIC_KEY:
    print("WARNING: DISCORD_PUBLIC_KEY environment variable is not set. Interaction verification will fail.")
else:
    # Convert the public key string to a verification key object
    try:
        VERIFY_KEY = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
    except Exception as e:
        print(f"Error initializing VerifyKey: {e}")
        VERIFY_KEY = None


# --- Discord Interaction Verification Middleware ---
def verify_signature(req):
    """Verifies the request signature using the Public Key."""
    if not VERIFY_KEY:
        # If key isn't set, abort immediately (security best practice)
        print("Verification key is missing. Aborting.")
        abort(401, 'Public Key Missing')

    signature = req.headers.get("X-Signature-Ed25519")
    timestamp = req.headers.get("X-Signature-Timestamp")
    body = req.data.decode("utf-8")

    if not signature or not timestamp or not body:
        print("Missing signature, timestamp, or body.")
        abort(401, 'Missing required headers/body')

    try:
        # Verification requires the timestamp + the raw body
        VERIFY_KEY.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        print("Invalid signature.")
        abort(401, 'Invalid Signature')
    except Exception as e:
        print(f"Verification error: {e}")
        abort(401, 'Verification Error')


# --- Main Discord Interactions Endpoint ---
@app.route("/api/index", methods=["POST"])
def interactions():
    # 1. Verification (CRITICAL Security Step)
    verify_signature(request)

    # Load the verified JSON payload
    data = request.json

    # 2. Handle PING/PONG (Type 1 Interaction)
    if data["type"] == 1:
        # This is Discord testing the endpoint. Respond with PONG (Type 1).
        print("Received PING, sending PONG.")
        return jsonify({"type": 1})

    # 3. Handle Application Command (Type 2 Interaction - Slash Commands)
    elif data["type"] == 2:
        command_name = data["data"]["name"]
        
        # Simple handler for a '/hello' command
        if command_name == "hello":
            # Respond with a channel message (Type 4)
            response_message = {
                "type": 4, # Type 4 is CHANNEL_MESSAGE_WITH_SOURCE
                "data": {
                    "content": "Hello! I am a serverless bot running on Vercel. I processed your `/hello` command successfully!",
                    "flags": 64 # Optional: makes the response visible only to the user who ran the command
                }
            }
            return jsonify(response_message)
            
        # Add more command handlers here...
        elif command_name == "ping":
            return jsonify({
                "type": 4, 
                "data": {
                    "content": f"Pong! Vercel latency check successful.",
                    "flags": 64
                }
            })

        else:
            # Handle unknown commands
            return jsonify({
                "type": 4,
                "data": {
                    "content": "Unknown command received. Did you register your slash commands?",
                    "flags": 64
                }
            })

    # 4. Handle other interaction types if needed (e.g., buttons, modals)

    # Default fallback
    return jsonify({"type": 1}), 400


# Vercel requires the function handler to be defined
# The name 'app' is the standard entry point for Python/Flask on Vercel.
if __name__ == "__main__":
    app.run(debug=True)
