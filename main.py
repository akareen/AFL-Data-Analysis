from game_scraper import MatchScraper
from player_scraper import PlayerScraper

def main() -> None:
    start_year: int = 1897
    end_year: int = 2025
    folder_path = "data/"

    match_scraper: MatchScraper = MatchScraper(start_year, end_year)
    player_scraper: PlayerScraper = PlayerScraper()

    # match_scraper.scrape_all_matches(
    #     match_folder_path=folder_path + "matches", lineup_folder_path=folder_path + "lineups"
    # )
    player_scraper.scrape_all_players(
        folder_path=folder_path + "players"
    )

if __name__ == "__main__":
    main()