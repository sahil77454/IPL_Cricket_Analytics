
import pandas as pd


def calculate_team_statistics(matches):
    """
    Calculate IPL team performance statistics.
    """

    teams = sorted(
        set(matches["team1"].dropna())
        | set(matches["team2"].dropna())
    )

    team_records = []

    for team in teams:

        played = matches[
            (matches["team1"] == team)
            | (matches["team2"] == team)
        ]

        matches_played = len(played)

        wins = int((played["winner"] == team).sum())

        completed = int(played["winner"].notna().sum())

        losses = completed - wins

        no_result = matches_played - completed

        win_percentage = (
            round(wins / matches_played * 100, 2)
            if matches_played > 0 else 0
        )

        team_records.append({

            "Team": team,

            "Matches Played": matches_played,

            "Wins": wins,

            "Losses": losses,

            "No Result": no_result,

            "Win Percentage": win_percentage

        })

    team_stats = pd.DataFrame(team_records)

    if not team_stats.empty:

        team_stats = team_stats.sort_values(
            by=["Wins", "Win Percentage"],
            ascending=[False, False]
        ).reset_index(drop=True)

        team_stats.insert(
            0,
            "Rank",
            range(1, len(team_stats) + 1)
        )

    return team_stats


def calculate_team_runs(deliveries):
    """
    Calculate total runs scored by each IPL team.
    """

    team_runs = (
        deliveries.groupby("batting_team")["total_runs"]
        .sum()
        .reset_index()
    )

    team_runs.columns = ["Team", "Total Runs"]

    return team_runs.sort_values(
        by="Total Runs",
        ascending=False
    )


def calculate_team_wickets(deliveries):
    """
    Calculate total wickets lost by each batting team.
    """

    team_wickets = (
        deliveries.groupby("batting_team")["is_wicket"]
        .sum()
        .reset_index()
    )

    team_wickets.columns = ["Team", "Total Wickets"]

    return team_wickets.sort_values(
        by="Total Wickets",
        ascending=False
    )


def get_team_performance(matches, deliveries, team_name):
    """
    Get detailed performance of one selected IPL team.
    """

    team_matches = matches[
        (matches["team1"] == team_name)
        | (matches["team2"] == team_name)
    ]

    team_deliveries = deliveries[
        deliveries["batting_team"] == team_name
    ]

    matches_played = len(team_matches)

    wins = int(
        (team_matches["winner"] == team_name).sum()
    )

    total_runs = int(
        team_deliveries["total_runs"].sum()
    )

    total_wickets = int(
        team_deliveries["is_wicket"].sum()
    )

    return {
        "Team": team_name,
        "Matches Played": matches_played,
        "Wins": wins,
        "Losses": int(
            team_matches["winner"].notna().sum() - wins
        ),
        "Total Runs": total_runs,
        "Total Wickets Lost": total_wickets
    }
