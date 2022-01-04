# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 14:03:16 2020

@author: Yukthi
"""

import pandas as pd
import numpy as np
import glob
import re

def create_csv(player_gw_dir, fpl_gw_dir, players_raw_dir, teams_folder, year):
    player_gw = pd.read_csv("C:\\Users\\Sama\\Documents\\Yukthi's_Work\\player_gameweeks_2020-2021.csv")
    fpl_gw = pd.read_csv("C:\\Users\\Sama\\Documents\\Yukthi's_Work\\FPL\\New_data\\2021\\merged_gw.csv")
    players_raw = pd.read_csv("C:\\Users\\Sama\\Documents\\Yukthi's_Work\\FPL\\New_data\\2021\\players_raw.csv")
    
    players_raw['name'] = players_raw['first_name'] +" "+ players_raw['second_name']
    player_gw['Round'] = player_gw['Round'].str.replace("Matchweek ", "")
    player_gw['Round'] = player_gw['Round'].astype('int32')
    
    fpl_gw = fpl_gw.rename(columns = {'GW':'Round'})
    
    fpl_gw['Round'] =fpl_gw['Round'].apply(lambda x: x-9 if x>29 else x)
    fpl_gw['name'] = fpl_gw['name'].str.replace('_'," ")
    fpl_gw['name'] = fpl_gw['name'].str.replace('\d+', '')
    fpl_gw['name'] = fpl_gw['name'].str.strip()
    player_gw = player_gw.merge(players_raw, on = 'name')
    
    merged_df = player_gw.merge(fpl_gw, how='inner', on=['name', 'Round'])
    merged_df = merged_df.replace('On matchday squad, but did not play',0)
    numerical_player_cols = ['Min', 'Gls', 'Ast', 'PK', 'PKatt',
           'Sh', 'SoT', 'CrdY', 'CrdR', 'Touches', 'Press', 'Tkl', 'Int', 'Blocks',
           'xG', 'npxG', 'xA', 'SCA', 'GCA', 'Cmp', 'Att', 'Cmp%', 'PrgDist',
           'Carries', 'PrgDist.1', 'Succ', 'Att.1']
    
    merged_df[numerical_player_cols]= merged_df[numerical_player_cols].astype('float64')
    
    numerical_player_over_last_5 = merged_df.groupby(['name'])[numerical_player_cols].shift(1).rolling(5).mean()
    numerical_player_over_last_5 = numerical_player_over_last_5.dropna()
    merged_df = merged_df.join(numerical_player_over_last_5, rsuffix="_last_5")
    merged_df = merged_df[merged_df['Min_last_5'].notna()]
    
    numerical_player_totals = merged_df.groupby('name')[numerical_player_cols].shift(1).rolling(5).sum()
    numerical_player_totals = numerical_player_totals.dropna()
    merged_df = merged_df.join(numerical_player_totals, rsuffix="_total")
    merged_df = merged_df[merged_df['Min_total'].notna()]
    
    
    
    
    path = "C:\\Users\\Sama\Documents\\Yukthi's_Work\\FPL\\New_data\\2021\\Team"
    all_files = glob.glob(path + "/*.csv")
    li = []   
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        team_name = re.search('understat_(.+)\.csv', filename).group(1)
        team_name = team_name.replace("_", " ")
        df['Squad'] = team_name
        df['Round'] = np.arange(df.shape[0])+1
        li.append(df)
    
    team_frame = pd.concat(li, axis=0, ignore_index=True)
    team_frame['ppda'] =team_frame['ppda'].map(eval)
    team_frame[['ppda_att', 'ppda_def']] = pd.json_normalize(team_frame['ppda'])
    
    team_frame['ppda_allowed'] =team_frame['ppda_allowed'].map(eval)
    team_frame[['ppda_allowed_att', 'ppda_allowed_def']] = pd.json_normalize(team_frame['ppda_allowed'])
    
    numerical_team_cols = ['Squad', 'deep', 'deep_allowed','missed',
           'npxG', 'npxGA','ppda_att',
           'ppda_def', 'ppda_allowed_att', 'ppda_allowed_def' ]
    
    numerical_team_over_last_5 = team_frame[numerical_team_cols]
    # df.groupby('id')['x'].apply(pd.rolling_mean, 2, min_periods=1)
    numerical_team_over_last_5 = numerical_team_over_last_5.groupby('Squad').shift(1).rolling(5).mean()
    team_frame = team_frame.join(numerical_team_over_last_5, rsuffix="_over_5")
    numerical_team_over_last_5 = numerical_team_over_last_5.add_suffix('_rolling')
    
    team_cols = ['Squad', 'Round','deep_over_5',
           'deep_allowed_over_5', 'missed_over_5', 'npxG_over_5', 'npxGA_over_5',
           'ppda_att_over_5', 'ppda_def_over_5', 'ppda_allowed_att_over_5',
           'ppda_allowed_def_over_5']
    team_frame = team_frame[team_frame['Round']>5]
    team_frame['Squad'] = team_frame['Squad'].replace({'Leeds':'Leeds United', 'Newcastle United':'Newcastle Utd',
                                                   'Sheffield United':'Sheffield Utd', 'West Bromwich Albion': 'West Brom',
                                                  'Manchester United' : 'Manchester Utd', 'Wolverhampton Wanderers':'Wolves',
                                                   'Leicester':'Leicester City'})
    merged_df = merged_df.merge(team_frame[team_cols],how = 'left',  on = ['Squad', 'Round'])
    merged_df = merged_df.merge(team_frame[team_cols], how = 'left', left_on=['Opponent', 'Round'], right_on =['Squad', 'Round'], suffixes=[None,'_opp'])
    merged_df = merged_df[merged_df['deep_over_5'].notna()]
    merged_df = merged_df[merged_df['deep_over_5_opp'].notna()]
    
    
    
    merged_df = merged_df.sort_values(['name','Round'])
    important_cols = ['name','element_type', 'Round','Squad', 'Opponent', 'total_points_y', 'Min_last_5',
                  'Gls_last_5', 'Ast_last_5', 'PK_last_5', 'PKatt_last_5', 'Sh_last_5', 'SoT_last_5',
                  'CrdY_last_5', 'CrdR_last_5', 'Touches_last_5', 'Press_last_5', 'Tkl_last_5', 'Int_last_5',
                  'Blocks_last_5', 'xG_last_5', 'npxG_last_5', 'xA_last_5', 'SCA_last_5', 'GCA_last_5', 'Cmp_last_5',
                  'Att_last_5', 'Cmp%_last_5', 'PrgDist_last_5', 'Carries_last_5', 'PrgDist.1_last_5', 'Succ_last_5',
                  'Att.1_last_5', 'Min_total', 'Gls_total', 'Ast_total', 'PK_total', 'PKatt_total',
                  'Sh_total', 'SoT_total', 'CrdY_total', 'CrdR_total', 'Touches_total', 'Press_total', 'Tkl_total',
                  'Int_total', 'Blocks_total', 'xG_total', 'npxG_total', 'xA_total', 'SCA_total', 'GCA_total', 'Cmp_total',
                  'Att_total', 'Cmp%_total', 'PrgDist_total', 'Carries_total', 'PrgDist.1_total', 'Succ_total', 'Att.1_total','deep_over_5_opp',
                  'deep_allowed_over_5_opp', 'missed_over_5_opp',    'npxG_over_5_opp', 'npxGA_over_5_opp', 'ppda_att_over_5_opp',
                  'ppda_def_over_5_opp', 'ppda_allowed_att_over_5_opp', 'ppda_allowed_def_over_5_opp','deep_over_5',
                  'deep_allowed_over_5', 'missed_over_5', 'npxG_over_5', 'npxGA_over_5', 'ppda_att_over_5', 'ppda_def_over_5']
    model_df = merged_df[important_cols]
    model_df['element_type'] = model_df['element_type'].map({1:'G',2:'D',3:'M',4:'F'})
    
    model_df.to_csv("fpl_stats_" + '2020-2021'+ ".csv")
