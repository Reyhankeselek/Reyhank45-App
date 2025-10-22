from flask import Flask, request, jsonify
from discord.interactions import verify_key_simple
import os

# Your bot's public key (from the "General Information" page in your Developer Portal)
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

app = Flask(__name__)

@app.route('/', methods=['POST'])
def interactions():
    # 1. Verify the request is from Discord
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    if not verify_key_simple(body, signature, timestamp, PUBLIC_KEY):
        return 'Bad request signature', 401

    # 2. Handle the interaction
    data = request.json
    interaction_type = data.get('type')

    # Type 1: Ping (Discord checking if your bot is alive)
    if interaction_type == 1:
        return jsonify({'type': 1})  # Respond with a "pong"

    # Type 2: Application Command (Slash Command)
    if interaction_type == 2:
        command_name = data['data']['name']

        if command_name == 'hello':
            # This is the response to the '/hello' command
            return jsonify({
                'type': 4,  # Type 4: Channel message with source
                'data': {
                    'content': 'Hello from my Vercel bot!'
                }
            })

    # Default/unknown case
    return jsonify({'type': 5}) # Acknowledge without a message

# This 'app' variable is what Vercel looks for
# The 'if' block is for local testing (optional)
if __name__ == '__main__':
    app.run(debug=True)