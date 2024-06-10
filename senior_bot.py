import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests
import threading
import discord
from discord.ext import commands

# Load environment variables from a .env file
load_dotenv()

# Get the Discord bot token and webhook URL from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Check if the environment variables are set
if not DISCORD_BOT_TOKEN or not DISCORD_WEBHOOK_URL:
    raise ValueError("Please set the DISCORD_BOT_TOKEN and DISCORD_WEBHOOK_URL environment variables.")

app = Flask(__name__)

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable this only if necessary
bot = commands.Bot(command_prefix='!', intents=intents)

# Route to handle GitHub webhook
@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    if request.method == 'POST':
        data = request.json
        repo_name = data['repository']['full_name']
        pusher = data['pusher']['name']
        commit_message = data['head_commit']['message']
        commit_url = data['head_commit']['url']
        
        # Format the message for Discord
        message = f"Repository {repo_name} was updated by {pusher}.\nCommit Message: {commit_message}\nCommit URL: {commit_url}"
        
        # Send the message to Discord
        discord_data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_data)
        
        if response.status_code == 204:
            return jsonify({'message': 'Notification sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send notification'}), 500

def run_flask():
    app.run(port=5000)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')

# Run Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Run Discord bot
bot.run(DISCORD_BOT_TOKEN)
