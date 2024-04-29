import requests
import argparse
import json
from datetime import datetime
import time

abbreviations = [
    # States
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA",
    "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO",
    "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI",
    "WV", "WY",
    # Federal district
    "DC",
    # Inhabited territories
    "AS", "GU", "MP", "PR", "VI",
]

def date_to_unix_timestamp(date_str):
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    unix_timestamp = int(time.mktime(date_obj.timetuple()))
    return unix_timestamp

def fetch_state_data(state, base_url_vote, base_url_api):
    full_vote_org_url = base_url_vote + state.lower()
    params = {"url": full_vote_org_url, "links": "true", "title": "true"}
    response = requests.get(base_url_api, params=params).text.split("\n")
    while "last updated" not in response[-1].lower():
        response.pop()
    last_updated_str = response[-1].split("Last Updated: ")[-1]
    last_updated = date_to_unix_timestamp(last_updated_str)
    response.pop()
    if "other ways to register" in str(response).lower():
        while "other ways to register" not in response[-1].lower():
            response.pop(-1)
        response.pop(-1)
        response.pop(-1)
    markdown_content = '\n'.join(response) + "\n\n"
    return markdown_content, last_updated

def setup(start_state=None):
    base_url_vote = "https://vote.gov/register/"
    base_url_api = "https://urltomarkdown.herokuapp.com/"
    state_data = {}
    if start_state and start_state in abbreviations:
        start_index = abbreviations.index(start_state)
    else:
        start_index = 0

    print("Starting data collection for all states from", abbreviations[start_index], "onwards...")
    with open("all_states_data.md", "a" if start_state else "w") as md_file, open("last_updated.json", "r+" if start_state else "w") as json_file:
        if start_state:
            state_data = json.load(json_file)
            json_file.seek(0)
            json_file.truncate()

        for state in abbreviations[start_index:]:
            print(f"Fetching data for {state}...")
            markdown_content, last_updated = fetch_state_data(state, base_url_vote, base_url_api)
            state_data[state] = last_updated
            md_file.write(markdown_content)
            md_file.flush()
            json.dump(state_data, json_file)
            json_file.flush()
            print(f"Data for {state} fetched, processed, and written to files.")
    print("Setup complete.")

def validate():
    base_url_vote = "https://vote.gov/register/"
    base_url_api = "https://urltomarkdown.herokuapp.com/"
    mismatches = []
    print("Validating data against saved timestamps...")
    with open("last_updated.json", "r") as file:
        saved_data = json.load(file)
    for state, saved_timestamp in saved_data.items():
        print(f"Checking {state}...")
        _, current_timestamp = fetch_state_data(state, base_url_vote, base_url_api)
        if current_timestamp != saved_timestamp:
            mismatches.append(state)
            print(f"Data mismatch found for {state}.")
    if mismatches:
        print("States with updated registration information:", ", ".join(mismatches))
    else:
        print("No updates found. All states are up to date.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage state registration data")
    parser.add_argument('action', type=str, choices=['setup', 'validate'])
    parser.add_argument('-start', '--start_state', type=str, help='Optional starting state abbreviation for setup')
    args = parser.parse_args()
    if args.action == 'setup':
        setup(args.start_state)
    elif args.action == 'validate':
        validate()