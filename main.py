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


def scrape_team_page_yearly(teams_url, directory):
    soup = get_soup(teams_url)
    if not soup:
        return

    for table in soup.find_all('table', class_='sortable'):
        team_link = table.find('a', href=lambda x: x and x.startswith('../teams/'))
        if not team_link:
            continue

        team_name = team_link.text.strip()
        team_directory = os.path.join(directory, team_name)
        os.makedirs(team_directory, exist_ok=True)

        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 1:
                player_link = cols[1].find('a', href=lambda x: x and x.startswith('players/'))
                if player_link:
                    player_url = urljoin('https://afltables.com/afl/stats/', player_link['href'])
                    scrape_player_page(player_url, team_directory)


def scrape_site(start_url, directory):
    soup = get_soup(start_url)
    if not soup:
        return
    
    # Find all team links on the main page
    for a in soup.find_all('a', href=lambda x: x and 'teams/' in x):
        intermediate_team_url = urljoin('https://afltables.com/afl/', a['href'])
        
        # Follow the intermediate team link
        intermediate_team_soup = get_soup(intermediate_team_url)
        if not intermediate_team_soup:
            continue
        
        # Find the first link with 'stats/teams'
        stats_link = intermediate_team_soup.find('a', href=lambda x: x and 'stats/teams' in x)
        if not stats_link:
            continue
        
        print(stats_link['href'])
        # Construct the final team stats URL explicitly
        final_team_stats_url = 'https://afltables.com/afl/' + stats_link['href'].replace('../', '')
        print(final_team_stats_url)
        final_team_stats_soup = get_soup(final_team_stats_url)
        if not final_team_stats_soup:
            continue
        
        team_name = os.path.basename(final_team_stats_url).replace('.html', '')
        team_directory = os.path.join(directory, team_name)
        os.makedirs(team_directory, exist_ok=True)

        # Follow the final team stats URL and scrape every href starting with '../players'
        for player_link in final_team_stats_soup.find_all('a', href=lambda x: x and x.startswith('../players')):
            player_url = urljoin(final_team_stats_url, player_link['href'])
            scrape_player_page(player_url, team_directory)


if __name__ == "__main__":
    # Usage
    start_url = 'https://afltables.com/afl/afl_index.html'
    directory = 'data/team_stats_players_all_time'
    scrape_site(start_url, directory)

