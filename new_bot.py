import functools
import os
import typing
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

def blocking_function_authenticate(name, id):
    seconds = 0
    while True:
        try:
            time.sleep(5)
            seconds += 5
            response = requests.get(REDIRECT_URI + '/runners?user=' + name)
            print(response.json())
            if (name == response.json()['name'] and 'code' in response.json()):
                athlete_data = strava_connector.exchange_token(response.json()['code'])
                athlete_data['discordID'] = id
                file_handler.write_json(athlete_data)
                response = requests.get(REDIRECT_URI + '/authenticated?user=' + name)
                if response.ok:
                    return 1
            if seconds >= 120:
                return 0
        except:
            return 0

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)

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
    print(REDIRECT_URI)
    await ctx.send(f'http://www.strava.com/oauth/authorize?client_id={strava_connector.client_id}&response_type=code&redirect_uri={REDIRECT_URI}?user={member.name}&approval_prompt=auto&scope=activity:read')
    await ctx.send(f'You have 2 minutes to authenticate')
    result = await run_blocking(blocking_function_authenticate, member.name, member.id)
    print(result)
    if result == 0:
        await ctx.send('Authentication failed')
    else:
        await ctx.send('You have been authenticated')


@bot.command()
async def get_activities(ctx):
    """Get the latest activity"""
    athletes = file_handler.read_json()
    for athlete in athletes:
        activities = strava_connector.get_activities(athlete)
        message = "All activites for " + athlete['athlete']['firstname'] + "\n"
        for activity in activities:
            message += "Activity: " + activity['name'] + " - " + activity["type"] + "\n"
        
        await ctx.send(message)

@bot.command()
async def unauthenticate(ctx, member: discord.Member):
    """Unauthenticate the user"""
    athletes = file_handler.read_json()
    for athlete in athletes:
        if athlete['discordID'] == member.id:
            file_handler.remove_athlete(athlete)
            #strava_connector.unauthorized_request(athlete)
            await ctx.send('You have been unauthenticated')
            return

    await ctx.send('You are not authenticated')

bot.run(TOKEN)