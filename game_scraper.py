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
            team = team.replace(' ', '_').lower()
            df = pd.DataFrame(value)
            df['players'] = df['players'].apply(lambda x: ';'.join(x))
            df.to_csv(f'{lineup_folder_path}/team_lineups_{team}.csv', index=False, encoding='utf-8')
    
    def _process_year(self, year: int, folder_path: str) -> None:
        """
        Processes a single year by scraping all match details and writing them to a CSV file.

        Args:
            year (int): The year to scrape.
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        print(f"Processing year: {year}")
        year_soup: BeautifulSoup = get_soup(self.base_url + str(year) + '.html')
        game_links: List[str] = self._find_game_links(year_soup)
        match_data: List[Optional[Dict[str, Any]]] = [self._extract_match_summary_table_data(link) for link in game_links]
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
        print(f"Extracting data from: {url}")
        soup: BeautifulSoup = get_soup(url)
        tables = soup.find_all('table')
        td_elements = tables[0].find_all('td')
        data_list: List[str] = [elem.text for elem in td_elements]

        data: Dict[str, Any] = self._extract_match_details(data_list)

        team_detail_tables: List[BeautifulSoup] = soup.find_all(class_='sortable', limit=2)
        team_lineup: Dict[str, List[str]] = {}
        teams: List[Dict[str, Union[str, int]]] = []
        team_data: List[str] = data_list[3:13]
        if '.' in data_list[8]:
            return data
        table_num: int = 0
        for i in range(0, len(team_data), 5):
            team: Dict[str, Union[str, int, List[str]]] = {}
            team['team_name'] = team_data[i]
            team_lineup[team['team_name']] = self._extract_player_names(team_detail_tables[table_num])
            team['q1_goals'], team['q1_behinds'], _ = map(int, team_data[i+1].split('.'))
            team['q2_goals'], team['q2_behinds'], _ = map(int, team_data[i+2].split('.'))
            team['q3_goals'], team['q3_behinds'], _ = map(int, team_data[i+3].split('.'))
            team['final_goals'], team['final_behinds'], _ = map(int, team_data[i+4].split('.'))
            teams.append(team)
            table_num += 1

        data.update({f'team_{i+1}_{k}': v for i, team in enumerate(teams) for k, v in team.items()})
        self._add_team_lineups(data, team_lineup)
        
        return data
    
    def _extract_match_details(self, data_list: List[str]) -> Dict[str, Any]:
        """
        Extracts match details from the given data list.

        Args:
            data_list (List[str]): The list of data elements.

        Returns:
            Dict[str, Any]: The extracted match details.
        """
        pattern: str = r"Round: (.+) Venue: (.+) Date: (\w+, \d+-\w+-\d{4} \d{1,2}:\d{2} (?:AM|PM))(?: \((\d{1,2}:\d{2} (?:AM|PM))\))?(?: Attendance: \d+)?"       

        data: Dict[str, Any] = {}

        match: Optional[re.Match] = re.search(pattern, data_list[1])
        if match:
            data['round_num'] = match.group(1)
            data['venue'] = match.group(2)
            data['date'] = datetime.strptime(match.group(3).split('(')[0].strip(), "%a, %d-%b-%Y %I:%M %p").strftime("%Y-%m-%d %H:%M")
            data['year'] = data['date'][:4]
            data['attendance'] = match.group(4) if match.group(4) else "N/A"
        else:
            print(f"No match found: {data_list[1]}")

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
            result.append(" ".join(reversed(link.text.strip().split(", "))))
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
        base_url: str = "https://afltables.com/afl/seas/"
        absolute_links: List[str] = [urljoin(base_url, link) for link in relative_links]
        return absolute_links