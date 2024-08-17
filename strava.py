import os
import requests
from dotenv import load_dotenv
from file_reader import JsonFileHandler
import time

class StravaConnector:
    def __init__(self):
        # Load environment variables from a .env file
        load_dotenv()
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.update_refresh_tokens()
    
    # Update the refresh token of all the athletes
    def update_refresh_tokens(self):
        file_reader = JsonFileHandler('runners.json')
        runners = file_reader.read_json()
        for runner in runners:
            self.update_refresh_token(runner, file_reader)

    def update_refresh_token(self, athlete, file_reader : JsonFileHandler = None):
        if file_reader is None:
            # If no file reader is provided, create a new one
            # My VS code is saying this code is unreachable, but it is not. So I will just leave it at this.
            print("No file reader")
            file_reader = JsonFileHandler('runners.json')

        epoch_time = time.time()
        if 'refresh_token' in athlete:
                if epoch_time > athlete['expires_at']:
                    new_token = self.get_refresh_token(athlete['refresh_token'])
                    athlete['access_token'] = new_token['access_token']
                    athlete['expires_at'] = new_token['expires_at']
                    athlete['expires_in'] = new_token['expires_in']
                    athlete['refresh_token'] = new_token['refresh_token']
                    file_reader.update_atlete(athlete)

    # Used when the token is first retrieved from Strava (for new users)
    def exchange_token(self, token):
        
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': token,
            'grant_type': 'authorization_code'
        }

        response = requests.post(url, data=payload)

        print(response.json())
        return response.json()

    # Used to refresh the token of existing athletes. 
    def get_refresh_token(self, refresh_token):
            
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(url, data=payload)

        print(response.json())

        return response.json()
    
    def unauthorized_request(self, athlete):
        url = "https://www.strava.com/oauth/deauthorize"
        headers = {
            'Authorization': f'Bearer {athlete["access_token"]}'
        }

        response = requests.post(url, headers=headers)

        print(response.json())
        return response.json()

    # Get all the activities of the athlete
    def get_activities(self, athlete):
        # IMPORTANT: even though we refresh the tokens at bot startup, we also have to refresh them here
        # It could happen that a token expires between bot startup and first user command. 
        self.update_refresh_token(athlete)
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {
            'Authorization': f'Bearer {athlete["access_token"]}'
        }

        response = requests.get(url, headers=headers)
        return response.json()