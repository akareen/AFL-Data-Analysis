# AFL Data Analysis

![GitHub last commit](https://img.shields.io/github/last-commit/akareen/AFL-Data-Analysis)
![GitHub contributors](https://img.shields.io/github/contributors/akareen/AFL-Data-Analysis)
![GitHub stars](https://img.shields.io/github/stars/akareen/AFL-Data-Analysis?style=social)
![GitHub forks](https://img.shields.io/github/forks/akareen/AFL-Data-Analysis?style=social)

![AFL Data Analysis Banner Image](/assets/readme_banner.png)

An in-depth analysis of Australian Football League (AFL) data. This repository contains data, tools and code for exploring and analysing AFL match and player statistics, as well as historical odds data.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Data Sources](#data-sources)
- [Data Guide](#data-guide)
- [Contributing](#contributing)
- [License](#license)

## Overview

The AFL Data Analysis project provides a comprehensive platform for examining and deriving insights from AFL match and player data. Whether you're a sports enthusiast, a tipper, a data scientist, or a student, this repository offers valuable resources for diving into the world of Australian Rules Football. In addition, historical odds data from 2009 to the present is available for tipping and betting purposes.

The repository currently stores match scores data from 1897 to 2020, In depth statistics on all players who have ever played in the VFL/AFL and historical odds data from 2009 to 2021. The data is stored in CSV format for easy access and analysis.

## Features

- Analyze match statistics to gain insights into team performance.
- Explore player data to assess individual player performance.
- Visualize AFL data for a better understanding of the game.
- Historical odds data for tipping and betting analysis.
- Data cleaning and preprocessing tools for ease of analysis.
- Jupyter notebooks with example analyses and visualizations.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/akareen/AFL-Data-Analysis.git
   cd AFL-Data-Analysis
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

I regularly update the CSV data files in the "data" directory with the latest AFL match and player data. But you can also do your own data scraping using the provided scripts in the "scripts" directory. These scripts are written in Python and use the [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library for web scraping.

To start analyzing AFL data, you can use the provided Jupyter notebooks in the "notebooks" directory. These notebooks cover a wide range of analyses and visualizations related to AFL match and player data.

### Options

- `<data_storage_directory>`: Specify the directory where the data will be stored.
- `<option>`: Choose one of the following options:
  - `matches <start year> <end year>`: Collect match scores data within the specified year range.
  - `players <start year> <end year>`: Gather player statistics data within the specified year range.
  - `all_players`: Collect data for all players.

Please note that the available data ranges from 1897 to the current year.

## Examples

- To scrape match scores data from 1897 to 2020 and store it in the "data/match_scores" directory:

  ```bash
  python scrape.py data/match_scores matches 1897 2020
  ```

- To gather player statistics data from 1990 to 2023 and save it in the "data/player_stats" directory:

  ```bash
  python scrape.py data/player_stats players 1990 2023
  ```

- To collect data for all players and store it in the "data/all_players" directory:

  ```bash
  python scrape.py data/all_players all_players
  ```


## Data Sources

This project uses publicly available AFL data sources, including match scores, player statistics, and historical odds data. The data sources are as follows:

- Match and Player Data: [AFL Tables](https://afltables.com/afl/afl_index.html)
- Historical Odds Data: [AusSportsBetting](https://www.aussportsbetting.com/data/historical-afl-results-and-odds-data/)

## Data Guide

### Match Spreadsheet Column Names

| **Category**           | **Columns**                                           |
|------------------------|-------------------------------------------------------|
| **Game Info Cols**     | Year, Round, Home Team, Away Team, Date               |
| **Home Team Stats Cols** | Home Team Goals (1st, 2nd, 3rd, 4th), Home Team Behinds (1st, 2nd, 3rd, 4th), Home Team Total Goals, Home Team Total Behinds, Home Team Total Score |
| **Away Team Stats Cols** | Away Team Goals (1st, 2nd, 3rd, 4th), Away Team Behinds (1st, 2nd, 3rd, 4th), Away Team Total Goals, Away Team Total Behinds, Away Team Total Score |
| **Winning Info Cols**  | Winning Team, Margin                                  |
| **Misc Info Cols**     | Attendance, Venue                                     |


### Player Spreadsheet Column Names

| Abbreviation | Description            |
| ------------ | ---------------------- |
| `#`          | Jumper                 |
| GM           | Games played           |
| KI           | Kicks                  |
| MK           | Marks                  |
| HB           | Handballs              |
| DI           | Disposals              |
| DA           | Disposal average       |
| GL           | Goals                  |
| BH           | Behinds                |
| HO           | Hit outs               |
| TK           | Tackles                |
| RB           | Rebound 50s            |
| IF           | Inside 50s             |
| CL           | Clearances             |
| CG           | Clangers               |
| FF           | Free kicks for         |
| FA           | Free kicks against     |
| BR           | Brownlow votes         |
| CP           | Contested possessions  |
| UP           | Uncontested possessions|
| CM           | Contested marks        |
| MI           | Marks inside 50        |
| 1%           | One percenters         |
| BO           | Bounces                |
| GA           | Goal assist            |
| %P           | Percentage of game played |
| SU           | Sub (On/Off)           |
| ↑            | Subbed on              |
| ↓            | Subbed off             |


## Contributing

Contributions to AFL Data Analysis are welcome! If you have ideas for improvements, new analyses, or data sources, please open an issue or submit a pull request. We appreciate your input and help in making this project even better.

## License

This project is licensed under the GPL 3 License - see the [LICENSE](LICENSE) file for details.