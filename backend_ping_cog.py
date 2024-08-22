from discord.ext import tasks, commands
import requests
import os
import time

class BackendPingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('REDIRECT_URI')
        self.pingLoop.start()

    def cog_unload(self) -> None:
        self.pingLoop.cancel()
    
    @tasks.loop(minutes=5.0)
    async def pingLoop(self):
        now = time.time()
        requests.get(url=f"{self.backend_url}ping")
        print(f"Pinging backend took: {time.time() - now} ms")
        pass

    @pingLoop.before_loop
    async def before_pingLoop(self):
        await self.bot.wait_until_ready()