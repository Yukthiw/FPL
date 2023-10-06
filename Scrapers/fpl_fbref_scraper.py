# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 19:18:22 2020
Updated on Sunday Dec 26, 2021

@author: Yukthi Wickramarachchi
"""
import sys
sys.path.append('..')
from bs4 import BeautifulSoup, Comment
import requests
import pandas as pd
import re
import Controllers.ScraperController as ScraperController

from Scrapers.scraper import Scraper


class FPLFbrefScraper(Scraper):
    
    def scrape(self):
        links = []
        player_cols = ['Name', 'Venue', 'Round', 'Squad', 'Opponent', 'Min', 'xG', 'xA', 'Touches']
        keeper_cols = ['Name', 'Venue', 'Round', 'Squad', 'Opponent', 'Min', 'PSxG']
        prefix = 'https://fbref.com/'
        player_df = pd.DataFrame({'A' : []})
        keeper_df = pd.DataFrame({'A' : []})
        source = requests.get(self.url)
        soup = BeautifulSoup(source.content, 'lxml')
        year_text = soup.find('div', {'id': 'info'}).find('h1').text.strip()
        year = re.search('(\d+-\d+)\s', year_text).group(1)
        placeholder = soup.select_one('#all_stats_standard .placeholder')
        comment = next(elem for elem in placeholder.next_siblings if isinstance(elem, Comment))
        table_soup = BeautifulSoup(comment, 'lxml')
        players = (table_soup.find('div', {'class': 'table_container'}))
        player_table = (players.find('tbody'))
        for row in player_table.find_all('tr'):
            if row.find('td', {'data-stat': 'player'}) is not None:
                link = prefix + ((row.find('td', {'data-stat': 'player'})).a.attrs['href'])
                position = row.find('td', {'data-stat': 'position'}).text
                links.append([link, position])


        for link in links:
            is_keeper = False
            temp_source = requests.get(link[0])
            temp_soup = BeautifulSoup(temp_source.content, 'lxml')
            name = temp_soup.find('h1').text
            if link[1] != 'GK':
                stat_type = 'summary'
            else:
                stat_type = 'keeper'
                is_keeper = True
            for li in (temp_soup.find_all('li', {'class': 'full hasmore'})):
                if li.span.text == 'Match Logs':
                    for a in li.find_all('a'):
                        if a.text == year:
                            temp_link = prefix + a['href']
                            temp_link = temp_link.replace('misc', stat_type)
                            break
                    break
            temp_source_2 = requests.get(temp_link)
            temp_soup_2 = BeautifulSoup(temp_source_2.content, 'lxml')
            table = (temp_soup_2.find('table'))
            temp_df = pd.read_html(str(table), header=1)[0]
            temp_df = temp_df.dropna()
            temp_df = temp_df.loc[temp_df['Comp'] == "Premier League"]
            name = name.replace("\n", "")
            temp_df['Name'] = name
            
            if(is_keeper):
                temp_df = temp_df[keeper_cols]
                if(keeper_df.empty):
                    keeper_df = temp_df
                else:
                    keeper_df = pd.concat([keeper_df, temp_df], axis=0, ignore_index=True)
            else:
                temp_df = temp_df[player_cols]
                if(player_df.empty):
                    player_df = temp_df
                else:
                    player_df = pd.concat([player_df, temp_df], axis=0, ignore_index=True)

        player_df['Round'] = player_df['Round'].str.replace("Matchweek ", "")
        keeper_df['Round'] = keeper_df['Round'].str.replace("Matchweek ", "")
        player_df.to_csv("Outfield Players " + year + ".csv")
        keeper_df.to_csv("Goalkeepers " + year + ".csv")
