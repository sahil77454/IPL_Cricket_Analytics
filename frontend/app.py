
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import plotly.express as px

# ==========================================================
# PROJECT PATH AND BACKEND CONNECTION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.data_loader import load_ipl_data, get_dataset_info
from backend.preprocessing import (
    preprocess_matches,
    preprocess_deliveries
)
from backend.team_analysis import (
    calculate_team_statistics,
    calculate_team_runs,
    calculate_team_wickets
)
from backend.player_analysis import (
    calculate_batting_statistics,
    get_top_batsmen
)
from backend.bowling_analysis import (
    calculate_bowling_statistics,
    get_top_bowlers,
    get_best_economy_bowlers
)

from styles import apply_custom_styles


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="IPL Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_custom_styles()


# ==========================================================
# HEADER
# ==========================================================

st.title("🏏 IPL CRICKET ANALYTICS")

st.markdown(
    "### Indian Premier League | Data Analysis & Visualization"
)

st.caption(
    "Explore team performance, batting statistics, "
    "bowling records and IPL season trends."
)


# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data(show_spinner="Loading IPL data...")
def get_data():

    matches, deliveries = load_ipl_data()

    matches = preprocess_matches(matches)

    deliveries = preprocess_deliveries(deliveries)

    return matches, deliveries


try:

    dataset_info = get_dataset_info()

    if not dataset_info["matches_file"] or not dataset_info["deliveries_file"]:

        st.error(
            "Processed IPL data not found. "
            "Please run the original root app.py once to create the Parquet files."
        )

        st.stop()

    matches, deliveries = get_data()

except Exception as error:

    st.error(f"Unable to load IPL data: {error}")

    st.stop()


# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.title("🏏 IPL Analytics")

st.sidebar.markdown("### Filters")

seasons = sorted(
    int(value)
    for value in matches["season"].dropna().unique()
)

selected_season = st.sidebar.selectbox(
    "Select Season",
    ["All Seasons"] + seasons
)

if selected_season == "All Seasons":

    filtered_matches = matches.copy()
    filtered_deliveries = deliveries.copy()

else:

    filtered_matches = matches[
        matches["season"] == selected_season
    ].copy()

    filtered_deliveries = deliveries[
        deliveries["season"] == selected_season
    ].copy()


teams = sorted(
    set(filtered_matches["team1"].dropna())
    | set(filtered_matches["team2"].dropna())
)

selected_team = st.sidebar.selectbox(
    "Select Team",
    ["All Teams"] + teams
)

if selected_team != "All Teams":

    filtered_matches = filtered_matches[
        (filtered_matches["team1"] == selected_team)
        | (filtered_matches["team2"] == selected_team)
    ].copy()

    filtered_deliveries = filtered_deliveries[
        filtered_deliveries["match_id"].isin(
            filtered_matches["match_id"]
        )
    ].copy()


st.sidebar.divider()

st.sidebar.caption(
    f"Total dataset files: {dataset_info['total_yaml_files']:,}"
)

st.sidebar.caption(
    f"Total matches: {len(matches):,}"
)


# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("📊 Tournament Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Matches",
    f"{len(filtered_matches):,}"
)

col2.metric(
    "Total Runs",
    f"{int(filtered_deliveries['total_runs'].sum()):,}"
)

col3.metric(
    "Total Wickets",
    f"{int(filtered_deliveries['is_wicket'].sum()):,}"
)

col4.metric(
    "Total Teams",
    len(teams)
)

st.divider()


# ==========================================================
# DASHBOARD TABS
# ==========================================================

overview, team_tab, batting_tab, bowling_tab, records_tab = st.tabs([

    "🏆 Overview",
    "🛡️ Team Analysis",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "📋 Match Records"

])


# ==========================================================
# OVERVIEW
# ==========================================================

