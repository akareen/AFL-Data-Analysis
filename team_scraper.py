from typing import List
from bs4 import BeautifulSoup
import pandas as pd
import requests
from requests.exceptions import RequestException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_soup(year_url: str) -> BeautifulSoup:
    """
    Fetches the HTML content of the given URL and returns a BeautifulSoup object.
    
    Args:
        year_url (str): The URL to fetch.
        
    Returns:
        BeautifulSoup: A BeautifulSoup object of the page content, or None if an error occurs.
    """
    try:
        response = requests.get(year_url)
        response.raise_for_status()  # Raises an error for 4xx and 5xx status codes
        return BeautifulSoup(response.content, 'html.parser')
    except RequestException as e:
        logging.error(f"Error fetching data from {year_url}: {e}")
        return None

class TeamScraper:
    base_url: str = 'https://afltables.com/afl/stats/'
    TEAM_COL_TITLES: List[str] = [
        'year', 'team', 'kicks', 'marks', 'handballs', 'disposals', 'goals', 
        'behinds', 'hit_outs', 'tackles', 'rebound_50s', 'inside_50s', 
        'clearances', 'clangers', 'frees_for', 'brownlow_votes', 
        'contested_possessions', 'uncontested_possessions', 'contested_marks', 
        'marks_inside_50', 'one_percenters', 'bounces', 'goal_assists'
    ]

    def scrape_team_stats(self, start_year: int, end_year: int, folder_path: str) -> None:
        for year in range(start_year, end_year + 1):
            year_url = f'{self.base_url}{year}s.html'
            soup: BeautifulSoup = get_soup(year_url)

            if soup is None:
                logging.warning(f"Failed to retrieve data for {year}.")
                continue

            team_data = self._scrape_team_performance_details(soup, year)

            if team_data:
                try:
                    stats_df = pd.DataFrame(team_data, columns=self.TEAM_COL_TITLES)
                    stats_df.to_csv(f"{folder_path}/team_stats_{year}.csv", index=False)
                    logging.info(f"Data for year {year} saved to CSV.")
                except ValueError as e:
                    logging.error(f"ValueError: {e}. Data for year {year} had {len(team_data[0])} columns.")
            else:
                logging.warning(f"No data found for year {year}.")

    def _scrape_team_performance_details(self, soup: BeautifulSoup, year: int) -> List[List[str]]:
        result = []
        tables = soup.find_all('table')

        logging.info(f"Found {len(tables)} tables for year {year}.")
        
        for table in tables:
            if "Team Totals For" in table.text:
                for row in table.tbody.find_all('tr'):
                    # Extract the columns matching the TEAM_COL_TITLES
                    data = [year] + [td.text.strip() for td in row.find_all('td')]
                    data = data[:len(self.TEAM_COL_TITLES)]

                    logging.debug(f"Scraped Data: {data}")
                    result.append(data)

        return result
