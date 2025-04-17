"""
scraper.py

Handles scraping Billboard Hot 100 song titles and artists for a given date.
Supports both modern and legacy Billboard chart layouts.
"""

import requests
from bs4 import BeautifulSoup


def get_hot_100_songs(date):
    """
    Scrape the Billboard Hot 100 chart for a given date.

    Tries both modern and legacy Billboard layouts.
    Returns a list of (title, artist) tuples for songs found on the chart.
    
    Args:
        date (str): Date string in 'YYYY-MM-DD' format
    
    Returns:
        List[Tuple[str, str]]: A list of song title and artist pairs
    """
    url = f"https://www.billboard.com/charts/hot-100/{date}/"
    headers = {
        "User-Agent": "Mozilla/5.0"  # Spoof UA to avoid bot protection
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch chart for {date}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    songs = []

    # --- Attempt #1: Newer Billboard layout ---
    entries = soup.select("li.o-chart-results-list__item")

    for entry in entries:
        title_tag = entry.select_one("h3")
        artist_tag = entry.select_one("span.c-label")

        if title_tag and artist_tag:
            title = title_tag.get_text(strip=True)
            artist = artist_tag.get_text(strip=True)

            # Filter out junk (empty or numeric-only entries)
            if len(title) > 1 and len(artist) > 1 and not title.isdigit():
                songs.append((title, artist))

    # --- Attempt #2: Legacy layout fallback (for older dates) ---
    if len(songs) < 50:
        titles = soup.select("span.chart-element__information__song")
        artists = soup.select("span.chart-element__information__artist")

        for t, a in zip(titles, artists):
            title = t.get_text(strip=True)
            artist = a.get_text(strip=True)

            if len(title) > 1 and len(artist) > 1:
                songs.append((title, artist))

    # Remove duplicates while preserving order
    return list(dict.fromkeys(songs))
