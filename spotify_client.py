"""
spotify_client.py

Handles all Spotify-related functionality using Spotipy.
Includes user authentication, song search, playlist creation, and track addition.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Required scope to modify private playlists
SCOPE = "playlist-modify-private"


class SpotifyClient:
    def __init__(self):
        """
        Authenticate the user and initialize Spotipy client.
        Caches token locally to avoid repeated login prompts.
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=SCOPE,
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            show_dialog=True,
            cache_path=".cache/token.txt"  # Clearer than root-level file
        ))
        self.user_id = self.sp.current_user()["id"]

    def search_song_uris(self, song_list, year):
        """
        Search each (title, artist) pair in the provided list on Spotify.

        Args:
            song_list (List[Tuple[str, str]]): Songs as (title, artist)
            year (str): Year to narrow search scope

        Returns:
            Tuple[List[str], List[str]]: Found Spotify track URIs and not-found song strings
        """
        uris = []
        not_found = []

        for title, artist in song_list:
            query = f"track:{title} artist:{artist} year:{year}"
            try:
                result = self.sp.search(q=query, type="track", limit=1)
                uri = result["tracks"]["items"][0]["uri"]
                uris.append(uri)
            except (IndexError, KeyError):
                print(f"⚠️ '{title}' by {artist} not found on Spotify. Skipped.")
                not_found.append(f"{title} - {artist}")

        return uris, not_found

    def create_playlist(self, name, description=""):
        """
        Create a private Spotify playlist with the given name and description.

        Args:
            name (str): Playlist title
            description (str): Playlist description

        Returns:
            dict: Playlist metadata returned by Spotify API
        """
        return self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=False,
            description=description
        )

    def add_songs_to_playlist(self, playlist_id, track_uris):
        """
        Add a list of Spotify track URIs to the specified playlist.

        Args:
            playlist_id (str): Spotify playlist ID
            track_uris (List[str]): List of Spotify track URIs
        """
        self.sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
