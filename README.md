# 🏈 AFL Data Analysis
![AFL Data Analysis Banner Image](/assets/readme_banner.png)
<div align="center">
  <img src="https://img.shields.io/github/last-commit/akareen/AFL-Data-Analysis">
  <img src="https://img.shields.io/github/contributors/akareen/AFL-Data-Analysis">
  <img src="https://img.shields.io/github/stars/akareen/AFL-Data-Analysis?style=social">
  <img src="https://img.shields.io/github/forks/akareen/AFL-Data-Analysis?style=social">
</div>
<br>
An in-depth analysis of Australian Football League (AFL) data. This repository contains comprehensive data, tools and code for exploring and analysing AFL match and player statistics, as well as historical odds data.

## Table of Contents
- [🔦 Overview](#overview)
  - [🛠 Features](#features)
- [💾 Installation](#installation)
  - [📖 Usage](#usage)
  - [🔍 Scraping Examples](#scraping-examples)
- [📚 Data Guide](#data-guide)
- [🔗 Data Sources](#data-sources)
- [🤝 Contributing](#contributing)
- [⚖️ License](#license)


## Overview

The AFL Data Analysis project provides a comprehensive platform for examining and deriving insights from AFL match and player data. Whether you're a sports enthusiast, a tipper, a data scientist, or a student, this repository offers valuable resources for diving into the world of Australian Rules Football. 

The repository currently stores match scores data from 1897 to 2023, in depth personal and game statistics for every player who have ever played in the VFL/AFL and historical odds data from 2009 to 2023. All the data is  conveniently stored in CSV format for seamless access and analysis.

Explore the **/match_and_player_data/** directory for the complete dataset. Contributions are encouraged; don't hesitate to submit a pull request!

## Features

**Current Offerings:**
- Profiles for 5,700+ players
- Statistics for 15,000+ matches, inclusive of individual player performance
- Historical odds data for strategic tipping and betting
- Cleansed data, primed for analysis
- Analytical Jupyter notebooks showcasing potential insights

**In the Pipeline:**
- Python classes for players, teams, and matches
- Dedicated database system
- Advanced scoring algorithms
- Visualization tools for performance metrics

**Suggestions?**
- Pitch in your wishlist. One current suggestion: Player GPS Data

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/akareen/AFL-Data-Analysis.git
   cd AFL-Data-Analysis
   ```

2. (Skip if you just want the data) Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

I regularly update the CSV data files in the **/match_and_player_data** directory with the latest AFL match and player data. But you can also do your own data scraping using the provided scripts in the "scripts" directory. Scripts, using the Beautiful Soup library, are available for web scraping.

To start analyzing AFL data, you can use the provided Jupyter notebooks in the "notebooks" directory. These notebooks cover a wide range of analyses and visualizations related to AFL match and player data.

### Command Line Options

- `<data_storage_directory>`: Specify the directory where the data will be stored.
- `<option>`: Choose one of the following options:
  - `matches <start year> <end year>`: Collect match scores data within the specified year range.
  - `match_details <start year> <end year>`: Collect match scores data as well as player stats within those matches for the specified year range.
  - `all_players`: Collect data for all players in the VFL/AFL.

Please note that the available data ranges from 1897 to the current year.

## Scraping Examples
While data is readily available in the repository, here's how you can use scraping if needed.

- To scrape match scores data from 1897 to 2023 and store it in the "data/match_scores" directory:

  ```bash
  python scrape.py data/match_scores matches 1897 2023
  ```

- To collect data for all players and store it in the "data/all_players" directory:

  ```bash
  python scrape.py data/all_players all_players
  ```



## Data Guide

### Match Data Explanation

The repository contains the information for all matches from 1897-2023.

**The columns for each match are as follows:**   
Year, Round, Venue, Date, Attendance,  
Home Team, Away Team,   
Home Teams Goals by Quarter, Home Teams Behinds by Quarter,  
Away Teams Goals by Quarter, Away Teams Behinds by Quarter,  
Home Total Goals, Home Total Behinds,  
Away Total Goals, Away Total Behinds,  
Winning Team, Margin  

All the columns are in **snake case** and there is a column for each quarter such as **home_q1_g** for Home Team Quarter 1 goals and **away_q1_b** for Away team Quarter 1 Behinds.

The **match_and_player_data/match_scores** directory contains the match scores data in CSV format for each year. The file format is **{YEAR}_MATCH_RESULTS.csv**.  

The **match_and_player_data/match_details** directory contains the match scores data as well as player statistics for each match in CSV format. The file format is **{YEAR}\_{HOME_TEAM}\_{AWAY_TEAM}\_GAMESTATS.csv** and **{YEAR}\_{HOME_TEAM}\_{AWAY_TEAM}\_TEAMSTATS\_{TEAM}.csv**.

An example of the match data can be seen here: [2023_MATCH_RESULTS.csv](match_and_player_data/match_scores/2023_MATCH_RESULTS.csv)  
  
  An example of the match details data (2023 Grand Final) can be seen here:  
 [2023_GF_COL_BRL_GAMESTATS.csv](match_and_player_data/match_details/2023/gamestats/2023_GF_COL_BRL_GAMESTATS.csv),   
 [2023_GF_COL_BRL_TEAMSTATS_BRL.csv](match_and_player_data/match_details/2023/teamstats/2023_GF_COL_BRL_TEAMSTATS_BRL.csv),   
 [2023_GF_COL_BRL_TEAMSTATS_COL.csv](match_and_player_data/match_details/2023/teamstats/2023_GF_COL_BRL_TEAMSTATS_COL.csv), 

----
### Player Data Explanation

#### Player Personal Data

**The columns for each player are as follows:**
First Name, Last Name, Born Date, Debut Date, Height, Weight

Inside the data all the columns are in **snake case** and the players born date along with first and last name are used to create a unique identifier for each player. The file format is **{FIRST_NAME}\_{LAST_NAME}\_{BORN_DATE}\_PERSONAL.csv**.

#### Player Performance Data

**The columns for each player are as follows:**  

Team, Year, Games Played, Opponent, Round, Result,   
Jersey Num, Kicks, Marks, Handballs, Disposals, Goals, Behinds, Hit Outs,   
Tackles, Rebound 50s, Inside 50s, Clearances, Clangers, Free Kicks For, Free Kicks Against,   
Brownlow Votes, Contested Possessions, Uncontested Possessions, Contested Marks, Marks Inside 50,   
One Percenters %, Bounces, Goal Assist, % Percentage of Game Played

Inside the data all the columns are in **snake case**. The file format is **{FIRST_NAME}\_{LAST_NAME}\_{BORN_DATE}\_PERFORMANCE.csv**.

### Team Data Explanation

The team data is stored by year in the **match_and_player_data/player_data_by_year** directory.  
The information ranges from 1951 to today. It contains all of the player personal data as well as an additional two columns for each player that have the file path to the players personal data and the players performance data. This prevents duplication whilst also allowing for easy access to the data.

## Data Sources

This project uses publicly available AFL data sources, including match scores, player statistics, and historical odds data. The data sources are as follows:

- Match and Player Data: [AFL Tables](https://afltables.com/afl/afl_index.html)
- Historical Odds Data: [AusSportsBetting](https://www.aussportsbetting.com/data/historical-afl-results-and-odds-data/)

## Contributing

AFL Data Analysis thrives on collaboration! Got a novel analysis idea or data source? Open an issue or send a pull request. Your expertise is invaluable in elevating this project.

## License

AFL Data Analysis is under the GPL 3 License. Refer to the [LICENSE](LICENSE) file for a complete understanding. This license promotes open-source by allowing modifications while ensuring derivations remain equally open.