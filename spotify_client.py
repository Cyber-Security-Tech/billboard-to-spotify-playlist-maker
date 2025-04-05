# spotify_client.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPE = "playlist-modify-private"

class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=SCOPE,
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            show_dialog=True,
            cache_path="token.txt"
        ))
        self.user_id = self.sp.current_user()["id"]

    def search_song_uris(self, song_list, year):
        """
        Accepts a list of (title, artist) tuples.
        Searches each song on Spotify and returns a list of URIs and not-found songs.
        """
        uris = []
        not_found = []

        for title, artist in song_list:
            query = f"track:{title} artist:{artist} year:{year}"
            result = self.sp.search(q=query, type="track", limit=1)
            try:
                uri = result["tracks"]["items"][0]["uri"]
                uris.append(uri)
            except IndexError:
                print(f"⚠️ '{title}' by {artist} not found on Spotify. Skipped.")
                not_found.append(f"{title} - {artist}")

        return uris, not_found

    def create_playlist(self, name, description=""):
        playlist = self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=False,
            description=description
        )
        return playlist

    def add_songs_to_playlist(self, playlist_id, track_uris):
        self.sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
