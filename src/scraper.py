

from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def make_safe_filename(platform, source_name):

    name = f"{platform}_{source_name}".lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    return f"{name}.txt"


def fetch_url_text(url, timeout=20):

    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # fix whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def scrape_source_to_raw_file(source, raw_data_dir):

    platform = source["platform"]
    source_name = source["source_name"]
    url = source["url"]

    filename = make_safe_filename(platform, source_name)
    raw_file_path = Path(raw_data_dir) / filename

    print(f"Scraping: {source_name}")
    print(f"URL: {url}")

    text = fetch_url_text(url)

    raw_file_path.parent.mkdir(parents=True, exist_ok=True)
    raw_file_path.write_text(text, encoding="utf-8")

    return raw_file_path, text