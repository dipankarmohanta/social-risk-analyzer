import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_instagram_profile(username):
    url = f"https://www.instagram.com/{username}/"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception:
        return {"status": "error"}

    if r.status_code != 200:
        return {"status": "blocked"}

    if "This Account is Private" in r.text:
        return {"status": "private"}

    soup = BeautifulSoup(r.text, "html.parser")

    # OpenGraph tags
    name = None
    image = None

    og_title = soup.find("meta", property="og:title")
    og_image = soup.find("meta", property="og:image")

    if og_title:
        name = og_title.get("content")

    if og_image:
        image = og_image.get("content")

    return {
        "status": "public",
        "display_name": name,
        "profile_pic": image,
        "html": soup.get_text()
    }
