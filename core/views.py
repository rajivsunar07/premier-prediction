from asyncio.base_futures import _FINISHED
from re import A
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import Fixtures, Teams

import pandas as pd
import numpy as np

from analysisandprediction import data_extraction, data_wrangling, training_model, prediction

# Create your views here.
def home(request):

    ''' Fill in new data '''
    # fixtures data
    all_fixtures = Fixtures.objects.all()
    
    new_data = pd.DataFrame()
    new_data = data_extraction.get_fixtures_data()
    
    if all_fixtures.count() == 0:
        processed_data = pd.DataFrame()
        processed_data = data_wrangling.data_wrangling(new_data)
        processed_data_finished = processed_data[processed_data['finished']==True].copy()
        training_model.logistic_modelling(processed_data_finished)

        for index, rows in processed_data.iterrows():
            data = rows.to_dict()
            f = Fixtures(**data)
            f.save()
        
        teams_data = data_extraction.get_team_data()

        for index, rows in teams_data.iterrows():
            team = rows.to_dict()
            t = Teams(**team)
            t.save()

    else:
        new_data_finished = new_data[new_data['finished']==True]
        finished_fixtures = Fixtures.objects.filter(finished = True)


        if new_data_finished.shape[0] != finished_fixtures.count():
            processed_data = data_wrangling.data_wrangling(new_data)


            for index, rows in processed_data.iterrows():
                data = rows.to_dict()
                f = Fixtures(**data)
                f.save()
        

    unfinished_fixtures = Fixtures.objects.filter(finished = False)
    event = unfinished_fixtures[0].event

    upcoming_fixtures = Fixtures.objects.filter(finished = False, event = event)

    ''' Get the upcoming fixtures list '''
    # teams_list = []
    # upcoming_fixtures = []

    # for fixture in unfinished_fixtures:
    #     if len(teams_list) <= 20:
    #         team_a = fixture.team_a
    #         team_h = fixture.team_h

    #         if team_a not in teams_list or team_h not in teams_list :
    #             upcoming_fixtures.append(fixture)
                
    #         if team_a not in teams_list:
    #             teams_list.append(team_a)
            
    #         if team_h not in teams_list:
    #             teams_list.append(team_h)

    for fixture in upcoming_fixtures:
        team_a = Teams.objects.get(id = fixture.team_a)
        team_h = Teams.objects.get(id = fixture.team_h)

        fixture.team_a = team_a
        fixture.team_h = team_h

    context = {
        'fixtures': upcoming_fixtures
    }

    return render(request, 'core/upcoming_matches.html', context)


def match_detail(request, id):
    fixtures = Fixtures.objects.filter(id=id).values()
    fixture_df = pd.DataFrame(list(fixtures))


    clean_df = fixture_df.drop(['event', 'finished', 'id', 'kickoff_time', 'started', 'team_a', 'team_a_score', 'team_h', 'team_h_score', 'stats', 'ftr'], axis=1).copy()

    predicted_result = prediction.predict(clean_df)

    fixture = Fixtures.objects.get(id = id)
    team_a = Teams.objects.get(id = fixture.team_a)
    team_h = Teams.objects.get(id = fixture.team_h)

    result = ''
    draw = False
    if predicted_result[0][0] == 'a':
        result = team_a.name
    elif predicted_result[0][0] == 'h':
        result = team_h.name
    else:
        result = "draw"
        draw = True

    # get the form
    # for home team
    last_five_results_h = Fixtures.objects.filter(Q(team_a=fixture.team_h, finished=True)  |  Q(team_h=fixture.team_h,  finished=True)).order_by('-event')[:5]
    form_h = []
    for last_result in last_five_results_h:
        if last_result.ftr == 'h':
            form_h.append('W')
        elif last_result.ftr == 'a':
            form_h.append('L')
        elif last_result.ftr == 'd':
            form_h.append('D')

    # for away team
    last_five_results_a = Fixtures.objects.filter(Q(team_a=fixture.team_a, finished=True)  |  Q(team_h=fixture.team_a, finished=True)).order_by('-event')[:5]
    form_a = []
    for last_result in last_five_results_a:
        if last_result.ftr == 'a':
            form_a.append('W')
        elif last_result.ftr == 'h':
            form_a.append('L')
        elif last_result.ftr == 'd':
            form_a.append('D')
  
    # goals scored for 
    # home
    goals_when_home_h = Fixtures.objects.filter(team_h=fixture.team_h, finished=True).values('team_h_score')
    goals_when_away_h = Fixtures.objects.filter(team_a=fixture.team_h, finished=True).values('team_a_score')

    goals_h = 0
    for goal in goals_when_home_h:
        goals_h += int(goal['team_h_score'])
    for goal in goals_when_away_h:
        goals_h += int(goal['team_a_score'])

    # away
    goals_when_home_a = Fixtures.objects.filter(team_h=fixture.team_a, finished=True).values('team_h_score')
    goals_when_away_a = Fixtures.objects.filter(team_a=fixture.team_a, finished=True).values('team_a_score')

    goals_a = 0
    for goal in goals_when_home_a:
        goals_a += int(goal['team_h_score'])
    for goal in goals_when_away_a:
        goals_a += int(goal['team_a_score'])

    # goals conceeded for
    #home
    conceeded_when_home_h = Fixtures.objects.filter(team_h=fixture.team_h, finished=True).values('team_a_score')
    conceeded_when_away_h = Fixtures.objects.filter(team_a=fixture.team_h, finished=True).values('team_h_score')

    conceeded_h = 0
    for conceeded in conceeded_when_home_h:
        conceeded_h += int(conceeded['team_a_score'])
    for conceeded in conceeded_when_away_h:
        conceeded_h += int(conceeded['team_h_score'])

    # away
    conceeded_when_home_a = Fixtures.objects.filter(team_h=fixture.team_a, finished=True).values('team_a_score')
    conceeded_when_away_a = Fixtures.objects.filter(team_a=fixture.team_a, finished=True).values('team_h_score')

    conceeded_a = 0
    for conceeded in conceeded_when_home_a:
        conceeded_a += int(conceeded['team_a_score'])
    for conceeded in conceeded_when_away_a:
        conceeded_a += int(conceeded['team_h_score'])
    

    context = {
        'fixture': fixture,
        'team_a': team_a,
        'team_h': team_h,
        'result': result,
        'form_h': form_h,
        'form_a': form_a,
        'goals_h': goals_h,
        'goals_a': goals_a,
        'conceeded_h': conceeded_h,
        'conceeded_a': conceeded_a,
        'draw': draw

    }
    return render(request, 'core/match_detail.html', context)
