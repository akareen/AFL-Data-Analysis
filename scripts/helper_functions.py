import requests
from bs4 import BeautifulSoup

# Used to create a BeautifulSoup object from a URL
def get_soup(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    return BeautifulSoup(response.text, 'html.parser')