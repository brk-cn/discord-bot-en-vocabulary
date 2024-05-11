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

    if message.content == '!w':
        rw = list(collection.aggregate([{ "$sample": { "size": 1 }}]))[0]
        await message.channel.send(f"{rw['word_english']} ({rw['word_class']}) : {rw['word_turkish']}")

    if message.content == '!q':
        rw = list(collection.aggregate([{ "$sample": { "size": 1 }}]))[0]
        await message.channel.send(f"{rw['word_english']} ({rw['word_class']})")

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            response = await client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await message.channel.send('Time is up!')
            return

        if response.content.lower() == rw['word_turkish'].lower():
            await message.channel.send('Correct!')
        else:
            await message.channel.send(f'Wrong! The correct answer is: {rw["word_turkish"]}')
    
client.run(TOKEN)