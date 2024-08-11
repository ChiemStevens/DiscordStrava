import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
import random
import threading
import time
import requests
from strava import StravaConnector
from file_reader import JsonFileHandler

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
REDIRECT_URI = os.getenv('REDIRECT_URI')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description="Strava bot", intents=intents)

strava_connector = StravaConnector()
file_handler = JsonFileHandler('runners.json')

@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.command()
async def get_activities(ctx):
    """Get the latest activity"""
    athletes = file_handler.read_json()
    for athlete in athletes:
        if 'access_token' in athlete:
            activities = strava_connector.get_activities(athlete['access_token'])
            message = "All activites for " + athlete['athlete']['firstname'] + "\n"
            for activity in activities:
                message += "Activity: " + activity['name'] + " - " + activity["type"] + "\n"
            
            await ctx.send(message)

@bot.command()
async def strava(ctx, member: discord.Member):
    """Start the strava part"""
    runners = file_handler.read_json()
    for runner in runners:
        if runner['discordID'] == member.id:
            await ctx.send('You have already connected to Strava')
            return
        
    await ctx.send(f'Please autenticate using the following link:')
    # We can put put the approval prompt to auto later to make sure that someone who is already authenticated won't have to reauthenticate on the page.
    await ctx.send(f'http://www.strava.com/oauth/authorize?client_id={strava_connector.client_id}&response_type=code&redirect_uri={REDIRECT_URI}?user={member.name}&approval_prompt=force&scope=activity:read')
    await ctx.send(f'You have 2 minutes to authenticate')
    time = 0
    while True:
            try:
                await asyncio.sleep(5)
                time += 5
                response = requests.get(REDIRECT_URI + '/runners?user=' + member.name)
                print(response.json()['name'])
                if member.name == response.json()['name']:
                    athlete_data = strava_connector.exchange_token(response.json()['code'])
                    athlete_data['discordID'] = member.id
                    file_handler.write_json(athlete_data)
                    response = requests.get(REDIRECT_URI + '/authenticated?user=' + member.name)
                    if response.ok:
                        await ctx.send('You have successfully connected to Strava')
                        break
                if time >= 120:
                    await ctx.send('Time is up')
                    break
            except:
                break

bot.run(TOKEN)