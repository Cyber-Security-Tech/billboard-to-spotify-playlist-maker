"""
main.py

Entry point for the Billboard to Spotify Playlist Maker.

This script prompts the user for a Billboard chart date, scrapes the Hot 100 songs 
from that date (or nearest valid chart), matches them on Spotify using the Spotify API, 
and creates a playlist in the user's account.

Modules:
- scraper.py: handles Billboard chart scraping
- spotify_client.py: handles Spotify API authentication and playlist operations
"""

from datetime import datetime, timedelta
from scraper import get_hot_100_songs
from spotify_client import SpotifyClient


def is_valid_date_format(date_str):
    """
    Check if the input string is in the correct YYYY-MM-DD format.
    Returns True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_previous_saturday(date_str):
    """
    Given any date, return the previous (or same) Saturday in YYYY-MM-DD format.
    Billboard charts are published on Saturdays only.
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() != 5:  # 5 = Saturday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")


def find_nearest_valid_chart_date(start_date_str):
    """
    Try up to 14 days backwards from the provided date to find a Billboard chart 
    with at least 80 songs. Returns the valid chart date and the song list.
    """
    date = datetime.strptime(start_date_str, "%Y-%m-%d")
    attempts = 0

    while attempts < 14:
        formatted_date = date.strftime("%Y-%m-%d")
        print(f"🔎 Trying {formatted_date}...")
        songs = get_hot_100_songs(formatted_date)

        if len(songs) >= 80:
            return formatted_date, songs

        date -= timedelta(days=1)
        attempts += 1

    return None, []


def main():
    # Get and validate date input
    while True:
        input_date = input("📅 Enter a Billboard chart date (YYYY-MM-DD): ")

        if not is_valid_date_format(input_date):
            print("❌ Invalid format! Please use YYYY-MM-DD.\n")
            continue

        corrected_date = get_previous_saturday(input_date)

        if corrected_date != input_date:
            print("⚠️ Billboard only publishes charts for Saturdays.")
            print(f"✅ Using previous Saturday instead: {corrected_date}")

        print(f"\n🔍 Scraping Billboard Hot 100 for {corrected_date}...")
        songs = get_hot_100_songs(corrected_date)

        # Fallback if the chart is incomplete
        if len(songs) < 80:
            print(f"⚠️ Only found {len(songs)} songs. Searching for nearest valid chart...")
            fallback_date, fallback_songs = find_nearest_valid_chart_date(corrected_date)

            if not fallback_songs:
                print("❌ No valid chart found within the last 2 weeks. Try another date.")
                continue

            if fallback_date != corrected_date:
                print(f"✅ Using chart from {fallback_date} instead.")
                corrected_date = fallback_date
                songs = fallback_songs
            else:
                print("⚠️ Closest valid chart is the one you entered — continuing anyway.")

        break

    year = corrected_date.split("-")[0]

    print("\n🔐 Logging into Spotify...")
    spotify = SpotifyClient()

    print(f"\n🎵 Searching for Spotify tracks from {year}...")
    uris, missing_songs = spotify.search_song_uris(songs, year)
    print(f"✅ Found {len(uris)} out of {len(songs)} songs on Spotify.")

    # Save missing songs to file for manual review
    if missing_songs:
        with open("not_found_songs.txt", "w", encoding="utf-8") as file:
            for song in missing_songs:
                file.write(f"{song}\n")
        print(f"📝 Saved {len(missing_songs)} unfound songs to 'not_found_songs.txt'")

    if not uris:
        print("\n❌ No matching songs found on Spotify. Playlist will not be created.")
        return

    playlist_name = f"{corrected_date} Billboard 100"
    print(f"\n📁 Creating playlist: '{playlist_name}'...")
    playlist = spotify.create_playlist(
        name=playlist_name,
        description=f"Billboard Hot 100 on {corrected_date} (requested: {input_date})"
    )

    print("➕ Adding songs to playlist...")
    spotify.add_songs_to_playlist(playlist_id=playlist["id"], track_uris=uris)

    print(f"\n🎉 Done! Your playlist '{playlist_name}' has been created on Spotify.")
    print(f"🎧 Playlist link: {playlist['external_urls']['spotify']}")


if __name__ == "__main__":
    main()
