import os
import discord
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["vocabulary"]
collection = db["words"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):
        random_word = list(collection.aggregate([{ "$sample": { "size": 1 }}]))[0]
        await message.channel.send(f"{random_word['word_english']} ({random_word['word_class']}) : {random_word['word_turkish']}")

client.run(TOKEN)