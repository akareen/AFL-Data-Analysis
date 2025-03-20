from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import json

from helper_functions import get_soup

class MatchScraper:
    """
    A class to scrape match data from the AFL Tables website.
    """
    base_url: str = 'https://afltables.com/afl/seas/'
    
    def __init__(self, start_year: int, end_year: int):
        """
        Initialize the MatchScraper with the specified start and end years.

        Args:
            start_year (int): The starting year for scraping.
            end_year (int): The ending year for scraping.
        """
        self.start_year = start_year
        self.end_year = end_year
        self.team_lineups: Dict[str, List[Dict[str, Union[str, List[str]]]]] = {}

    def scrape_all_matches(self, match_folder_path: str, lineup_folder_path: str) -> None:
        """
        Scrapes all match details from the start year to the end year and writes them to CSV files.

        Args:
            match_folder_path (str): The path to the folder where the match CSV files will be saved.
            lineup_folder_path (str): The path to the folder where the team lineup CSV files will be saved.

        Returns:
            None
        """
        for year in range(self.start_year, self.end_year + 1):
            self._process_year(year, match_folder_path)

        for team, value in self.team_lineups.items():
            team_filename = team.replace(' ', '_').lower()
            df = pd.DataFrame(value)
            df['players'] = df['players'].apply(lambda x: ';'.join(x))
            df.to_csv(f'{lineup_folder_path}/team_lineups_{team_filename}.csv', index=False, encoding='utf-8')
    
    def _process_year(self, year: int, folder_path: str) -> None:
        """
        Processes a single year by scraping all match details and writing them to a CSV file.

        Args:
            year (int): The year to scrape.
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        year_soup: BeautifulSoup = get_soup(self.base_url + str(year) + '.html')
        game_links: List[str] = self._find_game_links(year_soup)
        match_data: List[Optional[Dict[str, Any]]] = []
        
        for link in game_links:
            match_info = self._extract_match_summary_table_data(link)
            if match_info:
                match_data.append(match_info)
        
        if match_data:
            df = pd.DataFrame(match_data)
            df.to_csv(f'{folder_path}/matches_{year}.csv', index=False)

    def _extract_match_summary_table_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extracts match summary table data from the given URL.

        Args:
            url (str): The URL of the match summary page.

        Returns:
            Optional[Dict[str, Any]]: The extracted match data.
        """
        try:
            soup: BeautifulSoup = get_soup(url)
            tables = soup.find_all('table')
            
            if not tables:
                return None
                
            td_elements = tables[0].find_all('td')
            data_list: List[str] = [elem.text.strip() for elem in td_elements]
            
            if len(data_list) < 13:  # Basic validation
                return None

            data: Dict[str, Any] = self._extract_match_details(data_list)
            
            team_detail_tables: List[BeautifulSoup] = soup.find_all(class_='sortable')
            if len(team_detail_tables) < 2:
                return data
                
            team_lineup: Dict[str, List[str]] = {}
            teams: List[Dict[str, Union[str, int]]] = []
            team_data: List[str] = data_list[3:13]
            
            table_num: int = 0
            for i in range(0, len(team_data), 5):
                if i + 4 >= len(team_data):
                    break
                    
                team: Dict[str, Union[str, int, List[str]]] = {}
                team['team_name'] = team_data[i]
                
                if table_num < len(team_detail_tables):
                    team_lineup[team['team_name']] = self._extract_player_names(team_detail_tables[table_num])
                
                team['q1_goals'], team['q1_behinds'] = self._parse_score(team_data[i+1])
                team['q2_goals'], team['q2_behinds'] = self._parse_score(team_data[i+2])
                team['q3_goals'], team['q3_behinds'] = self._parse_score(team_data[i+3])
                team['final_goals'], team['final_behinds'] = self._parse_score(team_data[i+4])
                
                teams.append(team)
                table_num += 1

            data.update({f'team_{i+1}_{k}': v for i, team in enumerate(teams) for k, v in team.items()})
            self._add_team_lineups(data, team_lineup)
            
            return data
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None
    
    def _parse_score(self, score_str: str) -> Tuple[int, int]:
        """
        Parses a score string into goals and behinds.
        
        Args:
            score_str (str): The score string to parse.
            
        Returns:
            Tuple[int, int]: The goals and behinds.
        """
        parts = score_str.split('.')
        if len(parts) >= 2:
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                return 0, 0
        return 0, 0
    
    def _extract_match_details(self, data_list: List[str]) -> Dict[str, Any]:
        """
        Extracts match details from the given data list.

        Args:
            data_list (List[str]): The list of data elements.

        Returns:
            Dict[str, Any]: The extracted match details.
        """
        pattern: str = r"Round: (.+) Venue: (.+) Date: (\w+, \d+-\w+-\d{4} \d{1,2}:\d{2} (?:AM|PM))(?: \((\d{1,2}:\d{2} (?:AM|PM))\))?(?: Attendance: (\d+))?"       

        data: Dict[str, Any] = {}

        match: Optional[re.Match] = re.search(pattern, data_list[1])
        if match:
            data['round_num'] = match.group(1)
            data['venue'] = match.group(2)
            try:
                date_str = match.group(3).split('(')[0].strip()
                data['date'] = datetime.strptime(date_str, "%a, %d-%b-%Y %I:%M %p").strftime("%Y-%m-%d %H:%M")
                data['year'] = data['date'][:4]
            except ValueError:
                # Fallback for date parsing issues
                data['date'] = match.group(3)
                data['year'] = match.group(3).split('-')[-1][:4]
                
            data['attendance'] = match.group(5) if match.group(5) else "N/A"
        else:
            print(f"No match found in: {data_list[1]}")
            data['round_num'] = "Unknown"
            data['venue'] = "Unknown"
            data['date'] = "Unknown"
            data['year'] = "Unknown"
            data['attendance'] = "N/A"

        return data
    
    def _add_team_lineups(self, data: Dict[str, Any], team_lineup: Dict[str, List[str]]) -> None:
        """
        Adds team lineups to the data.

        Args:
            data (Dict[str, Any]): The match data.
            team_lineup (Dict[str, List[str]]): The team lineup data.

        Returns:
            None
        """
        for team in team_lineup:
            if team not in self.team_lineups:
                self.team_lineups[team] = []
            self.team_lineups[team].append({
                'year': data['year'],
                'date': data['date'],
                'round_num': data['round_num'],
                'team_name': team,
                'players': team_lineup[team]
            })

    def _extract_player_names(self, team_detail_table: BeautifulSoup) -> List[str]:
        """
        Extracts player names from the given team detail table.

        Args:
            team_detail_table (BeautifulSoup): The team detail table.

        Returns:
            List[str]: The list of player names.
        """
        result: List[str] = []
        links = team_detail_table.find_all("a", href=lambda href: href and href.startswith("../../players/"))
        for link in links:
            name_parts = link.text.strip().split(", ")
            if len(name_parts) == 2:
                result.append(f"{name_parts[1]} {name_parts[0]}")
            else:
                result.append(link.text.strip())
        return result

    def _find_game_links(self, year_soup: BeautifulSoup) -> List[str]:
        """
        Finds game links from the given year soup.

        Args:
            year_soup (BeautifulSoup): The soup of the year page.

        Returns:
            List[str]: The list of game links.
        """
        relative_links: List[str] = [
            link['href'] 
            for link in year_soup.find_all(
                'a', 
                href=lambda href: href and href.startswith("../stats/games/")
            )
        ]
        base_url: str = "https://afltables.com/afl/stats/"
        absolute_links: List[str] = [urljoin(base_url, link.replace("../stats/", "")) for link in relative_links]
        return absolute_links

if __name__ == "__main__":
    import os
    
    # Set start year to 2011 and end year to current year (2025)
    start_year = 2011
    end_year = 2025
    
    # Define output folder paths
    match_folder_path = "./data/matches"
    lineup_folder_path = "./data/lineups"
    
    # Create output directories if they don't exist
    os.makedirs(match_folder_path, exist_ok=True)
    os.makedirs(lineup_folder_path, exist_ok=True)
    
    # Create an instance of MatchScraper
    scraper = MatchScraper(start_year, end_year)
    
    # Run the scraper
    print(f"Starting to scrape AFL match data from {start_year} to {end_year}...")
    scraper.scrape_all_matches(match_folder_path, lineup_folder_path)
    print("Scraping completed successfully!")
