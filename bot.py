import discord
import requests
import os

TOKEN = os.getenv('DISCORD_BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True  # Enable the Message Content Intent

# Create the bot client
client = discord.Client(intents=intents)

# This event runs when the bot has successfully connected to Discord.
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}') # Logs a message to your terminal

# This event runs every time a message is sent in a server the bot is in.
@client.event
async def on_message(message):
    # Don't let the bot respond to its own messages
    if message.author == client.user:
        return

    # Check if the message starts with '!hello'
    if message.content.startswith('!hello'):
        # Send a reply back to the same channel
        await message.channel.send('Hello!')

client.run(TOKEN)

