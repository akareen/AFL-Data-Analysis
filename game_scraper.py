import os
import re
import hashlib
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from bs4 import BeautifulSoup
import requests

def get_soup(url: str) -> BeautifulSoup:
    """
    Gets a BeautifulSoup object from the given URL.
    
    Args:
        url (str): The URL to get the soup from.
        
    Returns:
        BeautifulSoup: The BeautifulSoup object.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return BeautifulSoup("", 'html.parser')

class MatchScraper:
    def __init__(self):
        """
        Initialize the MatchScraper.
        """
        self.team_lineups: Dict[str, List[Dict[str, Union[str, List[str]]]]] = {}
        self.processed_lineup_keys = set()  # Track processed lineup entries
        self.base_url = "https://afltables.com/afl/seas/"  # Base URL for AFL tables

    def scrape_all_matches(self, match_folder_path: str = "./data/matches", lineup_folder_path: str = "./data/lineups") -> None:
        """
        Scrapes match details from the last processed date to the current date.

        Args:
            match_folder_path (str): The path to the folder where the match CSV files will be saved.
            lineup_folder_path (str): The path to the folder where the team lineup CSV files will be saved.

        Returns:
            None
        """
        # Ensure directories exist
        os.makedirs(match_folder_path, exist_ok=True)
        os.makedirs(lineup_folder_path, exist_ok=True)

        # Check if data already exists
        match_files = [f for f in os.listdir(match_folder_path) if f.endswith('.csv')]
        lineup_files = [f for f in os.listdir(lineup_folder_path) if f.endswith('.csv')]
        
        if match_files or lineup_files:
            print(f"Data already exists in {match_folder_path} ({len(match_files)} files) and/or {lineup_folder_path} ({len(lineup_files)} files).")
            proceed = input("Do you want to proceed with updating the data? (y/n): ").lower()
            if proceed != 'y':
                print("Scraping aborted by user.")
                return

        # Load existing team lineup data to avoid duplicates
        self._load_existing_lineup_keys(lineup_folder_path)
        
        # Get the current year and the last processed year/date
        current_year = datetime.now().year
        last_processed_year, last_processed_date = self._get_last_processed_info(match_folder_path)
        
        # Default to 2011 if no previous data exists
        start_year = last_processed_year if last_processed_year else 2011
        
        print(f"Starting delta update from {start_year} to {current_year}")
        print(f"Last processed date: {last_processed_date}")
        
        # Process each year
        for year in range(start_year, current_year + 1):
            self._process_year(year, match_folder_path, last_processed_date)
        
        # Process team lineups
        self._process_team_lineups(lineup_folder_path)

    def _get_last_processed_info(self, match_folder_path: str) -> Tuple[Optional[int], Optional[datetime]]:
        """
        Gets the last processed year and date from existing match files.
        
        Args:
            match_folder_path (str): The path to the folder where match CSV files are saved.
            
        Returns:
            Tuple[Optional[int], Optional[datetime]]: The last processed year and date.
        """
        try:
            if not os.path.exists(match_folder_path):
                return None, None
                
            csv_files = [f for f in os.listdir(match_folder_path) if f.startswith('matches_') and f.endswith('.csv')]
            
            if not csv_files:
                return None, None
            
            # Get the latest year from file names
            years = [int(f.split('_')[-1].split('.')[0]) for f in csv_files]
            latest_year = max(years) if years else None
            
            # Get the latest date from the file for the latest year
            latest_date = None
            if latest_year:
                latest_file = os.path.join(match_folder_path, f"matches_{latest_year}.csv")
                try:
                    df = pd.read_csv(latest_file)
                    if not df.empty and 'date' in df.columns:
                        latest_date_str = df['date'].max()
                        try:
                            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d %H:%M")
                        except ValueError:
                            pass
                except Exception as e:
                    print(f"Error reading latest file: {e}")
            
            return latest_year, latest_date
        except Exception as e:
            print(f"Error determining last processed info: {e}")
            return None, None

    def _load_existing_lineup_keys(self, lineup_folder_path: str) -> None:
        """
        Loads existing lineup keys to avoid duplicates.
        
        Args:
            lineup_folder_path (str): The path to the folder where team lineup CSV files are saved.
        """
        try:
            if not os.path.exists(lineup_folder_path):
                return
                
            csv_files = [f for f in os.listdir(lineup_folder_path) if f.startswith('team_lineups_') and f.endswith('.csv')]
            
            for file in csv_files:
                file_path = os.path.join(lineup_folder_path, file)
                try:
                    df = pd.read_csv(file_path)
                    for _, row in df.iterrows():
                        key = self._generate_lineup_key(row['year'], row['date'], row['round_num'], row['team_name'])
                        self.processed_lineup_keys.add(key)
                except Exception as e:
                    print(f"Error loading existing lineup data from {file}: {e}")
        except Exception as e:
            print(f"Error loading existing lineup keys: {e}")

    def _find_game_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Finds game links in the given soup.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object.
            
        Returns:
            List[str]: The list of game links.
        """
        links = []
        base_url = "https://afltables.com/afl/"  # Correct base URL for AFLTables
        a_tags = soup.find_all('a', href=lambda href: href and 'stats/games/' in href)
        for a in a_tags:
            href = a['href']
            # Handle relative URLs starting with "../"
            if href.startswith('../'):
                full_link = base_url + href[3:]  # Remove "../" and append to base URL
            elif href.startswith('/'):
                full_link = base_url[:-1] + href  # Handle absolute paths from root
            else:
                full_link = base_url + href  # Handle relative paths without "../"
            links.append(full_link)
            print(f"Generated link: {full_link}")  # Debug print to verify URLs
        return links

    def _process_year(self, year: int, folder_path: str, last_processed_date: Optional[datetime] = None) -> None:
        """
        Processes a single year by scraping all match details and writing them to a CSV file.

        Args:
            year (int): The year to scrape.
            folder_path (str): The path to the folder where the CSV files will be saved.
            last_processed_date (Optional[datetime]): The last processed date.

        Returns:
            None
        """
        print(f"Processing year {year}...")
        year_soup: BeautifulSoup = get_soup(self.base_url + str(year) + '.html')
        game_links: List[str] = self._find_game_links(year_soup)
        match_data: List[Optional[Dict[str, Any]]] = []
        
        # Track processed match keys to avoid duplicates
        processed_match_keys = set()
        
        # Load existing match data if file exists
        file_path = os.path.join(folder_path, f"matches_{year}.csv")
        if os.path.exists(file_path):
            try:
                existing_df = pd.read_csv(file_path)
                for _, row in existing_df.iterrows():
                    if 'date' in row and 'round_num' in row:
                        key = f"{row['date']}_{row['round_num']}"
                        processed_match_keys.add(key)
            except Exception as e:
                print(f"Error loading existing match data for {year}: {e}")
        
        # Process each game link
        for link in game_links:
            match_info = self._extract_match_summary_table_data(link)
            if match_info:
                # Skip matches before the last processed date
                if last_processed_date and 'date' in match_info:
                    try:
                        match_date = datetime.strptime(match_info['date'], "%Y-%m-%d %H:%M")
                        if match_date <= last_processed_date:
                            continue
                    except ValueError:
                        pass
                
                # Check for duplicates using a unique key
                match_key = f"{match_info['date']}_{match_info['round_num']}"
                if match_key not in processed_match_keys:
                    match_data.append(match_info)
                    processed_match_keys.add(match_key)
        
        # Save match data
        if match_data:
            if os.path.exists(file_path):
                # Append to existing file
                existing_df = pd.read_csv(file_path)
                new_df = pd.DataFrame(match_data)
                combined_df = pd.concat([existing_df, new_df])
                # Remove duplicates based on date and round_num
                combined_df = combined_df.drop_duplicates(subset=['date', 'round_num'], keep='last')
                combined_df.to_csv(file_path, index=False)
            else:
                # Create new file
                df = pd.DataFrame(match_data)
                df.to_csv(file_path, index=False)
            
            print(f"Saved {len(match_data)} new matches for year {year}")

    def _process_team_lineups(self, lineup_folder_path: str) -> None:
        """
        Processes team lineups, merging with existing data.
        
        Args:
            lineup_folder_path (str): The path to the folder where team lineup CSV files are saved.
        """
        for team, value in self.team_lineups.items():
            # Skip invalid team names
            if not self._is_valid_team_name(team):
                print(f"Skipping invalid team name: {team}")
                continue
                
            team_filename = team.replace(' ', '_').lower()
            file_path = os.path.join(lineup_folder_path, f"team_lineups_{team_filename}.csv")
            
            # Deduplicate lineup data
            deduplicated_data = []
            for entry in value:
                key = self._generate_lineup_key(entry['year'], entry['date'], entry['round_num'], entry['team_name'])
                if key not in self.processed_lineup_keys:
                    deduplicated_data.append(entry)
                    self.processed_lineup_keys.add(key)
            
            # If no new data after deduplication, continue to next team
            if not deduplicated_data:
                continue
            
            # Convert player lists to strings
            new_df = pd.DataFrame(deduplicated_data)
            new_df['players'] = new_df['players'].apply(lambda x: ';'.join(x) if isinstance(x, list) else x)
            
            # Merge with existing data if file exists
            if os.path.exists(file_path):
                try:
                    existing_df = pd.read_csv(file_path)
                    combined_df = pd.concat([existing_df, new_df])
                    combined_df = combined_df.drop_duplicates(subset=['year', 'date', 'round_num', 'team_name'], keep='last')
                    combined_df.to_csv(file_path, index=False, encoding='utf-8')
                except Exception as e:
                    print(f"Error merging lineup data for {team}: {e}")
                    new_df.to_csv(file_path, index=False, encoding='utf-8')
            else:
                new_df.to_csv(file_path, index=False, encoding='utf-8')
            print(f"Saved lineup data for {team} to {file_path}")

    def _is_valid_team_name(self, team_name: str) -> bool:
        """
        Checks if a team name is valid.
        
        Args:
            team_name (str): The team name to check.
            
        Returns:
            bool: True if the team name is valid, False otherwise.
        """
        # Check if the team name contains digits and periods (like an IP address)
        if re.match(r'^\d+\.\d+\.\d+', team_name):
            return False
        
        # Check if the team name is too short
        if len(team_name) < 3:
            return False
        
        # Check if the team name is mostly digits
        if sum(c.isdigit() for c in team_name) > len(team_name) / 2:
            return False
        
        # Check for known AFL team names (including historical teams)
        known_teams = [
            "adelaide", "brisbane", "carlton", "collingwood", "essendon", 
            "fremantle", "geelong", "gold coast", "greater western sydney", 
            "hawthorn", "melbourne", "north melbourne", "port adelaide", 
            "richmond", "st kilda", "sydney", "west coast", "western bulldogs",
            # Historical teams
            "fitzroy", "south melbourne", "brisbane bears", "footscray",
            "kangaroos", "north melbourne kangaroos", "university", 
            "st. kilda", "gws giants"
        ]
        
        team_lower = team_name.lower()
        return any(team in team_lower for team in known_teams)

    def _generate_lineup_key(self, year: str, date: str, round_num: str, team_name: str) -> str:
        """
        Generates a unique key for a lineup entry.
        
        Args:
            year (str): The year.
            date (str): The date.
            round_num (str): The round number.
            team_name (str): The team name.
            
        Returns:
            str: A unique key for the lineup entry.
        """
        key_str = f"{year}_{date}_{round_num}_{team_name}"
        return hashlib.md5(key_str.encode()).hexdigest()

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
            
            team_detail_tables: List[BeautifulSoup] = soup.find_all('table', class_='sortable')
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
        pattern: str = r"Round: (.+) Venue: (.+) Date: (\w+, \d+-\w+-\d{4} \d{1,2}:\d{2} (?:AM|PM))(?: \(\d{1,2}:\d{2} (?:AM|PM)\))?(?: Attendance: (\d+))?"       

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
                
            data['attendance'] = match.group(4) if match.group(4) else "N/A"
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
        for team, players in team_lineup.items():
            if not self._is_valid_team_name(team):
                continue
            lineup_entry = {
                'year': data['year'],
                'date': data['date'],
                'round_num': data['round_num'],
                'team_name': team,
                'players': players
            }
            if team not in self.team_lineups:
                self.team_lineups[team] = []
            self.team_lineups[team].append(lineup_entry)

    def _extract_player_names(self, table: BeautifulSoup) -> List[str]:
        """
        Extracts player names from a team detail table.

        Args:
            table (BeautifulSoup): The BeautifulSoup table object containing player data.

        Returns:
            List[str]: A list of player names.
        """
        try:
            player_names = []
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all('td')
                if cells and len(cells) > 0:
                    player_name = cells[0].text.strip()  # Assuming first column is player name
                    if player_name:
                        player_names.append(player_name)
            return player_names
        except Exception as e:
            print(f"Error extracting player names: {e}")
            return []

if __name__ == "__main__":
    scraper = MatchScraper()
    scraper.scrape_all_matches()  # Uses default paths "./data/matches" and "./data/lineups"