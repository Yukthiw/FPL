# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 19:18:22 2020
Updated on Sunday Dec 26, 2021

@author: Yukthi Wickramarachchi
"""
from tokenize import Comment

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

from Scrapers.scraper import Scraper


class FPLFbrefScraper(Scraper):
    def scrape(self):
        links = []
        prefix = 'https://fbref.com/'

        source = requests.get(self.url)
        soup = BeautifulSoup(source.content, 'lxml')
        year_text = soup.find('div', {'id': 'info'}).find('h1', {'itemprop': 'name'}).text.strip()
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
        # link_1 = links[0]
        # if link_1[1] != 'GK':
        #     stat_type = 'summary'
        # else:
        #     stat_type = 'keeper'
        # temp_source = requests.get(link_1[0])
        # temp_soup = BeautifulSoup(temp_source.content, 'lxml')
        # name = temp_soup.find('h1', {'itemprop': 'name'}).text
        # for li in (temp_soup.find_all('li', {'class': 'full hasmore'})):
        #     if li.span.text == 'Match Logs':
        #         for a in li.find_all('a'):
        #             if a.text == year:
        #                 link_2 = prefix + a['href']
        #                 link_2 = link_2.replace('misc', stat_type)
        # temp_source_2 = requests.get(link_2)
        # temp_soup_2 = BeautifulSoup(temp_source_2.content, 'lxml')
        # table = (temp_soup_2.find('table'))
        # df = pd.read_html(str(table), header=1)[0]
        # df['name'] = name
        # links.pop(0)

        for link in links:
            temp_source = requests.get(link[0])
            temp_soup = BeautifulSoup(temp_source.content, 'lxml')
            name = temp_soup.find('h1', {'itemprop': 'name'}).text
            if link[1] != 'GK':
                stat_type = 'summary'
            else:
                stat_type = 'keeper'
            for li in (temp_soup.find_all('li', {'class': 'full hasmore'})):
                if li.span.text == 'Match Logs':
                    for a in li.find_all('a'):
                        if a.text == year:
                            temp_link = prefix + a['href']
                            temp_link = temp_link.replace('misc', stat_type)
            temp_source_2 = requests.get(temp_link)
            temp_soup_2 = BeautifulSoup(temp_source_2.content, 'lxml')
            table = (temp_soup_2.find('table'))
            temp_df = pd.read_html(str(table), header=1)[0]
            temp_df['name'] = name
            df = df.append(temp_df, ignore_index=True)

        cleaned_df = df[df['Comp'] == 'Premier League']
        cleaned_df['name'] = cleaned_df['name'].str.replace('\n', "")

        cleaned_df.to_csv(self.target + year + ".csv")
