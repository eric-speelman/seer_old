from collector import collect
import datetime
import pandas as pd
import csv

months = ['september', 'october', 'november', 'december', 'january', 'feburary', 'march', 'april', 'may']
data_path = '../data/'
player_data = []
start_year = 2018
end_year = 2020

def collect_game(href):
    print(f'Collecting https://www.basketball-reference.com{href}')
    html = collect('https://www.basketball-reference.com' + href)
    if html is None:
        return []
    game_data = {}
    team_data = []
    player_data = []
    game_data['id'] = href.split('/')[2].split('.')[0]
    game_scoreboard = html.select('div.scorebox > div')[2]
    game_data['date'] = game_scoreboard.contents[1].contents[0]
    if len(game_scoreboard.contents[2].contents) >= 1:
        game_data['venue'] = game_scoreboard.contents[2].contents[0].split(',')[0]
    else:
        game_data['venue'] = ''
    for team_html in html.select('div.scorebox > div')[:2]:
        data = {}
        team_data.append(data)
        team_link = team_html.select('strong a')[0]
        data['id'] = team_link['href'].split('/')[2]
        data['name'] = team_link.contents[0]
        data['points'] = int(team_html.select('div.score')[0].contents[0])
        score_parts = list(map(lambda x: int(x), team_html.contents[4].contents[0].split('-')))
        data['season_wins'] = score_parts[0]
        data['season_losses'] = score_parts[1]
    if team_data[0]['points'] > team_data[1]['points']:
        team_data[0]['season_wins'] -= 1
        team_data[1]['season_losses'] -= 1
    else:
        team_data[1]['season_wins'] -= 1
        team_data[0]['season_losses'] -= 1
    for team in team_data:
        starting = 1
        for stat_row in html.select(f'#box-' + team['id'] + '-game-basic tbody tr'):
            data = {}
            if stat_row.has_attr('class'):
                starting = 0
            elif len(stat_row.select('td')) > 1:
                player_data.append(data)
                player_link = stat_row.select('th a')[0]
                data['id'] = player_link['href'].split('/')[3].split('.')[0]
                data['name'] = player_link.contents[0]
                data['starting'] = starting
                for stat_cell in stat_row.select('td'):
                    stat = stat_cell['data-stat']
                    if not stat.endswith('pct') and stat != 'plus_minus':
                        data[stat_cell['data-stat']] = stat_cell.contents[0]
                for curr_team in team_data:
                    prefix = 'team_'
                    if curr_team['id'] != team['id']:
                        prefix = 'opp_team_'
                    for key in curr_team:
                        data[prefix + key] = str(curr_team[key])
                for key in game_data:
                    data[f'game_{key}'] = str(game_data[key])
    return player_data
                
            
year = start_year
while year < end_year:
    for month in months:
        html = collect(f'https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html')
        if html is not None:
            for row in html.select('#schedule tr'):
                th = row.select('th')[0]
                if th.has_attr('csk'):
                    links = row.select('a')
                    if len(links) >= 4:
                        href = row.select('a')[3]['href']
                        player_data.extend(collect_game(href))

    keys = player_data[0].keys()
    with open(f'../data/nba_{year}.csv', 'w', encoding='utf-8', newline='') as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(player_data)
    year += 1
    player_data = []

