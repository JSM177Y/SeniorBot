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

# Dictionary to store the latest commit SHA for each branch
latest_commit_shas = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')
    check_for_updates.start()  # Start the task to check for updates

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot is active and connected.")

@tasks.loop(minutes=5)  # Adjust the interval as needed
async def check_for_updates():
    global latest_commit_shas
    branches_url = f'https://api.github.com/repos/{GITHUB_REPO}/branches'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    branches_response = requests.get(branches_url, headers=headers)
    
    if branches_response.status_code != 200:
        print(f'Error fetching branches: {branches_response.status_code}, {branches_response.text}')
        return
    
    branches = branches_response.json()
    
    for branch in branches:
        branch_name = branch['name']
        commits_url = f'https://api.github.com/repos/{GITHUB_REPO}/commits?sha={branch_name}'
        commits_response = requests.get(commits_url, headers=headers)
        
        if commits_response.status_code != 200:
            print(f'Error fetching commits for branch {branch_name}: {commits_response.status_code}, {commits_response.text}')
            continue
        
        commits = commits_response.json()
        
        if not commits:
            print(f'No commits found for branch {branch_name} or error fetching commits.')
            continue

        latest_commit = commits[0]
        latest_sha = latest_commit['sha']
        print(f"Latest commit SHA for branch {branch_name}: {latest_sha}")

        if branch_name not in latest_commit_shas:
            latest_commit_shas[branch_name] = latest_sha
            print(f"Initialized latest_commit_sha for branch {branch_name}")
            continue

        if latest_sha != latest_commit_shas[branch_name]:
            print(f"New commit detected on branch {branch_name}")
            latest_commit_shas[branch_name] = latest_sha
            commit_message = latest_commit['commit']['message']
            commit_url = latest_commit['html_url']
            author = latest_commit['commit']['author']['name']

            # Get the channel
            channel = bot.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                message = f"New commit in {GITHUB_REPO} on branch {branch_name} by {author}:\n\n{commit_message}\n{commit_url}"
                await channel.send(message)
            else:
                print(f'Could not find channel with ID {DISCORD_CHANNEL_ID}')

# Run the bot
bot.run(DISCORD_BOT_TOKEN)