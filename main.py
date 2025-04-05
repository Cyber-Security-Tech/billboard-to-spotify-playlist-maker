# main.py

from scraper import get_hot_100_songs
from spotify_client import SpotifyClient
from datetime import datetime

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def main():
    # Get user input with validation
    while True:
        date = input("📅 Enter a Billboard chart date (YYYY-MM-DD): ")
        if not is_valid_date_format(date):
            print("❌ Invalid format! Please use YYYY-MM-DD.\n")
            continue

        print(f"\n🔍 Scraping Billboard Hot 100 for {date}...")
        songs = get_hot_100_songs(date)
        
        if not songs:
            print(f"❌ No songs found. Billboard may not have a chart for {date}. Try a Saturday or Sunday.\n")
            continue

        break

    year = date.split("-")[0]

    print("\n🔐 Logging into Spotify...")
    spotify = SpotifyClient()

    print(f"\n🎵 Searching for Spotify tracks from {year}...")
    uris, missing_songs = spotify.search_song_uris(songs, year)
    print(f"✅ Found {len(uris)} out of {len(songs)} songs on Spotify.")

    # Save missing songs to a file
    if missing_songs:
        with open("not_found_songs.txt", "w", encoding="utf-8") as file:
            for song in missing_songs:
                file.write(f"{song}\n")
        print(f"📝 Saved {len(missing_songs)} unfound songs to 'not_found_songs.txt'")

    if not uris:
        print("\n❌ No matching songs found on Spotify. Playlist will not be created.")
        return

    playlist_name = f"{date} Billboard 100"
    print(f"\n📁 Creating playlist: '{playlist_name}'...")
    playlist = spotify.create_playlist(playlist_name, description="Top 100 songs from Billboard on this date")

    print("➕ Adding songs to playlist...")
    spotify.add_songs_to_playlist(playlist_id=playlist["id"], track_uris=uris)

    print(f"\n🎉 Done! Your playlist '{playlist_name}' has been created on Spotify.")
    print(f"🎧 Playlist link: {playlist['external_urls']['spotify']}")

if __name__ == "__main__":
    main()
