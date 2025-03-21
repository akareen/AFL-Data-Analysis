import os
import re
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import requests
import time

def get_soup(url: str) -> BeautifulSoup:
    """
    Gets a BeautifulSoup object from the given URL with a delay to avoid rate limiting.
    
    Args:
        url (str): The URL to get the soup from.
        
    Returns:
        BeautifulSoup: The BeautifulSoup object.
    """
    try:
        time.sleep(0.5)  # Delay to prevent overwhelming the server
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return BeautifulSoup("", 'html.parser')

class PlayerScraper:
    base_url: str = 'https://afltables.com/afl/stats/'
    team_alltime_urls: List[str] = [
        'https://afltables.com/afl/stats/alltime/adelaide.html',
        'https://afltables.com/afl/stats/alltime/brisbanel.html',  # Brisbane Lions
        'https://afltables.com/afl/stats/alltime/brisbaneb.html',  # Brisbane Bears
        'https://afltables.com/afl/stats/alltime/carlton.html',
        'https://afltables.com/afl/stats/alltime/collingwood.html',
        'https://afltables.com/afl/stats/alltime/essendon.html',
        'https://afltables.com/afl/stats/alltime/fitzroy.html',
        'https://afltables.com/afl/stats/alltime/fremantle.html',
        'https://afltables.com/afl/stats/alltime/geelong.html',
        'https://afltables.com/afl/stats/alltime/goldcoast.html',
        'https://afltables.com/afl/stats/alltime/gws.html',
        'https://afltables.com/afl/stats/alltime/hawthorn.html',
        'https://afltables.com/afl/stats/alltime/melbourne.html',
        'https://afltables.com/afl/stats/alltime/kangaroos.html',  # North Melbourne
        'https://afltables.com/afl/stats/alltime/padelaide.html',  # Port Adelaide
        'https://afltables.com/afl/stats/alltime/richmond.html',
        'https://afltables.com/afl/stats/alltime/stkilda.html',
        'https://afltables.com/afl/stats/alltime/swans.html',      # Sydney
        'https://afltables.com/afl/stats/alltime/westcoast.html',
        'https://afltables.com/afl/stats/alltime/bullldogs.html',  # Western Bulldogs
        'https://afltables.com/afl/stats/alltime/university.html'
    ]
    PLAYER_COL_TITLES: List[str] = [
        'team', 'year', 'games_played', 'opponent', 'round', 'result', 'jersey_num', 
        'kicks', 'marks', 'handballs', 'disposals', 'goals', 'behinds', 'hit_outs', 
        'tackles', 'rebound_50s', 'inside_50s', 'clearances', 'clangers', 
        'free_kicks_for', 'free_kicks_against', 'brownlow_votes', 'contested_possessions', 
        'uncontested_possessions', 'contested_marks', 'marks_inside_50', 
        'one_percenters', 'bounces', 'goal_assist', 'percentage_of_game_played', 'date'
    ]
    RETIREMENT_THRESHOLD: int = 5  # Years since last game to consider a player retired

    def _get_player_links(self) -> List[str]:
        """
        Fetches the list of player page links from team all-time pages.

        Returns:
            List[str]: List of relative URLs to individual player pages.
        """
        player_links = set()  # Use set to avoid duplicates
        for team_url in self.team_alltime_urls:
            soup = get_soup(team_url)
            if not soup:
                print(f"Failed to fetch team page: {team_url}")
                continue

            # Updated to search entire page for player links, not just first table
            link_objs = soup.select('a[href*="/players/"]')
            
            if not link_objs:
                print(f"No player links found at {team_url}")
                continue
                
            for link_obj in link_objs:
                href = link_obj['href']
                if '/players/' in href:  # Ensure it's a player link
                    # Normalize the path to remove '../' and ensure proper format
                    normalized_href = href.replace('../', '')
                    player_links.add(normalized_href)
                    print(f"Found player link: {normalized_href}")  # Debug output
        
        if not player_links:
            print("No player links found across all team pages.")
        else:
            print(f"Found {len(player_links)} player links")
        
        return list(player_links)

    def scrape_all_players(self, folder_path: str) -> None:
        """
        Scrapes all player details from the player links and writes them to CSV files.

        Args:
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        os.makedirs(folder_path, exist_ok=True)
        player_links = self._get_player_links()

        if not player_links:
            print("No player links found. Exiting.")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  # Limit workers to avoid overwhelming server
            futures = []
            for player_link in player_links:
                future = executor.submit(self._process_player, player_link, folder_path)
                futures.append(future)

            concurrent.futures.wait(futures)
            print(f"Completed scraping {len(futures)} player pages.")

    def _process_player(self, player_link: str, folder_path: str) -> None:
        """
        Processes a single player by scraping their personal and performance details and writing them to CSV files.

        Args:
            player_link (str): The link to the player's page (relative path).
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        full_url = self.base_url + player_link
        player_soup: BeautifulSoup = get_soup(full_url)
        if not player_soup:
            print(f"Failed to fetch player page: {full_url}")
            return

        try:
            personal_details = self._player_personal_details(player_soup)
            filename = self._get_filename(personal_details, folder_path)
            performance_file = os.path.join(folder_path, f"{filename}_performance_details.csv")

            # Check existing data
            last_game_date = self._get_last_game_date(performance_file)
            current_year = datetime.now().year

            if last_game_date:
                years_since_last_game = current_year - last_game_date.year
                if years_since_last_game >= self.RETIREMENT_THRESHOLD:
                    print(f"Skipping retired player {filename} (last game {last_game_date})")
                    return

            # Scrape performance details since the last game date
            performance_details = self._scrape_player_performance_details(player_soup, since_date=last_game_date)
            if not performance_details and last_game_date:
                print(f"No new data for {filename} since {last_game_date}")
                return

            self._write_player_details(personal_details, performance_details, folder_path)
        except Exception as e:
            print(f"Error processing player {full_url}: {e}")

    def _get_filename(self, personal_details: Dict[str, Optional[Union[str, int]]], folder_path: str) -> str:
        """
        Generates the base filename for a player based on their personal details.

        Args:
            personal_details (Dict[str, Optional[Union[str, int]]]): Player's personal details.
            folder_path (str): The path to the folder where files are saved.

        Returns:
            str: The base filename without extension.
        """
        born_date_str = personal_details['born_date']
        if isinstance(born_date_str, str):
            born_date = datetime.strptime(born_date_str, "%d-%m-%Y")
        else:
            born_date = born_date_str  # Already a datetime object
        return f"{personal_details['last_name']}_{personal_details['first_name']}_{born_date.strftime('%d%m%Y')}".lower()

    def _get_last_game_date(self, performance_file: str) -> Optional[datetime]:
        """
        Gets the last game date from an existing performance details file.

        Args:
            performance_file (str): Path to the performance details CSV file.

        Returns:
            Optional[datetime]: The last game date, or None if file doesn’t exist or is empty.
        """
        if not os.path.exists(performance_file):
            return None
        try:
            df = pd.read_csv(performance_file)
            if 'date' in df.columns and not df.empty:
                last_date_str = df['date'].max()
                return datetime.strptime(last_date_str, "%Y-%m-%d")
            elif 'year' in df.columns and 'round' in df.columns and not df.empty:
                # Infer date from year and round if 'date' column is missing
                last_row = df.loc[df['year'].idxmax()]  # Get latest year
                year = int(last_row['year'])
                round_num = int(re.sub(r'\D', '', last_row['round'])) if re.sub(r'\D', '', last_row['round']) else 1
                approx_date = datetime(year, 3, 1) + timedelta(weeks=round_num - 1)  # Assume season starts March 1
                return approx_date
            return None
        except Exception as e:
            print(f"Error reading {performance_file}: {e}")
            return None

    def _write_player_details(
        self,
        player_personal_details: Dict[str, Optional[Union[str, int]]],
        player_performance_details: List[List[str]],
        folder_path: str
    ) -> None:
        """
        Writes the player's personal details and performance details to separate CSV files.

        Args:
            player_personal_details (Dict[str, Optional[Union[str, int]]]): Player's personal details.
            player_performance_details (List[List[str]]): Player's performance details.
            folder_path (str): The path to the folder where the CSV files will be saved.

        Returns:
            None
        """
        filename = self._get_filename(player_personal_details, folder_path)
        personal_details_file = os.path.join(folder_path, f"{filename}_personal_details.csv")
        performance_details_file = os.path.join(folder_path, f"{filename}_performance_details.csv")

        # Write personal details (overwrite as these rarely change)
        personal_df = pd.DataFrame([player_personal_details])
        personal_df.to_csv(personal_details_file, index=False)
        print(f"Wrote personal details to {personal_details_file}")

        # Append or write performance details
        if player_performance_details:
            new_df = pd.DataFrame(player_performance_details, columns=self.PLAYER_COL_TITLES)
            if os.path.exists(performance_details_file):
                existing_df = pd.read_csv(performance_details_file)
                # Ensure 'date' column exists in existing data
                if 'date' not in existing_df.columns and 'year' in existing_df.columns and 'round' in existing_df.columns:
                    existing_df['date'] = existing_df.apply(
                        lambda row: (datetime(int(row['year']), 3, 1) + timedelta(weeks=int(re.sub(r'\D', '', row['round'] or '1')) - 1)).strftime("%Y-%m-%d"),
                        axis=1
                    )
                combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['team', 'year', 'round', 'opponent'], keep='last')
                combined_df.to_csv(performance_details_file, index=False)
            else:
                new_df.to_csv(performance_details_file, index=False)
            print(f"Updated performance details to {performance_details_file} with {len(player_performance_details)} new rows")

    def _scrape_player_performance_details(self, player_soup: BeautifulSoup, since_date: Optional[datetime] = None) -> List[List[str]]:
        """
        Scrapes the player's performance details from the player's page, optionally since a given date.

        Args:
            player_soup (BeautifulSoup): The BeautifulSoup object of the player's page.
            since_date (Optional[datetime]): Only scrape data after this date (for delta updates).

        Returns:
            List[List[str]]: A list of lists containing the player's performance details.
        """
        result = []
        tables = player_soup.find_all('table')

        for table in tables:
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            header_text = th_colspan_28.text.strip()
            try:
                team, year = header_text.split(' - ')
                year_int = int(year)
                if since_date and year_int < since_date.year:
                    continue  # Skip entire year if before since_date
            except ValueError:
                print(f"Could not parse team and year from: {header_text}")
                continue

            tbody = table.find('tbody')
            if not tbody:
                print(f"No tbody found in table for {header_text}")
                continue

            for row in tbody.find_all('tr'):
                cells = [td.text.strip() for td in row.find_all('td')]
                if len(cells) >= 26:  # Ensure enough columns for stats
                    round_str = cells[2]  # 'round' is 3rd column after team, year
                    round_num = int(re.sub(r'\D', '', round_str)) if re.sub(r'\D', '', round_str) else 1
                    game_date = datetime(year_int, 3, 1) + timedelta(weeks=round_num - 1)  # Approximate date
                    if since_date and game_date <= since_date:
                        continue  # Skip games before since_date

                    data = [team, year] + cells + [game_date.strftime("%Y-%m-%d")]
                    if len(data) < len(self.PLAYER_COL_TITLES):
                        data.extend([''] * (len(self.PLAYER_COL_TITLES) - len(data)))
                    elif len(data) > len(self.PLAYER_COL_TITLES):
                        data = data[:len(self.PLAYER_COL_TITLES)]
                    result.append(data)
        
        return result

    def _player_personal_details(self, soup: BeautifulSoup) -> Dict[str, Optional[Union[str, int]]]:
        """
        Scrapes the player's personal details from the player's page.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the player's page.

        Returns:
            Dict[str, Optional[Union[str, int]]]: A dictionary containing the player's personal details.
        """
        h1_tag = soup.find('h1')
        if not h1_tag or not h1_tag.text.strip():
            print("No player name found in h1 tag")
            full_name = ["Unknown", "Unknown"]
        else:
            full_name = h1_tag.text.strip().split()

        born_tag = soup.find('b', string='Born:')
        born_date_str = born_tag.next_sibling.strip().rstrip(' (') if born_tag else '01-Jan-1900'
        
        try:
            born_date = datetime.strptime(born_date_str, "%d-%b-%Y")
        except ValueError:
            print(f"Invalid born date format: {born_date_str}, using default")
            born_date = datetime(1900, 1, 1)

        debut_tag = soup.find('b', string='Debut:')
        if debut_tag:
            debut_age_str = debut_tag.next_sibling.strip()
            debut_age_ls = debut_age_str.split()
            debut_years = int(re.sub(r'\D', '', debut_age_ls[0])) if debut_age_ls else 0
            debut_days = int(re.sub(r'\D', '', debut_age_ls[1])) if len(debut_age_ls) > 1 else 0
            debut_date = born_date + timedelta(days=(debut_years * 365 + debut_days))
            debut_date_str = debut_date.strftime('%d-%m-%Y')
        else:
            debut_date_str = None

        height_obj = soup.find('b', string='Height:')
        weight_obj = soup.find('b', string='Weight:')
        height_str = height_obj.next_sibling.strip() if height_obj else None
        weight_str = weight_obj.next_sibling.strip() if weight_obj else None

        return {
            "first_name": full_name[0],
            "last_name": full_name[-1] if len(full_name) > 1 else "Unknown",
            "born_date": born_date.strftime('%d-%m-%Y'),
            "debut_date": debut_date_str,
            "height": int(re.sub(r'\D', '', height_str)) if height_str else -1,
            "weight": int(re.sub(r'\D', '', weight_str)) if weight_str else -1
        }

if __name__ == "__main__":
    scraper = PlayerScraper()
    scraper.scrape_all_players("./data/player_data")  # Using relative path