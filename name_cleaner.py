# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 18:03:31 2022

@author: Yukthi Wickramarachchi
"""
import pandas as pd
import numpy as np


def clean_names(player_data, fpl_data):
    player_data = "Data/player_gameweeks_2021-2022.csv"
    fpl_data = "Data/2021-2022_player_fpl_data.csv"
    player_df = pd.read_csv(player_data)
    fpl_df = pd.read_csv(fpl_data)

    # Uneeded for now, will see if required in future. Keep.
    # name_map = {"Ãº": "u",
    #             "Ã©": "e",
    #             "Ã­": "i",
    #             "Ã¶": "o",
    #             "ÃŸ": "s",
    #             "Ã«": "e",
    #             "Ã¡": "e",
    #             "Ã¸": "o",
    #             "Ã³": "o",
    #             "ÄŸ": "g",
    #             "ÅŸ": "c",
    #             "Ã¼": "u",
    #             "Å‚": "l",
    #             "Ã£": "a"}

    player_df['last_name'] = player_df['name'].str.split().str[-1]
    combined_df = pd.merge(fpl_df, player_df, on='last_name', how='left')
    features = ['round', 'Squad', 'opponent_team', 'was_home', 'total_points',
                'minutes', 'value', 'last_name', 'Pos', 'xG', 'xA', 'PSxG']
    combined_df.columns
    combined_df.to_csv("Data/combined_2022.csv")