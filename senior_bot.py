import os
import requests
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the Discord bot token and GitHub repository info from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')  # Format: username/repo
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Set up the Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Variable to store the latest commit SHA
latest_commit_sha = None

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')
    check_for_updates.start()  # Start the task to check for updates

@tasks.loop(minutes=5)  # Adjust the interval as needed
async def check_for_updates():
    global latest_commit_sha
    url = f'https://api.github.com/repos/{GITHUB_REPO}/commits'
    response = requests.get(url)
    commits = response.json()
    
    if not commits:
        print('No commits found or error fetching commits.')
        return

    latest_commit = commits[0]
    latest_sha = latest_commit['sha']

    if latest_commit_sha is None:
        latest_commit_sha = latest_sha
        return

    if latest_sha != latest_commit_sha:
        latest_commit_sha = latest_sha
        commit_message = latest_commit['commit']['message']
        commit_url = latest_commit['html_url']
        author = latest_commit['commit']['author']['name']

        # Get the channel
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            message = f"New commit in {GITHUB_REPO} by {author}:\n\n{commit_message}\n{commit_url}"
            await channel.send(message)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)