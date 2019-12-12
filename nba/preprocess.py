import pandas as pd
import numpy as np
from datetime import datetime
import math
import os.path
import time
from os import path
from sklearn import feature_extraction

window_size = 10
child_sets_config = [
    {
        'name': 'full',
        'cols': [{
            'offset': False,
            'calc': False,
            'col': 'team_is_home'
        },
        {
            'offset': False,
            'calc': False,
            'col': 'game_season'
        },
        {
            'offset': False,
            'calc': False,
            'col': 'game_day'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'team_points'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'team_season_wins'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'team_season_losses'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'opp_team_points'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'opp_team_season_wins'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'opp_team_season_losses'
        }],
        'prior_cols': [
        {
            'offset': True,
            'calc': False,
            'col': 'dkp'
        },
        {
            'offset': True,
            'calc': False,
            'col': 'mp'
        }]
    }
]
child_sets_gen = ['full']
child_sets = []
for cs in child_sets_config:
    if cs['name'] in child_sets_gen:
        child_sets.append(cs)
data = []
start = datetime.now()
stats = ['dkp', 'game_venue', 'team_id', 'opp_team_id', 'game_season', 'game_day', 'mp', 'team_points', 'team_season_wins', 'team_season_losses','team_is_home', 'opp_team_points', 'opp_team_season_wins', 'opp_team_season_losses']
avgs = []
for child_set in child_sets:
    for col in child_set['cols']:
        if not col['calc']:
            stats.append(col['col'])
    for col in child_set['prior_cols']:
        if not col['calc']:
            stats.append(col['col'])
stats = set(stats)
print(stats)

def scale(X, x_min, x_max):
    nom = (X-X.min(axis=0))*(x_max-x_min)
    denom = X.max(axis=0) - X.min(axis=0)
    denom[denom==0] = 1
    return x_min + nom/denom
hasher = feature_extraction.FeatureHasher(n_features=10, input_type='string')
def hash_encoder(item):
    return hasher.transform(item)
def binary_encode(arr, item, length):
    index = arr.index(item)
    binary = [int(x) for x in list('{0:0b}'.format(index))]
    while len(binary) < length:
        binary.append(0)
    return binary
def one_hot(arr, item):
    encoded = [0] * len(arr)
    encoded[arr.index(item)] = 1
    return encoded
data_dir = 'c:/github/seer/data/'
start = time.time()
timer_steps = {}
step_time = 0
data_dic = {}
def add_data(col, val):
    if col not in data_dic:
        data_dic[col] = []
    data_dic[col].append(val)
if not path.exists(f'{data_dir}/nba_win_{window_size}.csv'):
    print('Window data not found. Generating...')
    df = pd.read_csv(f'{data_dir}/nba.csv', index_col=['id'])
    game_df = pd.read_csv(f'{data_dir}/nba.csv', index_col=['game_id'])
    cols = []
    for prior_index in range(window_size):
        cols.append(f'has_value_p{prior_index}')
        for stat in stats:
            cols.append(f'{stat}_p{prior_index}')
    cnt = 0
    for id, df_row in df.iterrows():
        game_id = df_row['game_id']
        cnt += 1
        if cnt % 1000 == 1:
            end = time.time()
            print(f'Window {cnt}/{df.shape[0]} {end-start} {str(step_time)}')
            start = time.time()
            step_time = 0
        priors = df.loc[[id]]
        p_start = time.time()
        priors = priors[priors['game_id'] <= game_id ].sort_values('game_id', ascending=False)
        row = {}
        all_players = game_df.loc[[df_row['game_id']]]
        add_data('starters', ','.join(list(all_players[(all_players['team_id'] == df_row['team_id']) & (all_players['starting'] == 1)]['id'])))
        add_data('bench', ','.join(list(all_players[(all_players['team_id'] == df_row['team_id']) & (all_players['starting'] == 0)]['id'])))
        add_data('opp_starters', ','.join(list(all_players[(all_players['team_id'] != df_row['team_id']) & (all_players['starting'] == 1)]['id'])))
        add_data('opp_bench', ','.join(list(all_players[(all_players['team_id'] != df_row['team_id']) & (all_players['starting'] == 0)]['id'])))
        add_data('id', id)
        add_data('game_id', game_id)
        for prior_index in range(window_size):
            has_value = priors.shape[0] > prior_index
            add_data(f'has_value_p{prior_index}', 1 if has_value else 0)
            for prior_stat in stats:
                stat_val = 0
                if has_value:
                    stat_val = priors.iloc[prior_index][prior_stat]
                add_data(f'{prior_stat}_p{prior_index}', stat_val)
        step_time += time.time() - p_start
    prior_df = pd.DataFrame.from_dict(data_dic)
    prior_df.to_csv(f'{data_dir}/nba_win_{window_size}.csv', index=False)
