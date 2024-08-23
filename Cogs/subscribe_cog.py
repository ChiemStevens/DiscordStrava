from discord.ext import tasks, commands

class SubscribeCog(commands.Cog):
    def __init__(self, bot, stravaConnector) -> None:
        self.bot = bot
        self.stravaConnector = stravaConnector

        backendPingCog = self.bot.get_cog("BackendPingCog")
        backendPingCog.register_observer(self)

# commands
    

# processes
    def create_subscription(self):
        exists, id = self.stravaConnector.check_and_create_subscription()
        print(f"new Sub creation: {not exists}, id: {id}")

    def cancel_subscription(self):
        if self.stravaConnector.cancel_subscription():
            print("Succesfully unsubbed")
        else:
            print("Unsub failed")

    def backend_online(self):
        print(f"Backend is now online")
        self.create_subscription()
        
    def backend_offline(self):
        print(f"Backend is now Offline")
        self.cancel_subscription()

    def cog_unload(self) -> None:
        self.cancel_subscription()