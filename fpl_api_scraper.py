# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 17:14:35 2021

@author: Yukthi Wickramarachchi
"""

import pandas as pd
import re
import requests
import time

def fpl_scraper():
    has_next = True
    i = 1
    player_df = pd.DataFrame()
    player_names = []
    player_basic_reponse = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    player_names = [[i['id'], i['first_name'],i['web_name']] for i in player_basic_reponse.json()['elements']]
    player_names_df = pd.DataFrame(player_names, columns = ['id', 'first_name', 'last_name'])
    while has_next:
        player_details_response = requests.get("https://fantasy.premierleague.com/api/element-summary/" + str(i) + "/")      
        player_history_df = pd.DataFrame(player_details_response.json()['history'])[['element',
                                                                    'fixture',
                                                                    'opponent_team',
                                                                    'total_points',
                                                                    'was_home',
                                                                    'round',
                                                                    'minutes',
                                                                    'value']]
        player_df = pd.concat([player_df, player_history_df], axis = 0)
        i = i + 1
        if requests.get("https://fantasy.premierleague.com/api/element-summary/" + str(i) + "/").status_code == 404:
            has_next = False
        time.sleep(2)
    
    player_df = player_df.merge(player_names_df, how = 'left', left_on = 'element', right_on = 'id')
    player_df.to_csv("C:\\Users\\Sama\Documents\\Yukthi's_Work\\2021-2022_player_fpl_data.csv")