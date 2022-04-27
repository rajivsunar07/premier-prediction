import pandas as pd
import numpy as np
from scipy.stats import poisson

def set_ftr(row):
    if row['team_a_score'] > row ['team_h_score']:
        return 'a'
    elif row['team_a_score'] < row ['team_h_score']:
        return 'h'
    elif row['team_a_score'] == row ['team_h_score']:
        return 'd'

def get_wld(team, date, cleaned_fixtures_df):
    win_count = 0

    before_ = cleaned_fixtures_df[(cleaned_fixtures_df['kickoff_time'] < date)]

    # result before the given date
    before_away = before_[before_['team_a'] == team]
    before_home = before_[before_['team_h'] == team]

    # wins when team is away and home
    wins_away = before_away[before_away['team_a_score'] > before_away['team_h_score']]
    wins_home = before_home[before_home['team_h_score'] > before_home['team_a_score']]

    # loss when team is away and home
    loss_away = before_away[before_away['team_a_score'] < before_away['team_h_score']]
    loss_home = before_home[before_home['team_h_score'] < before_home['team_a_score']]

    # draw when team is away and home
    draw_away = before_away[before_away['team_a_score'] == before_away['team_h_score']]
    draw_home = before_home[before_home['team_h_score'] == before_home['team_a_score']]

    # latest 3 away games
    count = -3
    form = 0
    if len(before_away.index) < 3 :
        count = -abs(len(before_away.index))

    if count != 0:
        form_away = before_away[count:]
        form_home = before_home[count:]

        wins_away_form = form_away[form_away['team_a_score'] > form_away['team_h_score']]
        draw_away_form = form_away[form_away['team_a_score'] < form_away['team_h_score']]

        wins_home_form = form_home[form_home['team_h_score'] > form_home['team_a_score']]
        draw_home_form = form_home[form_home['team_h_score'] < form_home['team_a_score']]

        form_away = (len(wins_away_form.index) * 3) + (len(draw_away_form)) 
        form_home = (len(wins_home_form.index) * 3) + (len(draw_home_form)) 

        form = form_away + form_home

    win_count = len(wins_away.index) + len(wins_home.index)
    loss_count = len(loss_away.index) + len(loss_home.index)
    draw_count = len(draw_away.index) + len(draw_home.index)

    # before_ = cleaned_fixtures_df[(cleaned_fixtures_df['kickoff_time']<date) and ((cleaned_fixtures_df['team_a'] == team) or (cleaned_fixtures_df['team_h'] == team)) ].copy()
    return win_count, loss_count, draw_count, form

def past_win(home, away, cleaned_fixtures_df):
    # if they have played once
    past = cleaned_fixtures_df[(cleaned_fixtures_df['team_a'] == home) & (cleaned_fixtures_df['team_h'] == away)]

    if len(past.index) == 0:
        return 0, 0, 0, 0, 0, 0
    
    wins_away = past[past['team_a_score'] > past['team_h_score']]
    wins_home = past[past['team_h_score'] > past['team_a_score']]

    loss_away = past[past['team_a_score'] < past['team_h_score']]
    loss_home = past[past['team_h_score'] < past['team_a_score']]

    draw_away = past[past['team_a_score'] == past['team_h_score']]
    draw_home = past[past['team_h_score'] == past['team_a_score']]

    return len(wins_away.index), len(wins_home.index), len(loss_away.index), len(loss_home.index), len(draw_away.index), len(draw_home.index)