with overview:

    st.subheader("IPL Overall Performance")

    col1, col2 = st.columns(2)

    # Team wins
    with col1:

        wins = (
            filtered_matches["winner"]
            .dropna()
            .value_counts()
            .rename_axis("Team")
            .reset_index(name="Wins")
        )

        if not wins.empty:

            fig = px.bar(
                wins.sort_values("Wins"),
                x="Wins",
                y="Team",
                orientation="h",
                title="Team-wise Match Wins",
                color="Wins"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # Season-wise runs
    with col2:

        season_runs = (
            filtered_deliveries
            .groupby("season")["total_runs"]
            .sum()
            .reset_index()
        )

        if not season_runs.empty:

            fig = px.line(
                season_runs,
                x="season",
                y="total_runs",
                markers=True,
                title="Season-wise Total Runs"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    col1, col2 = st.columns(2)

    # Toss analysis
    with col1:

        toss_data = (
            filtered_matches["toss_decision"]
            .dropna()
            .value_counts()
            .rename_axis("Decision")
            .reset_index(name="Count")
        )

        if not toss_data.empty:

            fig = px.pie(
                toss_data,
                names="Decision",
                values="Count",
                title="Toss Decision Analysis",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # Player awards
    with col2:

        awards = (
            filtered_matches["player_of_match"]
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(10)
            .rename_axis("Player")
            .reset_index(name="Awards")
        )

        if not awards.empty:

            fig = px.bar(
                awards.sort_values("Awards"),
                x="Awards",
                y="Player",
                orientation="h",
                title="Top Player of the Match Awards"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ==========================================================
# TEAM ANALYSIS
# ==========================================================

with team_tab:

    st.subheader("🏆 Team Performance Analysis")

    team_stats = calculate_team_statistics(
        filtered_matches
    )

    if not team_stats.empty:

        fig = px.bar(
            team_stats.sort_values("Wins"),
            x="Wins",
            y="Team",
            orientation="h",
            title="IPL Team Rankings",
            color="Wins"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Team Statistics")

        st.dataframe(
            team_stats,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Team-wise Total Runs")

    team_runs = calculate_team_runs(
        filtered_deliveries
    )

    if not team_runs.empty:

        fig = px.bar(
            team_runs.sort_values("Total Runs"),
            x="Total Runs",
            y="Team",
            orientation="h",
            title="Total Runs Scored by Teams"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Team-wise Wickets Lost")

    team_wickets = calculate_team_wickets(
        filtered_deliveries
    )

    if not team_wickets.empty:

        fig = px.bar(
            team_wickets.sort_values("Total Wickets"),
            x="Total Wickets",
            y="Team",
            orientation="h",
            title="Total Wickets Lost by Teams"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ==========================================================
# BATTING ANALYSIS
# ==========================================================

with batting_tab:

    st.subheader("🏏 Batting Performance Analysis")

    batting_stats = calculate_batting_statistics(
        filtered_deliveries
    )

    if not batting_stats.empty:

        top_players = get_top_batsmen(
            filtered_deliveries,
            10
        )

        fig = px.bar(
            top_players.sort_values("Runs"),
            x="Runs",
            y="batsman",
            orientation="h",
            title="Top 10 Run Scorers",
            color="Runs"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig = px.scatter(
            batting_stats,
            x="Balls_Faced",
            y="Runs",
            size="Strike Rate",
            hover_name="batsman",
            title="Runs vs Balls Faced"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Complete Batting Statistics")

        st.dataframe(
            batting_stats.rename(columns={
                "batsman": "Player",
                "Balls_Faced": "Balls Faced"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Individual Player Performance")

        player_list = batting_stats["batsman"].tolist()

        selected_player = st.selectbox(
            "Choose Player",
            player_list
        )

        player = batting_stats[
            batting_stats["batsman"] == selected_player
        ].iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Runs", int(player["Runs"]))

        c2.metric(
            "Average",
            round(player["Average"], 2)
            if pd.notna(player["Average"]) else "N/A"
        )

        c3.metric(
            "Strike Rate",
            round(player["Strike Rate"], 2)
        )

        c4.metric("Sixes", int(player["Sixes"]))

    else:

        st.info("No batting records available.")


# ==========================================================
# BOWLING ANALYSIS
# ==========================================================

with bowling_tab:

    st.subheader("🎯 Bowling Performance Analysis")

    bowling_stats = calculate_bowling_statistics(
        filtered_deliveries
    )

    if not bowling_stats.empty:

        top_bowlers = get_top_bowlers(
            filtered_deliveries,
            10
        )

        fig = px.bar(
            top_bowlers.sort_values("Wickets"),
            x="Wickets",
            y="bowler",
            orientation="h",
            title="Top 10 Wicket Takers",
            color="Wickets"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Best Economy Rate")

        best_economy = get_best_economy_bowlers(
            filtered_deliveries,
            10
        )

        st.dataframe(
            best_economy,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Complete Bowling Statistics")

        st.dataframe(
            bowling_stats,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No bowling records available.")


# ==========================================================
# MATCH RECORDS
# ==========================================================

with records_tab:

    st.subheader("📋 IPL Match Records")

    display_columns = [
        "date",
        "season",
        "team1",
        "team2",
        "winner",
        "toss_winner",
        "toss_decision",
        "venue",
        "player_of_match"
    ]

    match_records = filtered_matches[
        display_columns
    ].sort_values(
        "date",
        ascending=False
    )

    st.dataframe(
        match_records,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Match Records CSV",
        data=match_records.to_csv(index=False).encode("utf-8"),
        file_name="ipl_match_records.csv",
        mime="text/csv"
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.success(
    "IPL Cricket Analytics Dashboard Loaded Successfully!"
)

st.caption(
    "Developed using Python | Pandas | Streamlit | "
    "Plotly | YAML | Parquet"
)
