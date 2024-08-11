import os
import requests
from dotenv import load_dotenv

class StravaConnector:
    def __init__(self):
        # Load environment variables from a .env file
        load_dotenv()
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')


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

    def refresh_token(self, refresh_token):
            
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(url, data=payload)

        print(response.json())

    def get_activities(self, access_token):
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)
        return response.json()