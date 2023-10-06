# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 14:03:16 2020

@author: Yukthi
"""

import pandas as pd
import glob
import re

def create_csv():
       outfield = pd.read_csv("Data/Outfield Players 2021-2022.csv")
       goalkeepers = pd.read_csv("Data/Goalkeepers 2021-2022.csv")
       team_attacking = pd.read_csv("Data/teams_offence.csv")
       team_defending = pd.read_csv("Data/teams_defence.csv")
       fpl_gw = pd.read_csv("Data/fpl_gw_2021_2022.csv")
       fpl_gw_cols = ['name', 'position', 'team', 'minutes', 'opponent_team', 'value', 'GW', 'was_home', 'total_points']
       numerical_outfield_cols = ['Min', 'xG', 'xA', 'Touches']
       numerical_goalkeeper_cols = ['Min', 'PSxG']

       # Cleaning columns
       fpl_gw = fpl_gw[fpl_gw_cols]
       outfield = outfield.rename(columns= {'Name':'name'})
       goalkeepers = goalkeepers.rename(columns= {'Name':'name'})
       outfield['Round'] = outfield['Round'].str.replace("Matchweek ", "").astype('int64')
       goalkeepers['Round'] = goalkeepers['Round'].str.replace("Matchweek ", "").astype('int64')
       fpl_gw = fpl_gw.rename(columns = {'GW':'Round'})
       outfield_fpl_gw = outfield.merge(fpl_gw, on = ['name', 'Round'])
       goalkeepers_fpl_gw = goalkeepers.merge(fpl_gw, on = ['name', 'Round'])
       

       outfield_fpl_gw = outfield_fpl_gw.replace('On matchday squad, but did not play',0)
       goalkeepers_fpl_gw = goalkeepers_fpl_gw.replace('On matchday squad, but did not play',0)

       outfield_fpl_gw[numerical_outfield_cols]= outfield_fpl_gw[numerical_outfield_cols].astype('float64')
       goalkeepers_fpl_gw[numerical_goalkeeper_cols]= goalkeepers_fpl_gw[numerical_goalkeeper_cols].astype('float64')

       #Feature Engineering
       numerical_player_over_last_5 = outfield_fpl_gw.groupby(['name'])[numerical_outfield_cols].shift(1).rolling(5).mean()
       numerical_player_over_last_5 = numerical_player_over_last_5.dropna()
       outfield_fpl_gw = outfield_fpl_gw.join(numerical_player_over_last_5, rsuffix="_last_5")
       outfield_fpl_gw = outfield_fpl_gw[outfield_fpl_gw['Min_last_5'].notna()]

       numerical_goalkeeper_over_last_5 = goalkeepers_fpl_gw.groupby(['name'])[numerical_goalkeeper_cols].shift(1).rolling(5).mean()
       numerical_goalkeeper_over_last_5 = numerical_goalkeeper_over_last_5.dropna()
       goalkeepers_fpl_gw = goalkeepers_fpl_gw.join(numerical_goalkeeper_over_last_5, rsuffix="_last_5")
       goalkeepers_fpl_gw = goalkeepers_fpl_gw[goalkeepers_fpl_gw['Min_last_5'].notna()]
       # Team data
       numerical_team_cols = ['squad', 'xG']
       
       numerical_attacking_team_over_last_5 = team_attacking[numerical_team_cols]
       numerical_defending_team_over_last_5 = team_defending[numerical_team_cols]

       numerical_attacking_team_over_last_5 = numerical_attacking_team_over_last_5.groupby('squad').shift(1).rolling(5).mean()
       team_attacking = team_attacking.join(numerical_attacking_team_over_last_5, rsuffix="_over_5")

       numerical_defending_team_over_last_5 = numerical_defending_team_over_last_5.groupby('squad').shift(1).rolling(5).mean()
       team_defending = team_defending.join(numerical_defending_team_over_last_5, rsuffix="_over_5")


       team_cols = ['Squad', 'Round', 'xG_over_5']
       team_attacking = team_attacking[team_attacking['Round']>5]
       team_defending = team_defending[team_defending['Round']>5]

       team_attacking['Squad'] = team_attacking['squad'].replace({'Leeds':'Leeds United', 'Newcastle United':'Newcastle Utd',
                                                        'Sheffield United':'Sheffield Utd', 'West Bromwich Albion': 'West Brom',
                                                        'Manchester United' : 'Manchester Utd', 'Wolverhampton Wanderers':'Wolves',
                                                        'Leicester':'Leicester City'})
       team_defending['Squad'] = team_defending['squad'].replace({'Leeds':'Leeds United', 'Newcastle United':'Newcastle Utd',
                                                        'Sheffield United':'Sheffield Utd', 'West Bromwich Albion': 'West Brom',
                                                        'Manchester United' : 'Manchester Utd', 'Wolverhampton Wanderers':'Wolves',
                                                        'Leicester':'Leicester City'})


       outfield_fpl_gw = outfield_fpl_gw.merge(team_attacking[team_cols], how = 'left', on = ['Squad', 'Round'], suffixes= [None,'_att'])
       outfield_fpl_gw = outfield_fpl_gw.merge(team_defending[team_cols], how = 'left', on = ['Squad', 'Round'], suffixes= [None,'_def'])
       outfield_fpl_gw = outfield_fpl_gw.merge(team_attacking[team_cols], how = 'left', left_on = ['Opponent', 'Round'], right_on = ['Squad', 'Round'], suffixes=  [None,'_opp_att'])
       outfield_fpl_gw = outfield_fpl_gw.merge(team_defending[team_cols], how = 'left', left_on = ['Opponent', 'Round'], right_on = ['Squad', 'Round'], suffixes=  [None,'_opp_def'])
       goalkeepers_fpl_gw = goalkeepers_fpl_gw.merge(team_defending[team_cols], how = 'left', on = ['Squad', 'Round'], suffixes=  [None,'_def'])
       goalkeepers_fpl_gw = outfield_fpl_gw.merge(team_attacking[team_cols], how = 'left', left_on = ['Opponent', 'Round'], right_on = ['Squad', 'Round'], suffixes=  [None,'_opp_att'])

       outfield_fpl_gw = outfield_fpl_gw.rename(columns={'xG_over_5':'xG_over_5_att'})
       goalkeepers_fpl_gw = goalkeepers_fpl_gw.rename(columns={'xG_over_5':'xG_over_5_def'})
       # Selecting columns for analysis
       important_cols = ['name','position', 'Venue', 'Round','Squad', 'Opponent', 'total_points', 'Min_last_5',
       'xG_last_5', 'xA_last_5', 'xG_over_5_att', 'xG_over_5_def', 'xG_over_5_opp_att', 'xG_over_5_opp_def']
       goalkeeper_cols = ['name','Venue', 'Round','Squad', 'Opponent', 'total_points', 'Min_last_5', 'xG_over_5_def', 'xG_over_5_opp_att']
       
       outfield_model_df = outfield_fpl_gw[important_cols]
       goalkeeper_model_df = goalkeepers_fpl_gw[goalkeeper_cols]
       

       outfield_model_df.to_csv("Data/outfield_model_data" + '2021-2022'+ ".csv")
       goalkeeper_model_df.to_csv("Data/goalkeeper_model_data" + '2021-2022'+ ".csv")

if __name__ == '__main__':
       create_csv()