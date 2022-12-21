# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:57:09 2021

@author: Yukthi Wickramarachchi
"""

import fpl_fbref_scraper
import tkinter
from tkinter import filedialog


def analyze_only():
    root = tkinter.Tk()
    root.withdraw()
    root.filename = filedialog.askopenfilenames(title= "Select the player_gw csv")
    player_gw_path = root.filename
    root.filename = filedialog.askopenfilenames(title= "Select fpl_gw csv")
    fpl_gw_path = root.filename
    root.filename = filedialog.askopenfilenames(title= "Select players_raw csv")
    players_raw_path = root.filename
    root.filename = filedialog.askdirectory(title= "Select players_raw csv")
    teams_path = root.filename
    year = input("input year\n")
    fpl.create_csv(player_gw_path[0], fpl_gw_path[0], players_raw_path[0], teams_path, year)
