
import requests, time
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent":"CargoSiteBot/1.0 (+https://example.com)"}

def can_fetch(url, user_agent="*"):
    # very simple checker: fetch robots.txt for domain and look for Disallow lines
    try:
        from urllib.parse import urlparse, urljoin
        parsed = urlparse(url)
        robots = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        r = requests.get(robots, headers=HEADERS, timeout=5)
        if r.status_code != 200:
            return True
        txt = r.text.lower()
        # naive check
        if "disallow: /" in txt:
            return False
        return True
    except Exception as e:
        return True

def search_della_ati(query):
    # query example: "Алматы-Астана" or "Москва-Казань"
    results = []
    # Example 1: search on della.kz (this is a simple demonstration)
    della_url = f"https://della.kz/search/?q={query}"
    if can_fetch(della_url):
        try:
            r = requests.get(della_url, headers=HEADERS, timeout=10)
            time.sleep(2)  # polite pause
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                # Example: find links or titles (this will likely need to be adapted)
                for a in soup.find_all("a", href=True)[:10]:
                    title = a.get_text().strip()
                    link = a["href"]
                    if title:
                        results.append({"source":"della", "title":title, "link":link})
        except Exception as e:
            print("della error", e)
    # Example 2: search on ati.su (demo)
    ati_url = f"https://ati.su/search/?q={query}"
    if can_fetch(ati_url):
        try:
            r = requests.get(ati_url, headers=HEADERS, timeout=10)
            time.sleep(2)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True)[:10]:
                    title = a.get_text().strip()
                    link = a["href"]
                    if title:
                        results.append({"source":"ati", "title":title, "link":link})
        except Exception as e:
            print("ati error", e)
    return results
