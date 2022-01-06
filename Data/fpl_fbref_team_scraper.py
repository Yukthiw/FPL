from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def scrape(url):
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    links = []
    prefix = 'https://fbref.com'
    source = requests.get(url)
    soup = BeautifulSoup(source.content, 'lxml')
    table = soup.find('table', {'class': 'stats_table'})
    team_table = table.find('tbody')
    for_df = pd.DataFrame()
    against_df = pd.DataFrame()
    for row in team_table.find_all('tr'):
        link = prefix + row.find('td', {'data-stat': 'squad'}).a.attrs['href']
        team_source = requests.get(link)
        team_soup = BeautifulSoup(team_source.content, 'lxml')
        nav_pane = team_soup.find('div', {'id': 'inner_nav'})
        for li in nav_pane.find_all('li'):
            if li.text == 'Shooting':
                links.append(li.a.attrs['href'])
                break


    for link in links:
        features = ['squad', 'Round', 'Venue', 'Opponent', 'xG', 'npxG']
        team_name = re.search('\/([A-Z].+)\-Match', link).group(1)
        team_name = team_name.replace('-', " ")
        match_log_source = requests.get(prefix + link)
        match_logs_soup = BeautifulSoup(match_log_source.content, 'lxml')
        shooting_div = match_logs_soup.find('div', {'id': 'all_matchlogs'})
        stats_table = shooting_div.find_all('table', {'class': 'stats_table'})
        # Taking 'for' stats
        temp_df = pd.read_html(str(stats_table[0]), header=1)[0]
        temp_df = temp_df[temp_df['Comp'] == 'Premier League']
        temp_df['squad'] = team_name
        for_df = for_df.append(temp_df[features], ignore_index=True)
        # Taking 'against' stats
        temp_df = pd.read_html(str(stats_table[1]), header=1)[0]
        temp_df = temp_df[temp_df['Comp'] == 'Premier League']
        temp_df['squad'] = team_name
        against_df = against_df.append(temp_df[features], ignore_index=True)

    for_df.to_csv('/Data/teams_offence.csv')
    against_df.to_csv('/Data/teams_defence.csv')