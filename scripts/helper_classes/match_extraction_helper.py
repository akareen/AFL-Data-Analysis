from datetime import datetime

# Extracts all the relevant information from a match page
def extract_match_info(rows):
    match_stats_link = "empty"

    # Process home and away rows
    for row_type in ["home", "away"]:
        row = rows[0] if row_type == "home" else rows[1]
        if row.find('td', {'width': '20%'}) is None:
            return
        team, scores, extra_info = extract_table_row_data(row)
        
        goals, behinds = unpack_team_scores(scores[:4])
        total_goals, total_behinds = sum(goals), sum(behinds)
        total_score = total_goals * 6 + total_behinds
        
        if row_type == "home":
            home_team, home_total_score = team, total_score
            home_goals, home_behinds = goals, behinds
            date, attendance, venue = extract_extra_info(extra_info)
        else:
            away_team, away_total_score = team, total_score
            away_goals, away_behinds = goals, behinds

        if row_type == "away":
            a_tag = row.find('a', href=lambda href: href and href.startswith('../stats/games'))
            if a_tag:
                match_stats_link = a_tag['href']
    
    winning_team = determine_winner(home_team, home_total_score, away_team, away_total_score)
    margin = abs(home_total_score - away_total_score)

    return {
        "venue": venue, "date": date, "attendance": attendance, "home_team": home_team, "away_team": away_team, 
        "home_goals": home_goals, "home_behinds": home_behinds,
        "away_goals": away_goals, "away_behinds": away_behinds,
        "sum_home_goals": sum(home_goals), "sum_home_behinds": sum(home_behinds), "home_total_score": home_total_score, 
        "sum_away_goals": sum(away_goals), "sum_away_behinds": sum(away_behinds), "away_total_score": away_total_score,
        "winning_team": winning_team, "margin": margin, "match_stats_link": match_stats_link
    }


# Extracts all relevant information from a table row
def extract_table_row_data(row):
    """
    Extract team, scores, and extra_info from a row
    :param row: row from the table
        row begins in the format <tr><td><a>Team</a></td><td width="20%">3.2 4.3 5.4 6.5</td><td>Extra Info</td></tr>
    :return: team, scores, extra_info
        it returns the team, scores, and extra_info
    """
    team = row.find('a').text
    scores = row.find('td', {'width': '20%'}).text.split()
    extra_info = row.find_all('td')[-1].text.split()
    return team, scores, extra_info


# Extracts the date, attendance, and venue from extra_info
def extract_extra_info(extra_info):
    """
    Extracts the date, attendance, and venue from extra_info
    :param extra_info: list of extra info from the row
        extra_info begins in the format ['Sat', '24-Apr-2021', '2:10pm', 'Att:', '7,000', 'Venue:', 'Marvel']
    :return: date, attendance, venue
        it returns the date, attendance, and venue
    """
    date = datetime.strptime(extra_info[1], "%d-%b-%Y").strftime("%d-%m-%Y")
    # if it doesnt contain 'Att:' then dont search and make it 0
    if 'Att:' not in extra_info:
        attendance = 0
    else:
        attendance = extra_info[extra_info.index('Att:') + 1].replace(',', '')
    if 'Venue:' not in extra_info:
        venue = 'Unknown'
    else:
        venue = extra_info[extra_info.index('Venue:') + 1]
    return date, attendance, venue


# Unpacks the scores into goals and behinds for each quarter
def unpack_team_scores(scores):
    """
    Unpacks the scores into goals and behinds for each quarter
    :param scores: list of scores for each quarter
        scores begins in the format ['3.2', '4.3', '5.4', '6.5']
        where it is goals.behinds and accumulates
    :return: goals, behinds
        it returns the goals and behinds for each quarter
    """
    goals_arr = []
    behinds_arr = []
    for score in scores:
        goals, behinds = map(int, score.split('.'))
        goals_arr.append(goals)
        behinds_arr.append(behinds)
    goals = [goals_arr[i] - goals_arr[i-1] if i != 0 else goals_arr[i] for i in range(4)]
    behinds = [behinds_arr[i] - behinds_arr[i-1] if i != 0 else behinds_arr[i] for i in range(4)]
    return goals, behinds


# Determines the winning team and returns the String name
def determine_winner(home_team, home_total_score, away_team, away_total_score):
    if home_total_score > away_total_score:
        return home_team
    elif away_total_score > home_total_score:
        return away_team
    else:
        return 'Match drawn'
