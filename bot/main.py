import discord
from pymongo import MongoClient
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
URI = os.getenv("MONGODB_URI")

client = MongoClient(URI)
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

    if message.content.startswith('!w'):
        parts = message.content.split()
        if len(parts) == 1:
            num = 1
        else:
            try:
                num = int(parts[1])
                if num > 10:
                    num = 10 
            except ValueError:
                await message.channel.send('Please enter a valid number.')
                return
        
        random_words = list(collection.aggregate([{ "$sample": { "size": num }}]))
        for word in random_words:
            await message.channel.send(f"{word['word_english']} ({word['word_class']}) : {word['word_turkish']}")


    if message.content == '!q':
        random_word = list(collection.aggregate([{ "$sample": { "size": 1 }}]))[0]
        await message.channel.send(f"{random_word['word_english']} ({random_word['word_class']})")

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        
        try:
            response = await client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await message.channel.send('Time is up!')
            return

        if response.content.lower() == random_word['word_turkish'].lower():
            await message.channel.send('Correct!')
        else:
            await message.channel.send(f'Wrong! The correct answer is: {random_word["word_turkish"]}')
    
client.run(TOKEN)