def get_goals_pg(team, date, event, fixtures):

    before_ = fixtures[(fixtures['kickoff_time'] < date)]

    # how many goals were scored before that match
    away_matches = before_[(before_['team_a'] == team)]
    away_goals_f = away_matches['team_a_score'].sum()
    away_goals_a = away_matches['team_h_score'].sum()
    away_played = len(away_matches.index)
    
    # how many goals were conceded before that match
    home_matches =  before_[(before_['team_h'] == team)]
    home_goals_f = home_matches['team_h_score'].sum()
    home_goals_a = home_matches['team_a_score'].sum()
    home_played = len(home_matches.index)

    # # all matches before that event 
    events = fixtures[(fixtures['event'] < event)]
    total_goals_a = events['team_a_score'].sum() 
    total_goals_h = events['team_h_score'].sum()

    total_matches = len(events.index)
    average_a_f = total_goals_a/total_matches
    average_a_a = total_goals_h/total_matches

    average_h_f = total_goals_h/total_matches
    average_h_a = total_goals_a/total_matches

    away_goals_f_pg = away_goals_f/away_played
    away_goals_a_pg = away_goals_a/away_played

    home_goals_f_pg = home_goals_f/home_played
    home_goals_a_pg = home_goals_a/home_played

    if(str(home_goals_f_pg) == 'nan' or str(home_goals_a_pg) == 'nan' or str(away_goals_f_pg) == 'nan' or str(away_goals_a_pg) == 'nan' ):
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    atk_h = home_goals_f_pg/average_h_f
    dfn_h = home_goals_a_pg/average_h_a

    atk_a = away_goals_f_pg/average_a_f
    dfn_a = away_goals_a_pg/average_a_a

       
    if(str(atk_h) == 'nan' or str(dfn_h) == 'nan' or str(atk_a) == 'nan' or str(dfn_a) == 'nan' or str(home_goals_f_pg) == 'nan' or str(away_goals_f_pg) == 'nan'):
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    
   
    return atk_h, dfn_h, atk_a, dfn_a, home_goals_f_pg, away_goals_f_pg
    

def get_goals_probability(lambd):
    k_axis = np.arange(0, 6)
    distribution = np.zeros(k_axis.shape[0])

    for i in range(k_axis.shape[0]):
        distribution[i] = poisson.pmf(i, lambd)

    sorted = distribution.copy()
    sorted.sort()
    highest, second, third = sorted[-1], sorted[-2], sorted[-3]
    highest_at, second_at, third_at = np.where(distribution == highest), np.where(distribution == second), np.where(distribution == third)
    highest_goal, second_goal, third_goal = k_axis[highest_at][0], k_axis[second_at][0], k_axis[third_at][0]

    return highest_goal, highest, second_goal, second, third_goal, third


