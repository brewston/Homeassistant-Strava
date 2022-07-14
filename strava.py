import requests
import json
import time

# Follow this guide https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86
# to get the contents of strava_tokens dict
# The example code writes it out to a file but I found that appdaemon couldnt find it and it simple enough to maintain it within this code anyway.

class Strava(hass.Hass):

  
     
  def initialize(self):
      self.log("Strava Started")
      self.run_in(self.update, 0)
      # We only need to update every 10mins really. How often do you ride your bike ?
      self.run_every(self.update, datetime.datetime.now(), 600)

  def update(self, kwargs):
        self.log("Update Started")
        strava_tokens = {"token_type": "Bearer", "access_token": "REDACTED", "expires_at": 1652019185, "expires_in": 21600, "refresh_token": "REDACTED"}
       
        if strava_tokens['expires_at'] < time.time():
           #Make Strava auth API call with current refresh token
           response = requests.post(
                        url = 'https://www.strava.com/oauth/token',
                        data = {
                                'client_id': 16329,
                                'client_secret': 'REDACTED',
                                'grant_type': 'refresh_token',
                                'refresh_token': strava_tokens['refresh_token']
                                }
                    )
           #Save response as json in new variable
           new_strava_tokens = response.json()
           strava_tokens = new_strava_tokens

        url = "https://www.strava.com/api/v3/activities"
        access_token = strava_tokens['access_token']
        # Get your own athlete code from your profile 
        strava_athlete = '17692813'
        url = "https://www.strava.com/api/v3/athletes/" + strava_athlete + "/stats"
        r = requests.get(url + '?access_token=' + access_token)
        r = r.json()
        # Values returned are in meters, but I wanted miles so divide by 1609
        all_ride = round(int(r['all_ride_totals']['distance'])/1609)
        # Build the HA sensor entity with the value returned 
        entity = "sensor.strava_all_ride_totals"
        self.set_state(entity, state = all_ride)
        # Repeat for YTD stats
        ytd_ride = round(int(r['ytd_ride_totals']['distance'])/1609)
        entity = "sensor.strava_ytd_ride_totals"
        self.set_state(entity, state = ytd_ride)
       
        # The API is explained here : https://developers.strava.com/docs/reference/#api-Athletes-getStats
        # and its slightly limited in what you can get back, ie the all_time and YTD stats are ride, run & swim only.
        # If you wanted YTD walking stats (for example) you'd need more complex code to count up the miles walked per activity.
