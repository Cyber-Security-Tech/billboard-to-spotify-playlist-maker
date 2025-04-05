# scraper.py
import requests
from bs4 import BeautifulSoup

def get_hot_100_songs(date):
    """Scrape Billboard Hot 100 song titles and artists for a given date."""
    url = f"https://www.billboard.com/charts/hot-100/{date}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch chart. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Try modern layout
    titles = soup.select("li.o-chart-results-list__item h3")
    artists = soup.select("li.o-chart-results-list__item span.c-label")

    songs = []
    for i in range(min(len(titles), len(artists))):
        title = titles[i].getText().strip()
        artist = artists[i].getText().strip()
        if title and artist and "RESTRICTED" not in artist:
            songs.append(f"{title} {artist}")

    # Fallback for old layout
    if not songs:
        song_titles = soup.select("span.chart-element__information__song")
        song_artists = soup.select("span.chart-element__information__artist")
        for title, artist in zip(song_titles, song_artists):
            songs.append(f"{title.getText().strip()} {artist.getText().strip()}")

    return list(dict.fromkeys(songs))