else:
    prior_df = pd.read_csv(f'{data_dir}/nba_win_{window_size}.csv', index_col=False)
print(prior_df['team_is_home_p0'].shape)
players = list(set(list(prior_df['id'])))
venues = list(set(list(prior_df['game_venue_p0'])))
teams = list(set(list(prior_df['team_id_p0'])))
start = time.time()
for child_set in child_sets:
    print('Generating for ' + child_set['name'])
    matrix = []
    cnt = 0
    for i, row in prior_df.iterrows():
        cnt += 1
        if cnt % 1000 == 1:
            end = time.time()
            print(f'Window {cnt}/{prior_df.shape[0]} {end-start}')
            start = time.time()
        matrix_row = []
        player_binary = binary_encode(players, row['id'], 11)
        matrix_row.extend(player_binary)
        matrix.append(matrix_row)
        if len(child_set['prior_cols']) > 0:
            for prior_index in range(window_size - 1):
                matrix_row.append(row[f'has_value_p{prior_index+1}'])
        for prior_col in child_set['prior_cols']:
            for prior_index in range(window_size - 1):
                real_p_index = prior_index
                is_offset = prior_col['offset']
                if is_offset:
                    real_p_index += 1
                col_name = prior_col['col']
                matrix_row.append(row[f'{col_name}_p{real_p_index}'])
        for col in child_set['cols']:
            prior_index = 0
            is_offset = col['offset']
            if is_offset:
                prior_index = 1
            col_name = col['col']
            if col_name == 'game_venue':
                venue_binary = one_hot(venues, row['game_venue_p0'])
                matrix_row.extend(venue_binary)
            elif 'team_id' in col_name:
                matrix_row.extend(one_hot(teams, row[col_name + '_p0']))
            elif 'starters' in col_name:
                for player_id in row[col_name].split(','):
                    matrix_row.append(1)
                    matrix_row.extend(one_hot(players, player_id))
            elif 'bench' in col_name:
                player_ids = row[col_name].split(',')
                for player_id in player_ids:
                    matrix_row.append(1)
                    matrix_row.extend(one_hot(players, player_id))
                bench_cnt = len(player_ids)
                while bench_cnt < 8:
                    arr = [0] * len(players)
                    matrix_row.extend(arr)
                    bench_cnt += 1
            else:
                matrix_row.append(row[f'{col_name}_p{prior_index}'])
        #print('aaaaa')
        #print(matrix_row)
        #print('bbbbbb')
        #print(matrix)
        #np.matrix(matrix, dtype='float32')
    np_matrix = np.matrix(matrix, dtype='float32')
    print('saving...')
    np.save('../data/'+ child_set['name'], np_matrix)
    print(np_matrix.shape)
np.save('../data/y', np.array(prior_df['dkp_p0']))
prior_df = None
for child_set in child_sets:
    print('loading...')
    matrix = np.load('../data/'+ child_set['name'] + '.npy')
    matrix = scale(matrix, 0, 1)
    print('saving...')
    np.save('../data/'+ child_set['name'], matrix)