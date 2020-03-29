import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import feature_lists.feature_lists as fl


class SpotifyDataMining:

    def __init__(self, user_id, user_secret):
        self.user_id = user_id
        self.user_secret = user_secret
        self.playlists = []

        self.client_credentials_manager = SpotifyClientCredentials(client_id=self.user_id,
                                                                   client_secret=self.user_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

        self.track_fields = fl.track_fields
        self.track_names = fl.track_names
        self.feature_fields = fl.feature_fields
        self.feature_names = fl.feature_names
        self.analysis_meta_fields = fl.analysis_meta_fields
        self.analysis_meta_names = fl.analysis_meta_names
        self.analysis_track_fields = fl.analysis_track_fields
        self.analysis_track_names = fl.analysis_track_names

        self.end_dic = {}
        self.create_final_dic()

        self.album_names = []
        self.album_uris = []
        self.album_genres = []
        self.artist_uris = []
        self.artist_genres = []

    def create_final_dic(self):
        for name in self.track_names:
            self.end_dic[name] = []
        self.end_dic['artist_name'] = []
        self.end_dic['album_name'] = []
        self.end_dic['popularity'] = []
        self.end_dic['genre'] = []
        for name in self.feature_names:
            self.end_dic[name] = []
        for name in self.analysis_meta_names:
            self.end_dic[name] = []
        for name in self.analysis_track_names:
            self.end_dic[name] = []

    def get_tracks_from_playlists(self, playlists, genres=None):
        self.playlists = playlists
        self.process_playlist_tracks(genres)
        return self.end_dic

    def get_tracks_and_artists_from_playlists(self, playlists, genres=None):
        self.playlists = playlists
        self.process_playlist_tracks(genres)
        self.process_artists(self.artist_uris, self.artist_genres)
        self.process_albums(self.album_genres)
        return self.end_dic

    def get_tracks_from_artists(self, artist_uris, genres=None):
        self.artist_uris = artist_uris
        self.process_artists(self.artist_uris, genres)
        return self.end_dic

    def get_playlists_from_genres(self, genres):
        playlists = []
        genres_list = []
        for genre in genres:
            linsting = self.sp.category_playlists(category_id=genre, limit=1)
            for instance in linsting['playlists']['items']:
                playlists.append(instance['uri'])
                genres_list.append(genre)
        self.get_tracks_from_playlists(playlists, genres_list)
        return self.end_dic

    def get_playlists_and_artists_from_genres(self, genres):
        playlists = []
        genres_list = []
        for genre in genres:
            playlists_list = self.sp.category_playlists(category_id=genre, limit=1)
            for instance in playlists_list['playlists']['items']:
                playlists.append(instance['uri'])
                genres_list.append(genre)
        self.get_tracks_and_artists_from_playlists(playlists, genres_list)
        return self.end_dic

    def process_playlist_tracks(self, genres):
        if genres is None:
            genres = []
            for i in range(0, len(self.playlists)):
                genres.append(None)
        for playlist, genre in zip(self.playlists, genres):
            tracks = self.sp.playlist_tracks(playlist)
            for track in tracks['items']:
                try:
                    self.end_dic['album_name'].append(track['track']['album']['name'])
                    self.end_dic['popularity'].append(track['track']['popularity'])
                    self.end_dic['genre'].append(genre)
                    self.album_names.append(track['track']['album']['name'])
                    self.album_uris.append(track['track']['album']['uri'])
                    self.album_genres.append(genre)
                    artist_names = ''
                    for artist in track['track']['artists']:
                        self.artist_uris.append(artist['uri'])
                        self.artist_genres.append(genre)
                        if artist_names == '':
                            artist_names = artist_names + artist['name']
                        else:
                            artist_names = artist_names + ', ' + artist['name']
                    self.end_dic['artist_name'].append(artist_names)
                    for track_name, track_field in zip(self.track_names, self.track_fields):
                        self.end_dic[track_name].append(track['track'][track_field])
                except Exception:
                    self.end_dic['album_name'].append(None)
                    self.end_dic['popularity'].append(None)
                    self.end_dic['genre'].append(None)
                    self.end_dic['artist_name'].append(None)
                    for track_name, track_field in zip(self.track_names, self.track_fields):
                        self.end_dic[track_name].append(None)
                try:
                    features = self.sp.audio_features(track['track']['uri'])
                    for feature in features:
                        for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                            self.end_dic[feature_name].append(feature[feature_field])
                except Exception:
                    for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                        self.end_dic[feature_name].append(None)
                try:
                    audio_ana = self.sp.audio_analysis(track['track']['uri'])
                    for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                        self.end_dic[ana_meta_name].append(audio_ana['meta'][ana_meta_field])
                    for ana_track_name, ana_track_field in zip(self.analysis_track_names, self.analysis_track_fields):
                        self.end_dic[ana_track_name].append(audio_ana['track'][ana_track_field])
                except Exception:
                    for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                        self.end_dic[ana_meta_name].append(None)
                    for ana_track_name, ana_track_field in zip(self.analysis_track_names, self.analysis_track_fields):
                        self.end_dic[ana_track_name].append(None)

    def process_artists(self, artist_uris, genres):
        if genres is None:
            genres = []
            for i in range(0, len(self.artist_uris)):
                genres.append(None)
        j = 0
        for artist_uri, genre in zip(artist_uris, genres):
            album_names_temp = []
            album_uris_temp = []
            for i in range(len(self.sp.artist_albums(artist_uri, album_type='album')['items'])):
                album_names_temp.append(self.sp.artist_albums(artist_uri, album_type='album')['items'][i]['name'])
                album_uris_temp.append(self.sp.artist_albums(artist_uri, album_type='album')['items'][i]['uri'])
            j = j+1
            for album, album_name in zip(album_uris_temp, album_names_temp):
                tracks = self.sp.album_tracks(album)
                for track in tracks['items']:
                    try:
                        track_detail = self.sp.track(track['uri'])
                        self.end_dic['album_name'].append(album_name)
                        self.end_dic['popularity'].append(track_detail['popularity'])
                        self.end_dic['genre'].append(genre)
                        artist_names = ''
                        for artist in track['artists']:
                            if artist_names == '':
                                artist_names = artist_names + artist['name']
                            else:
                                artist_names = artist_names + ', ' + artist['name']
                        self.end_dic['artist_name'].append(artist_names)
                        for track_name, track_field in zip(self.track_names, self.track_fields):
                            self.end_dic[track_name].append(track[track_field])
                    except Exception:
                        self.end_dic['album_name'].append(None)
                        self.end_dic['popularity'].append(None)
                        self.end_dic['genre'].append(None)
                        self.end_dic['artist_name'].append(None)
                        for track_name, track_field in zip(self.track_names, self.track_fields):
                            self.end_dic[track_name].append(None)
                    try:
                        features = self.sp.audio_features(track['uri'])
                        for feature in features:
                            for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                                self.end_dic[feature_name].append(feature[feature_field])
                    except Exception:
                        for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                            self.end_dic[feature_name].append(None)
                    try:
                        audio_ana = self.sp.audio_analysis(track['uri'])
                        for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                            self.end_dic[ana_meta_name].append(audio_ana['meta'][ana_meta_field])
                        for ana_track_name, ana_track_field in zip(self.analysis_track_names, self.analysis_track_fields):
                            self.end_dic[ana_track_name].append(audio_ana['track'][ana_track_field])
                    except Exception:
                        for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                            self.end_dic[ana_meta_name].append(None)
                        for ana_track_name, ana_track_field in zip(self.analysis_track_names,
                                                                   self.analysis_track_fields):
                            self.end_dic[ana_track_name].append(None)

    def process_albums(self, genres):
        if genres is None:
            genres = []
            for i in range(0, len(self.artist_uris)):
                genres.append(None)
        for album, album_name, genre in zip(self.album_uris, self.album_names, genres):
            tracks = self.sp.album_tracks(album)
            for track in tracks['items']:
                try:
                    track_detail = self.sp.track(track['uri'])
                    self.end_dic['album_name'].append(album_name)
                    self.end_dic['popularity'].append(track_detail['popularity'])
                    self.end_dic['genre'].append(genre)
                    artist_names = ''
                    for artist in track['artists']:
                        if artist_names == '':
                            artist_names = artist_names + artist['name']
                        else:
                            artist_names = artist_names + ', ' + artist['name']
                    self.end_dic['artist_name'].append(artist_names)
                    for track_name, track_field in zip(self.track_names, self.track_fields):
                        self.end_dic[track_name].append(track[track_field])
                except Exception:
                    self.end_dic['album_name'].append(None)
                    self.end_dic['popularity'].append(None)
                    self.end_dic['genre'].append(None)
                    self.end_dic['artist_name'].append(None)
                    for track_name, track_field in zip(self.track_names, self.track_fields):
                        self.end_dic[track_name].append(None)
                try:
                    features = self.sp.audio_features(track['uri'])
                    for feature in features:
                        for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                            self.end_dic[feature_name].append(feature[feature_field])
                except Exception:
                    for feature_name, feature_field in zip(self.feature_names, self.feature_fields):
                        self.end_dic[feature_name].append(None)
                try:
                    audio_ana = self.sp.audio_analysis(track['uri'])
                    for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                        self.end_dic[ana_meta_name].append(audio_ana['meta'][ana_meta_field])
                    for ana_track_name, ana_track_field in zip(self.analysis_track_names, self.analysis_track_fields):
                        self.end_dic[ana_track_name].append(audio_ana['track'][ana_track_field])
                except Exception:
                    for ana_meta_name, ana_meta_field in zip(self.analysis_meta_names, self.analysis_meta_fields):
                        self.end_dic[ana_meta_name].append(None)
                    for ana_track_name, ana_track_field in zip(self.analysis_track_names, self.analysis_track_fields):
                        self.end_dic[ana_track_name].append(None)
