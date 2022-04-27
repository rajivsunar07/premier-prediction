import pandas as pd
import requests
import json

def get_fixtures_data():
    baseUri = "https://fantasy.premierleague.com/api"


    f = requests.get("{}/fixtures/".format(baseUri))
    fixtures_json = f.json()

    fixtures_df = pd.DataFrame(fixtures_json)

    cleaned_fixtures_df =  fixtures_df[
        [
            'event', 'finished', 'id', 'kickoff_time',
            'started', 'team_a', 'team_a_score', 'team_h', 'team_h_score',
            'stats', 'team_h_difficulty', 'team_a_difficulty'
        ]
        ].copy()
    
    return cleaned_fixtures_df

def get_team_data():

    baseUri = "https://fantasy.premierleague.com/api"

    r = requests.get("{}/bootstrap-static/".format(baseUri))
    teams_data = r.json()

    teams_df = pd.DataFrame(teams_data['teams'])

    cleaned_teams_data = teams_df[
        [
            'id', 'name', 'short_name'
        ]
    ]

    return cleaned_teams_data

