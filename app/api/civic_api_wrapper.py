import requests
from .clients import GOOGLE_API_KEY
import json
from datetime import datetime

BASE_URL = "https://www.googleapis.com/civicinfo/v2/"

def get_elections():
    payload = {"key": GOOGLE_API_KEY}

    response = requests.get(BASE_URL+"elections", params=payload)
    return response.json()['elections']

def get_voter_info(address, electionId):
    payload = {"key": GOOGLE_API_KEY, "address": address, "electionId": electionId}

    response = requests.get(BASE_URL+"voterinfo", params=payload)

    response_json = response.json()

    if 'pollingLocations' not in response_json:
        return "COULD NOT FIGURE OUT WHETHER ADDRESS IS ELIGIBLE TO VOTE. What follows is the relevant authority's election office info so that the user can find out more through official's websites: " + str(response_json)
    
    return response.json()

def get_elected_representatives(address):
    payload = {"key": GOOGLE_API_KEY, "address": address}

    response = requests.get(BASE_URL+"representatives", params=payload)

    return response.json()


def updateElections():

    try:
        f = open("elections.json", "r")
    except:
        f = open("api/elections.json", "r")

    elections_data = json.load(f)

    f.close()

    today = datetime.today().strftime('%Y-%m-%d')

    if elections_data["updated"] != today:
        # Otherwise use Google API to fetch current elections and update the updated date
        print("Updating elections data..")
        elections_upcoming = get_elections()
        elections_data["elections"] = elections_upcoming
        elections_data["updated"] = today

        try:
            f = open("api/elections.json", "w")
        except:
            f = open("elections.json", "w")


        json.dump(elections_data, f)
        print("Wrote to json file")
        f.close()
    
    return elections_data