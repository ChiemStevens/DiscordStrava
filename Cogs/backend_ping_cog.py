from discord.ext import tasks, commands
import requests
import os
import time

class BackendPingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('REDIRECT_URI')
        self.ping_loop.start()

        self.observers = []

        self.online = False

    def cog_unload(self) -> None:
        self.ping_loop.cancel()
    
    @tasks.loop(minutes=5.0)
    async def ping_loop(self):
        now = time.time()
        response = requests.get(url=f"{self.backend_url}ping")

        self.update_backend_status(response.status_code == 200)

        print(f"Pinging backend took: {time.time() - now} s and online: {self.online}")
        pass

    @ping_loop.before_loop
    async def before_ping_loop(self):
        await self.bot.wait_until_ready()

    def update_backend_status(self, newStatus):
        if self.online is not newStatus:
            self.online = newStatus
            self.notify_observers()
        pass

    def register_observer(self, obj):
        self.observers.append(obj)

    def deregister_observer(self, obj):
        self.observers.remove(obj)

    def notify_observers(self):
        if self.online:
            for observer in self.observers:
                observer.backend_online()
        else:
            for observer in self.observers:
                observer.backend_offline()