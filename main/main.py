import data_mining.data_mining as sdm
import pandas as pd

ID = ''
PWD = ''

data_generator = sdm.SpotifyDataMining(ID, PWD)

name = 'playlists'
data = data_generator.get_tracks_from_playlists(['spotify:playlist:37i9dQZEVXbMDoHDwVN2tF'])

#name = 'playlists_and_artists'
#data = data_generator.get_tracks_and_artists_from_playlists(['spotify:playlist:37i9dQZEVXbMDoHDwVN2tF'])

#name = 'artists'
#data = data_generator.get_tracks_from_artists(['spotify:artist:3WrFJ7ztbogyGnTHbHJFl2'])

#name = 'genre_playlists'
#data = data_generator.get_playlists_from_genres(['hiphop', 'pop'])

#name = 'genre_playlists_and_artists'
#data = data_generator.get_playlists_and_artists_from_genres(['hiphop', 'pop'])

df = pd.DataFrame.from_dict(data_generator.end_dic)
df = df.drop_duplicates()

df = df.dropna(axis=0, how='all')

df.to_csv(f'~/Desktop/spotify_data_{name}.csv', header=True, index=False)
