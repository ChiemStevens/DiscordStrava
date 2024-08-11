class DataObjects:
    def __init__(self):
        self.data = []

    def get_athlete_json(self, discordID, athleteID):
        self.data.append({"discordID": discordID})
        self.data.append({"athleteID": athleteID})
        return self.data