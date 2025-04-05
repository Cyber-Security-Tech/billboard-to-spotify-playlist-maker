# scraper.py
import requests
from bs4 import BeautifulSoup

def get_hot_100_songs(date):
    """Scrape Billboard Hot 100 songs with (title, artist) tuples."""
    url = f"https://www.billboard.com/charts/hot-100/{date}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch chart. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    songs = []

    # Try new Billboard layout
    entries = soup.select("li.o-chart-results-list__item")
    for entry in entries:
        title_tag = entry.select_one("h3")
        artist_tag = entry.select_one("span.c-label")
        if title_tag and artist_tag:
            title = title_tag.get_text(strip=True)
            artist = artist_tag.get_text(strip=True)

            # Filter out junk
            if len(title) > 1 and len(artist) > 1 and not title.isdigit():
                songs.append((title, artist))

    # Try fallback layout (older pages)
    if len(songs) < 50:
        titles = soup.select("span.chart-element__information__song")
        artists = soup.select("span.chart-element__information__artist")
        for t, a in zip(titles, artists):
            title = t.get_text(strip=True)
            artist = a.get_text(strip=True)
            if len(title) > 1 and len(artist) > 1:
                songs.append((title, artist))

    return list(dict.fromkeys(songs))  # Remove duplicates
