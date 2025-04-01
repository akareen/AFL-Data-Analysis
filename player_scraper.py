from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import time

from helper_functions import get_soup

class PlayerScraper:
    base_url: str = 'https://afltables.com/afl/stats/'
    player_letter_links: List[str] = [
        f'https://afltables.com/afl/stats/players{letter}_idx.html'
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ]
    PLAYER_COL_TITLES: List[str] = [
        'team', 'year',
        "games_played", "opponent", "round", "result", "jersey_num", "kicks", 
        "marks", "handballs", "disposals", "goals", "behinds", "hit_outs", 
        "tackles", "rebound_50s", "inside_50s", "clearances", "clangers", 
        "free_kicks_for", "free_kicks_against", "brownlow_votes", "contested_possessions", 
        "uncontested_possessions", "contested_marks", "marks_inside_50", 
        "one_percenters", "bounces", "goal_assist", "percentage_of_game_played", 
    ]

    
    def scrape_all_players(self, folder_path: str) -> None:
        """
        Scrapes all player details from the player letter links and writes them to CSV files.

        Args:
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        for link in self.player_letter_links:
            letter_soup: BeautifulSoup = get_soup(link)
            table = letter_soup.select_one('table')
            link_objs = table.select('a')
            player_links_strs: List[str] = [link_obj['href'] for link_obj in link_objs]

            for player_link in player_links_strs:
                self._process_player(player_link, folder_path)
    
    def _process_player(self, player_link: str, folder_path: str) -> None:
        """
        Processes a single player by scraping their personal and performance details and writing them to CSV files.

        Args:
            player_link (str): The link to the player's page.
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        print(f"Processing player: {player_link}")
        player_soup: BeautifulSoup = get_soup(self.base_url + player_link)
        self._write_player_details(
            player_personal_details=self._player_personal_details(player_soup),
            player_performance_details=self._scrape_player_performance_details(player_soup),
            folder_path=folder_path
        )

    def _write_player_details(
        self,
        player_personal_details: Dict[str, Optional[str]],
        player_performance_details: List[List[str]],
        folder_path: str
    ) -> None:
        """
        Writes the player's personal details and performance details to separate CSV files.

        Args:
            player_personal_details (Dict[str, Optional[str]]): A dictionary containing the player's personal details.
            player_performance_details (List[List[str]]): A list of lists containing the player's performance details.
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        if not player_personal_details['first_name'] or not player_personal_details['last_name']:
            print(f"Skipping player due to missing personal details.")
            return
        if not player_performance_details:
            print(f"Skipping player due to missing performance details.")
            return
        born_date_for_file = player_personal_details['born_date'].strftime('%d%m%Y')
        filename = f"{player_personal_details['last_name']}_{player_personal_details['first_name']}_{born_date_for_file}".lower()

        personal_details_file = f"{folder_path}/{filename}_personal_details.csv"
        performance_details_file = f"{folder_path}/{filename}_performance_details.csv"

        personal_df = pd.DataFrame(player_personal_details, index=[0])
        personal_df.to_csv(personal_details_file, index=False)

        performance_df = pd.DataFrame(player_performance_details, columns=self.PLAYER_COL_TITLES)
        performance_df.to_csv(performance_details_file, index=False)   

    def _scrape_player_performance_details(self, player_soup: BeautifulSoup) -> List[List[str]]:
        """
        Scrapes the player's performance details from the player's page.

        Args:
            player_soup (BeautifulSoup): The BeautifulSoup object of the player's page.

        Returns:
            List[List[str]]: A list of lists containing the player's performance details.
        """
        result = []

        tables = [table for table in player_soup.find_all('table')]
        for table in tables:
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            team, year = th_colspan_28.text.strip().split(' - ')
            for row in table.tbody.find_all('tr'):
                data = [team, year, *[td.text.strip() for td in row.find_all('td')]]
                result.append(data)
        
        return result    
    
    def _player_personal_details(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """
        Scrapes the player's personal details from the player's page.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the player's page.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the player's personal details.
        """
        try:
            h1_tag = soup.find('h1')
            full_name = h1_tag.text.split()

            born_tag = soup.find('b', string='Born:')
            born_date_str = born_tag.next_sibling.strip().rstrip(' (') if born_tag else '01-Jan-1900'
            
            debut_age_str = born_tag.find_next('b', string='Debut:').next_sibling.strip()
            debut_age_ls = debut_age_str.split()

            debut_years = int(debut_age_ls[0][:-1])
            debut_days = int(debut_age_ls[1][:-1]) if len(debut_age_ls) > 1 else 0

            born_date = datetime.strptime(born_date_str, "%d-%b-%Y")
            debut_date = born_date + timedelta(days=(debut_years * 365 + debut_days))

            height_obj = soup.find('b', string='Height:')
            weight_obj = soup.find('b', string='Weight:')
            height_str = height_obj.next_sibling.strip() if height_obj else None
            weight_str = weight_obj.next_sibling.strip() if weight_obj else None

            return {
                "first_name": full_name[0],
                "last_name": full_name[-1],
                "born_date": born_date,
                "debut_date": debut_date.strftime('%d-%m-%Y'),
                "height": int(height_str.split()[0]) if height_str else -1,
                "weight": int(weight_str.split()[0]) if weight_str else -1
            }
        except Exception as e:
            print(f"Error scraping player details: {e}")
        return {
            "first_name": None,
            "last_name": None,
            "born_date": None,
            "debut_date": None,
            "height": None,
            "weight": None
        }