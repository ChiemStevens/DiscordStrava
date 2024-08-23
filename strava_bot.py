import functools
import os
import typing
import discord
import json
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
import random
import threading
import time
import requests
from Cogs.subscribe_cog import SubscribeCog
from strava import StravaConnector
from file_reader import JsonFileHandler
from Cogs.backend_ping_cog import BackendPingCog

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
REDIRECT_URI = os.getenv('REDIRECT_URI')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(debug_guilds=[1274345035105570826], description="Strava bot", intents=intents)

strava_connector = StravaConnector()
file_handler = JsonFileHandler('runners.json')

bot.add_cog(BackendPingCog(bot))
bot.add_cog(SubscribeCog(bot, strava_connector))

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

@bot.command(description="Authenticate")
async def authenticate(ctx, member: discord.Member):
    runners = file_handler.read_json()
    for runner in runners:
        if runner['discordID'] == member.id:
            await ctx.respond('You have already connected to Strava')
            return
        
    # We can put the approval prompt to auto later to make sure that someone who is already authenticated won't have to reauthenticate on the page.
    await ctx.respond(f"Please autenticate using the following link: \n http://www.strava.com/oauth/authorize?client_id={strava_connector.client_id}&response_type=code&redirect_uri={REDIRECT_URI}?user={member.name}&approval_prompt=auto&scope=activity:read \n You have 2 minutes to authenticate")
    print(REDIRECT_URI)
    
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
            strava_connector.unauthorized_request(athlete)
            await ctx.send('You have been unauthenticated')
            return

    await ctx.send('You are not authenticated')


@bot.command(description="Make subscribe call")
async def subscribe(ctx):
    exists, id = strava_connector.check_and_create_subscription()
    await ctx.respond(f"new Sub creation: {not exists}, id: {id}")
    
@bot.command(description="Make unsubscribe call")
async def unsubscribe(ctx):
    if strava_connector.cancel_subscription():
        await ctx.respond("succesfully unsubscribed")
    else:
        await ctx.respond("Failed!!!!!!!!!!!!!!!!!!!")

@bot.command(description="Make unsubscribe call with an id")
async def unsubscribe_id(ctx, id):
    if strava_connector.cancel_subscription(id):
        await ctx.respond("succesfully unsubscribed")
    else:
        await ctx.respond("Failed!!!!!!!!!!!!!!!!!!!")

@bot.command(description="Make unsubscribe call with an id")
async def get_sub(ctx):
    exists, id = strava_connector.get_subscription()
    await ctx.respond(f"sub exists: {exists}, id: {id}")


bot.run(TOKEN)