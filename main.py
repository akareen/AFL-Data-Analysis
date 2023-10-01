import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://afltables.com/afl/stats/2023.html"


def get_soup(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    return BeautifulSoup(response.text, 'html.parser')


def scrape_player_page(player_url, team_directory):
    soup = get_soup(player_url)
    if not soup:
        return

    tables = soup.find_all('table')
    player_name = player_url.split('/')[-1].replace('.html', '')
    csv_file_path = os.path.join(team_directory, f"{player_name}.csv")

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header_written = False  # flag to ensure header is written only once
        
        for table in tables:
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            team, year = th_colspan_28.text.strip().split(' - ')
            if not header_written:  # write header only if not already written
                header = ['Team', 'Year'] + [th.text.strip() for th in table.find_all('tr')[1].find_all('th')]
                writer.writerow(header)
                header_written = True

            for row in table.tbody.find_all('tr'):
                data = [team, year] + [td.text.strip().replace('↑', '').replace('↓', '') for td in row.find_all('td')]
                writer.writerow(data)


def main():
    soup = get_soup(base_url)
    if not soup:
        return

    for table in soup.find_all('table', class_='sortable'):
        team_link = table.find('a', href=lambda x: x and x.startswith('../teams/'))
        if not team_link:
            continue

        team_name = team_link.text.strip()
        team_directory = os.path.join('data/game_stats', team_name)
        os.makedirs(team_directory, exist_ok=True)

        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 1:
                player_link = cols[1].find('a', href=lambda x: x and x.startswith('players/'))
                if player_link:
                    player_url = urljoin('https://afltables.com/afl/stats/', player_link['href'])
                    scrape_player_page(player_url, team_directory)


if __name__ == "__main__":
    main()
