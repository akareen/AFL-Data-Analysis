from game_scraper import GameScraper
from player_scraper import PlayerScraper

def main() -> None:
    start_year: int = 1897
    end_year: int = 2024
    folder_path = "data/"

    match_scraper: GameScraper = GameScraper(start_year, end_year)
    player_scraper: PlayerScraper = PlayerScraper()

    match_scraper.scrape_all_matches(
        match_folder_path=folder_path + "matches", lineup_folder_path=folder_path + "lineups"
    )
    player_scraper.scrape_all_players(
        player_folder_path=folder_path + "players"
    )

if __name__ == "__main__":
    main()