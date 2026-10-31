
import pandas as pd


# Dismissals that are not credited to the bowler
NON_BOWLER_WICKETS = [
    "run out",
    "retired hurt",
    "retired out",
    "obstructing the field"
]


def calculate_bowling_statistics(deliveries):
    """
    Calculate bowling statistics for all IPL bowlers.
    """

    data = deliveries.copy()

    # Calculate wickets credited to bowlers
    credited_wickets = data[
        (data["is_wicket"] == 1)
        & (
            ~data["dismissal_kind"]
            .fillna("")
            .str.lower()
            .isin(NON_BOWLER_WICKETS)
        )
    ]

    wickets = (
        credited_wickets.groupby("bowler")
        .size()
        .reset_index(name="Wickets")
    )

    # Calculate balls and runs
    bowling_stats = (
        data.groupby("bowler")
        .agg(
            Legal_Balls=("legal_ball", "sum"),
            Runs_Conceded=("bowler_runs", "sum")
        )
        .reset_index()
    )

    bowling_stats = bowling_stats.merge(
        wickets,
        on="bowler",
        how="left"
    )

    bowling_stats["Wickets"] = (
        bowling_stats["Wickets"].fillna(0).astype(int)
    )

    # Calculate overs
    bowling_stats["Overs"] = (
        bowling_stats["Legal_Balls"] // 6
        + (bowling_stats["Legal_Balls"] % 6) / 10
    )

    # Calculate economy rate
    bowling_stats["Economy"] = bowling_stats.apply(
        lambda row: round(
            row["Runs_Conceded"] * 6 / row["Legal_Balls"], 2
        ) if row["Legal_Balls"] > 0 else 0,
        axis=1
    )

    bowling_stats = bowling_stats.sort_values(
        by="Wickets",
        ascending=False
    ).reset_index(drop=True)

    return bowling_stats


def get_top_bowlers(deliveries, top_n=10):
    """
    Get the top wicket-taking bowlers.
    """

    bowling_stats = calculate_bowling_statistics(deliveries)

    return bowling_stats.head(top_n)


def get_best_economy_bowlers(deliveries, top_n=10):
    """
    Get bowlers with the lowest economy rate.
    """

    bowling_stats = calculate_bowling_statistics(deliveries)

    # Consider bowlers who bowled at least 60 legal balls
    qualified = bowling_stats[
        bowling_stats["Legal_Balls"] >= 60
    ]

    return qualified.sort_values(
        by="Economy",
        ascending=True
    ).head(top_n)


def get_bowler_performance(deliveries, bowler_name):
    """
    Get detailed statistics of an individual bowler.
    """

    bowling_stats = calculate_bowling_statistics(deliveries)

    player_data = bowling_stats[
        bowling_stats["bowler"] == bowler_name
    ]

    if player_data.empty:
        return None

    return player_data.iloc[0].to_dict()


def get_bowler_season_performance(deliveries, bowler_name):
    """
    Calculate season-wise bowling performance.
    """

    player_data = deliveries[
        deliveries["bowler"] == bowler_name
    ].copy()

    season_stats = []

    for season, season_data in player_data.groupby("season"):

        stats = calculate_bowling_statistics(season_data)

        bowler_stats = stats[
            stats["bowler"] == bowler_name
        ]

        if not bowler_stats.empty:

            row = bowler_stats.iloc[0]

            season_stats.append({
                "Season": season,
                "Wickets": row["Wickets"],
                "Runs Conceded": row["Runs_Conceded"],
                "Overs": row["Overs"],
                "Economy": row["Economy"]
            })

    return pd.DataFrame(season_stats)
