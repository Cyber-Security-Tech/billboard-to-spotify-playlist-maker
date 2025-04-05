# main.py

from scraper import get_hot_100_songs
from spotify_client import SpotifyClient
from datetime import datetime, timedelta

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_previous_saturday(date_str):
    """Return the most recent Saturday on or before the given date."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() != 5:  # 5 = Saturday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

def find_nearest_valid_chart_date(date_str):
    """Go backward up to 14 days to find a chart with at least 80 songs."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
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
    while True:
        input_date = input("📅 Enter a Billboard chart date (YYYY-MM-DD): ")

        if not is_valid_date_format(input_date):
            print("❌ Invalid format! Please use YYYY-MM-DD.\n")
            continue

        corrected_to_saturday = get_previous_saturday(input_date)

        if corrected_to_saturday != input_date:
            print(f"⚠️ Billboard only publishes charts for Saturdays.")
            print(f"✅ Using previous Saturday instead: {corrected_to_saturday}")

        print(f"\n🔍 Scraping Billboard Hot 100 for {corrected_to_saturday}...")
        songs = get_hot_100_songs(corrected_to_saturday)

        if len(songs) < 80:
            print(f"⚠️ Only found {len(songs)} songs on {corrected_to_saturday}. Searching for nearest valid chart...")
            fallback_date, fallback_songs = find_nearest_valid_chart_date(corrected_to_saturday)

            if not fallback_songs:
                print("❌ Could not find a valid chart within 2 weeks. Try another date.")
                continue

            if fallback_date != corrected_to_saturday:
                print(f"✅ Using chart from {fallback_date} instead.")
                corrected_to_saturday = fallback_date
                songs = fallback_songs
            else:
                print("⚠️ Closest valid chart is the one you entered — continuing anyway.")

        break

    year = corrected_to_saturday.split("-")[0]

    print("\n🔐 Logging into Spotify...")
    spotify = SpotifyClient()

    print(f"\n🎵 Searching for Spotify tracks from {year}...")
    uris, missing_songs = spotify.search_song_uris(songs, year)
    print(f"✅ Found {len(uris)} out of {len(songs)} songs on Spotify.")

    if missing_songs:
        with open("not_found_songs.txt", "w", encoding="utf-8") as file:
            for song in missing_songs:
                file.write(f"{song}\n")
        print(f"📝 Saved {len(missing_songs)} unfound songs to 'not_found_songs.txt'")

    if not uris:
        print("\n❌ No matching songs found on Spotify. Playlist will not be created.")
        return

    playlist_name = f"{corrected_to_saturday} Billboard 100"
    print(f"\n📁 Creating playlist: '{playlist_name}'...")
    playlist = spotify.create_playlist(
        name=playlist_name,
        description=f"Billboard Hot 100 on {corrected_to_saturday} (requested: {input_date})"
    )

    print("➕ Adding songs to playlist...")
    spotify.add_songs_to_playlist(playlist_id=playlist["id"], track_uris=uris)

    print(f"\n🎉 Done! Your playlist '{playlist_name}' has been created on Spotify.")
    print(f"🎧 Playlist link: {playlist['external_urls']['spotify']}")

if __name__ == "__main__":
    main()
