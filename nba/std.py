import pandas as pd

df = pd.read_csv(f'../data/nba.csv', index_col=['id'])
cnt = 0
err = 0
avg = 0
players = {}
for id, df_row in df.iterrows():
    cnt += 1
    avg += df_row['dkp']
    if not id in players:
        players[id] = {
            'cnt': 0,
            'sum': 0
        }
    players[id]['cnt'] += 1
    players[id]['sum'] += df_row['dkp']

avg = avg / cnt

player_err = 0
for player in players:
    players[player]['avg'] = players[player]['sum'] / players[player]['cnt']
for id, df_row in df.iterrows():
    err += abs(df_row['dkp'] - avg)
    player_err += abs(df_row['dkp'] - players[id]['avg'])
err = err / cnt
player_err = player_err / cnt
print(err)
print(player_err)