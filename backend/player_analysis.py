
import pandas as pd


def calculate_batting_statistics(deliveries):
    """
    Calculate batting statistics for all IPL players.
    """

    batting_data = deliveries.dropna(
        subset=["batsman"]
    ).copy()

    batting_stats = (
        batting_data.groupby("batsman")
        .agg(
            Runs=("batsman_runs", "sum"),
            Balls_Faced=("batter_ball", "sum"),
            Fours=("batsman_runs", lambda x: (x == 4).sum()),
            Sixes=("batsman_runs", lambda x: (x == 6).sum())
        )
        .reset_index()
    )

    # Calculate dismissals
    dismissals = (
        deliveries.dropna(subset=["player_out"])
        .groupby("player_out")
        .size()
    )

    batting_stats["Dismissals"] = (
        batting_stats["batsman"]
        .map(dismissals)
        .fillna(0)
    )

    # Calculate batting average
    batting_stats["Average"] = batting_stats.apply(
        lambda row: round(
            row["Runs"] / row["Dismissals"], 2
        ) if row["Dismissals"] > 0 else None,
        axis=1
    )

    # Calculate strike rate
    batting_stats["Strike Rate"] = batting_stats.apply(
        lambda row: round(
            row["Runs"] / row["Balls_Faced"] * 100, 2
        ) if row["Balls_Faced"] > 0 else 0,
        axis=1
    )

    batting_stats = batting_stats.sort_values(
        "Runs",
        ascending=False
    ).reset_index(drop=True)

    return batting_stats


def get_top_batsmen(deliveries, top_n=10):
    """
    Return the top run-scoring IPL batsmen.
    """

    batting_stats = calculate_batting_statistics(deliveries)

    return batting_stats.head(top_n)


def get_top_strike_rate_players(deliveries, top_n=10):
    """
    Return players with the highest strike rates.
    """

    batting_stats = calculate_batting_statistics(deliveries)

    # Consider players who faced at least 100 balls
    qualified_players = batting_stats[
        batting_stats["Balls_Faced"] >= 100
    ]

    return qualified_players.sort_values(
        "Strike Rate",
        ascending=False
    ).head(top_n)


def get_player_performance(deliveries, player_name):
    """
    Get detailed performance of an individual batsman.
    """

    batting_stats = calculate_batting_statistics(deliveries)

    player_data = batting_stats[
        batting_stats["batsman"] == player_name
    ]

    if player_data.empty:
        return None

    return player_data.iloc[0].to_dict()


def get_player_season_performance(deliveries, player_name):
    """
    Calculate player runs season by season.
    """

    player_data = deliveries[
        deliveries["batsman"] == player_name
    ]

    season_stats = (
        player_data.groupby("season")
        .agg(
            Runs=("batsman_runs", "sum"),
            Balls_Faced=("batter_ball", "sum")
        )
        .reset_index()
    )

    season_stats["Strike Rate"] = (
        season_stats.apply(
            lambda row: round(
                row["Runs"] / row["Balls_Faced"] * 100, 2
            ) if row["Balls_Faced"] > 0 else 0,
            axis=1
        )
    )

    return season_stats