## data wrangling
def data_wrangling(cleaned_fixtures_df):
    cleaned_fixtures_df = cleaned_fixtures_df.assign(ftr=cleaned_fixtures_df.apply(set_ftr, axis=1))

    cleaned_fixtures_df['team_a_wins'] = 0
    cleaned_fixtures_df['team_h_wins'] = 0

    cleaned_fixtures_df['team_a_loss'] = 0
    cleaned_fixtures_df['team_h_loss'] = 0

    cleaned_fixtures_df['team_a_draw'] = 0
    cleaned_fixtures_df['team_h_draw'] = 0

    cleaned_fixtures_df['team_a_form'] = 0
    cleaned_fixtures_df['team_h_form'] = 0


    for index, row in cleaned_fixtures_df.iterrows():
        win_away, loss_away, draw_away, form_away = get_wld(row["team_a"], row["kickoff_time"], cleaned_fixtures_df)

        cleaned_fixtures_df.loc[[index], 'team_a_wins'] = win_away
        cleaned_fixtures_df.loc[[index], 'team_a_loss'] = loss_away
        cleaned_fixtures_df.loc[[index], 'team_a_draw'] = draw_away
        cleaned_fixtures_df.loc[[index], 'team_a_form'] = form_away


        win_home, loss_home, draw_home, form_home = get_wld(row["team_h"], row["kickoff_time"], cleaned_fixtures_df)

        cleaned_fixtures_df.loc[[index], 'team_h_wins'] = win_home
        cleaned_fixtures_df.loc[[index], 'team_h_loss'] = loss_home
        cleaned_fixtures_df.loc[[index], 'team_h_draw'] = draw_home
        cleaned_fixtures_df.loc[[index], 'team_h_form'] = form_home


    cleaned_fixtures_df['past_a_wins'] = 0
    cleaned_fixtures_df['past_h_wins'] = 0

    cleaned_fixtures_df['past_a_loss'] = 0
    cleaned_fixtures_df['past_h_loss'] = 0

    cleaned_fixtures_df['past_a_draw'] = 0
    cleaned_fixtures_df['past_h_draw'] = 0

     
    for index, row in cleaned_fixtures_df.iterrows():
        w_a, w_h, l_a, l_h, d_a, d_h =  past_win(row["team_h"], row["team_a"], cleaned_fixtures_df)

        cleaned_fixtures_df.loc[[index], 'past_a_wins'] = w_a
        cleaned_fixtures_df.loc[[index], 'past_h_wins'] = w_h
        cleaned_fixtures_df.loc[[index], 'past_a_loss'] = l_a
        cleaned_fixtures_df.loc[[index], 'past_h_loss'] = l_h
        cleaned_fixtures_df.loc[[index], 'past_a_draw'] = d_a
        cleaned_fixtures_df.loc[[index], 'past_h_draw'] = d_h

    cleaned_fixtures_df['exp_goals_h'] = 0.0
    cleaned_fixtures_df['exp_goals_a'] = 0.0

    for index, row in cleaned_fixtures_df.iterrows():
        atk_h1, dfn_h1, atk_a1, dfn_a1, home_goals_f_pg1, away_goals_f_pg1 = get_goals_pg(row["team_h"], row["kickoff_time"], row['event'], cleaned_fixtures_df)
        atk_h2, dfn_h2, atk_a2, dfn_a2, home_goals_f_pg2, away_goals_f_pg2 = get_goals_pg(row["team_a"], row["kickoff_time"], row['event'], cleaned_fixtures_df)

        cleaned_fixtures_df.loc[[index], 'exp_goals_h'] = atk_h1 * dfn_a2 * home_goals_f_pg1
        cleaned_fixtures_df.loc[[index], 'exp_goals_a'] = atk_a2 * dfn_h1 * away_goals_f_pg2

    cleaned_fixtures_df['highest_goal_a']  = 0.0
    cleaned_fixtures_df['highest_a'] = 0.0
    cleaned_fixtures_df['second_goal_a'] = 0.0
    cleaned_fixtures_df['second_a'] = 0.0
    cleaned_fixtures_df['third_goal_a'] = 0.0
    cleaned_fixtures_df['third_a'] = 0.0

    cleaned_fixtures_df['highest_goal_h']  = 0.0
    cleaned_fixtures_df['highest_h'] = 0.0
    cleaned_fixtures_df['second_goal_h'] = 0.0
    cleaned_fixtures_df['second_h'] = 0.0
    cleaned_fixtures_df['third_goal_h'] = 0.0
    cleaned_fixtures_df['third_h'] = 0.0

    for index, row in cleaned_fixtures_df.iterrows():
        highest_goal, highest, second_goal, second, third_goal, third = get_goals_probability(row["exp_goals_a"])

        cleaned_fixtures_df.loc[[index], 'highest_goal_a'] = highest_goal
        cleaned_fixtures_df.loc[[index], 'highest_a'] = highest
        cleaned_fixtures_df.loc[[index], 'second_goal_a'] = second_goal
        cleaned_fixtures_df.loc[[index], 'second_a'] = second
        cleaned_fixtures_df.loc[[index], 'third_goal_a'] = third_goal
        cleaned_fixtures_df.loc[[index], 'third_a'] = third


        highest_goal, highest, second_goal, second, third_goal, third = get_goals_probability(row["exp_goals_h"])

        cleaned_fixtures_df.loc[[index], 'highest_goal_h'] = highest_goal
        cleaned_fixtures_df.loc[[index], 'highest_h'] = highest
        cleaned_fixtures_df.loc[[index], 'second_goal_h'] = second_goal
        cleaned_fixtures_df.loc[[index], 'second_h'] = second
        cleaned_fixtures_df.loc[[index], 'third_goal_h'] = third_goal
        cleaned_fixtures_df.loc[[index], 'third_h'] = third

    # completed_cleaned_fixtures_df = cleaned_fixtures_df[cleaned_fixtures_df['finished']==True].copy()
    # cleaned_fixtures_df.to_csv('cleaned_fixtures.csv')
    return cleaned_fixtures_df
    