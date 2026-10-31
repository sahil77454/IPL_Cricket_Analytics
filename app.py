
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import yaml

# ==========================================================
# IPL CRICKET ANALYTICS DASHBOARD - OPTIMIZED VERSION
# ==========================================================

st.set_page_config(
    page_title="IPL Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PATHS ----------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "dataset" / "ipl"
PROCESSED_FOLDER = BASE_DIR / "dataset" / "processed"

MATCHES_FILE = PROCESSED_FOLDER / "matches.parquet"
DELIVERIES_FILE = PROCESSED_FOLDER / "deliveries.parquet"

YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}
[data-testid="stMetric"] {
    background-color: #192333;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #29364a;
}
h1, h2, h3 {
    color: #ffffff;
}
[data-testid="stSidebar"] {
    background-color: #121a27;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.title("🏏 IPL Cricket Analytics Dashboard")
st.markdown("### Indian Premier League - Data Analysis and Visualization")
st.caption(
    "Explore team performance, player statistics, runs, wickets "
    "and IPL season trends."
)

# ==========================================================
# 1. CONVERT YAML DATA TO PARQUET
# ==========================================================

def build_processed_data():

    yaml_files = sorted(DATA_FOLDER.glob("*.yaml"))
    yaml_files += sorted(DATA_FOLDER.glob("*.yml"))

    if not yaml_files:
        raise FileNotFoundError(
            f"No YAML files found in: {DATA_FOLDER}"
        )

    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

    match_records = []
    delivery_records = []

    progress = st.progress(0, text="Preparing IPL dataset...")
    status = st.empty()

    for file_number, file_path in enumerate(yaml_files, start=1):

        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = yaml.load(file, Loader=YAML_LOADER)

            if not isinstance(data, dict):
                continue

            info = data.get("info", {}) or {}
            dates = info.get("dates", []) or []

            match_date = (
                pd.to_datetime(dates[0], errors="coerce")
                if dates else pd.NaT
            )

            season = (
                int(match_date.year)
                if pd.notna(match_date) else None
            )

            teams = info.get("teams", []) or []
            outcome = info.get("outcome", {}) or {}
            toss = info.get("toss", {}) or {}
            player_of_match = info.get("player_of_match", []) or []

            match_id = file_path.stem

            match_records.append({
                "match_id": match_id,
                "date": match_date,
                "season": season,
                "city": info.get("city", "Unknown"),
                "venue": info.get("venue", "Unknown"),
                "team1": teams[0] if len(teams) > 0 else "Unknown",
                "team2": teams[1] if len(teams) > 1 else "Unknown",
                "winner": outcome.get("winner"),
                "win_by_runs": (outcome.get("by") or {}).get("runs", 0),
                "win_by_wickets": (outcome.get("by") or {}).get("wickets", 0),
                "toss_winner": toss.get("winner"),
                "toss_decision": toss.get("decision"),
                "player_of_match": ", ".join(map(str, player_of_match))
            })

            # Process innings and deliveries

            for innings_number, innings_item in enumerate(
                data.get("innings", []) or [], start=1
            ):

                if not isinstance(innings_item, dict) or not innings_item:
                    continue

                innings_name = next(iter(innings_item))
                innings_data = innings_item.get(innings_name, {}) or {}

                batting_team = innings_data.get("team", "Unknown")

                for delivery_item in innings_data.get("deliveries", []) or []:

                    if not isinstance(delivery_item, dict) or not delivery_item:
                        continue

                    over_ball = next(iter(delivery_item))
                    ball = delivery_item.get(over_ball, {}) or {}

                    runs = ball.get("runs", {}) or {}
                    extras = ball.get("extras", {}) or {}
                    wicket = ball.get("wicket", {}) or {}

                    is_wide = float(extras.get("wides", 0) or 0) > 0
                    is_no_ball = float(extras.get("noballs", 0) or 0) > 0

                    legal_ball = not (is_wide or is_no_ball)
                    batter_ball = not is_wide

                    non_bowler_extras = (
                        float(extras.get("byes", 0) or 0)
                        + float(extras.get("legbyes", 0) or 0)
                        + float(extras.get("penalty", 0) or 0)
                    )

                    total_runs = float(runs.get("total", 0) or 0)
                    bowler_runs = max(0, total_runs - non_bowler_extras)

                    delivery_records.append({
                        "match_id": match_id,
                        "date": match_date,
                        "season": season,
                        "innings": innings_number,
                        "batting_team": batting_team,
                        "batsman": ball.get("batsman"),
                        "bowler": ball.get("bowler"),
                        "batsman_runs": float(runs.get("batsman", 0) or 0),
                        "total_runs": total_runs,
                        "bowler_runs": bowler_runs,
                        "legal_ball": int(legal_ball),
                        "batter_ball": int(batter_ball),
                        "is_wicket": int(bool(wicket)),
                        "dismissal_kind": wicket.get("kind"),
                        "player_out": wicket.get("player_out"),
                        "extras_type": ", ".join(extras.keys()) if extras else ""
                    })

        except Exception as error:
            print(f"Could not read {file_path.name}: {error}")

        # Update progress every 10 files

        if file_number % 10 == 0 or file_number == len(yaml_files):

            percent = int(file_number / len(yaml_files) * 100)

            progress.progress(
                percent,
                text=f"Processing match file {file_number:,} of {len(yaml_files):,}"
            )

            status.caption(
                f"Processed {file_number:,}/{len(yaml_files):,} YAML files"
            )

    matches_df = pd.DataFrame(match_records)
    deliveries_df = pd.DataFrame(delivery_records)

    if matches_df.empty or deliveries_df.empty:
        raise ValueError(
            "No match or ball-by-ball records were extracted. "
            "Please check your YAML files."
        )

    # Save processed datasets

    matches_df.to_parquet(
        MATCHES_FILE,
        index=False,
        compression="snappy"
    )

    deliveries_df.to_parquet(
        DELIVERIES_FILE,
        index=False,
        compression="snappy"
    )

    progress.progress(100, text="IPL data processing complete!")

    status.success(
        f"Processed {len(matches_df):,} matches and "
        f"{len(deliveries_df):,} deliveries."
    )

    return matches_df, deliveries_df, len(yaml_files)


# ==========================================================
# 2. LOAD SAVED PARQUET DATA
# ==========================================================

@st.cache_data(show_spinner=False)
def load_parquet_data(matches_path, deliveries_path):

    matches_df = pd.read_parquet(matches_path)
    deliveries_df = pd.read_parquet(deliveries_path)

    matches_df["date"] = pd.to_datetime(
        matches_df["date"], errors="coerce"
    )

    deliveries_df["date"] = pd.to_datetime(
        deliveries_df["date"], errors="coerce"
    )

    return matches_df, deliveries_df


# ==========================================================
# 3. CHECK DATASET
# ==========================================================

if not DATA_FOLDER.exists():

    st.error("IPL dataset folder not found!")

    st.code(
        "IPL_Cricket_Analytics/dataset/ipl/335982.yaml"
    )

    st.stop()


# ---------------- SIDEBAR CONTROLS ----------------

st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.markdown("### Dataset Controls")

if st.sidebar.button("🔄 Rebuild dataset from YAML"):

    for processed_file in [MATCHES_FILE, DELIVERIES_FILE]:

        if processed_file.exists():
            processed_file.unlink()

    st.cache_data.clear()
    st.rerun()


try:

    if not MATCHES_FILE.exists() or not DELIVERIES_FILE.exists():

        with st.status(
            "First-time setup: converting YAML files into faster Parquet data...",
            expanded=True
        ) as setup_status:

            matches, deliveries, file_count = build_processed_data()

            setup_status.update(
                label="IPL dataset processed and saved successfully!",
                state="complete",
                expanded=False
            )

    else:

        matches, deliveries = load_parquet_data(
            str(MATCHES_FILE),
            str(DELIVERIES_FILE)
        )

        file_count = (
            len(list(DATA_FOLDER.glob("*.yaml")))
            + len(list(DATA_FOLDER.glob("*.yml")))
        )

except Exception as error:

    st.error(f"Dataset loading error: {error}")

    st.info(
        "If a Parquet dependency error occurs, run: "
        "python -m pip install pyarrow"
    )

    st.stop()


if matches.empty or deliveries.empty:

    st.error("No IPL records were loaded. Check your YAML files.")

    st.stop()


# ==========================================================
# 4. SIDEBAR FILTERS
# ==========================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboard Filters")

seasons = sorted(
    int(value)
    for value in matches["season"].dropna().unique()
)

selected_season = st.sidebar.selectbox(
    "Select IPL Season",
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


st.sidebar.markdown("---")

st.sidebar.caption(f"YAML files: {file_count:,}")
st.sidebar.caption(f"Matches loaded: {len(matches):,}")
st.sidebar.caption(f"Deliveries loaded: {len(deliveries):,}")


# ==========================================================
# 5. KPI CARDS
# ==========================================================

total_matches = len(filtered_matches)
total_runs = int(filtered_deliveries["total_runs"].sum())
total_wickets = int(filtered_deliveries["is_wicket"].sum())

total_teams = len(
    set(filtered_matches["team1"].dropna())
    | set(filtered_matches["team2"].dropna())
)

st.subheader("📊 IPL Tournament Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Matches", f"{total_matches:,}")
col2.metric("Total Runs", f"{total_runs:,}")
col3.metric("Total Wickets", f"{total_wickets:,}")
col4.metric("Total Teams", total_teams)

st.markdown("---")


# ==========================================================
# 6. DASHBOARD TABS
# ==========================================================

overview, team_tab, batting_tab, bowling_tab, match_tab = st.tabs([
    "🏆 Overview",
    "🛡️ Team Analysis",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "📋 Match Records"
])


# ==========================================================
# 7. OVERVIEW
# ==========================================================

with overview:

    st.subheader("IPL Overall Performance")

    col1, col2 = st.columns(2)

    with col1:

        team_wins = (
            filtered_matches["winner"]
            .dropna()
            .value_counts()
            .rename_axis("Team")
            .reset_index(name="Wins")
        )

        if not team_wins.empty:

            fig = px.bar(
                team_wins.sort_values("Wins"),
                x="Wins",
                y="Team",
                orientation="h",
                title="Team-wise Match Wins",
                color="Wins",
                color_continuous_scale="Blues"
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:

        season_runs = (
            filtered_deliveries.groupby("season")["total_runs"]
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

            st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:

        toss_data = (
            filtered_matches["toss_decision"]
            .dropna()
            .value_counts()
            .rename_axis("Decision")
            .reset_index(name="Matches")
        )

        if not toss_data.empty:

            fig = px.pie(
                toss_data,
                names="Decision",
                values="Matches",
                hole=0.4,
                title="Toss Decision Analysis"
            )

            st.plotly_chart(fig, use_container_width=True)

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
                title="Top 10 Player of the Match Awards"
            )

            st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# 8. TEAM ANALYSIS
# ==========================================================

with team_tab:

    st.subheader("🏆 Team Performance Analysis")

    team_rows = []

    for team in teams:

        played = filtered_matches[
            (filtered_matches["team1"] == team)
            | (filtered_matches["team2"] == team)
        ]

        wins = int((played["winner"] == team).sum())
        losses = int(played["winner"].notna().sum() - wins)
        no_result = int(played["winner"].isna().sum())

        win_percentage = (
            round(wins / len(played) * 100, 2)
            if len(played) else 0
        )

        team_rows.append({
            "Team": team,
            "Matches Played": len(played),
            "Wins": wins,
            "Losses": losses,
            "No Result": no_result,
            "Win Percentage": win_percentage
        })

    team_stats = pd.DataFrame(team_rows).sort_values(
        "Wins", ascending=False
    )

    if not team_stats.empty:

        fig = px.bar(
            team_stats.sort_values("Wins"),
            x="Wins",
            y="Team",
            orientation="h",
            title="IPL Team Rankings by Wins",
            color="Wins"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Team Statistics")

        st.dataframe(
            team_stats,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Team-wise Total Runs")

    team_runs = (
        filtered_deliveries.groupby("batting_team")["total_runs"]
        .sum()
        .reset_index(name="Runs")
    )

    if not team_runs.empty:

        fig = px.bar(
            team_runs.sort_values("Runs"),
            x="Runs",
            y="batting_team",
            orientation="h",
            title="Total Runs Scored by Teams"
        )

        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# 9. BATTING ANALYSIS
# ==========================================================

with batting_tab:

    st.subheader("🏏 Batting Performance Analysis")

    batting_data = filtered_deliveries.dropna(
        subset=["batsman"]
    )

    batting_stats = (
        batting_data.groupby("batsman")
        .agg(
            Runs=("batsman_runs", "sum"),
            Balls_Faced=("batter_ball", "sum"),
            Fours=("batsman_runs", lambda values: int((values == 4).sum())),
            Sixes=("batsman_runs", lambda values: int((values == 6).sum()))
        )
        .reset_index()
    )

    dismissals = (
        filtered_deliveries.dropna(subset=["player_out"])
        .groupby("player_out")
        .size()
    )

    batting_stats["Dismissals"] = (
        batting_stats["batsman"]
        .map(dismissals)
        .fillna(0)
        .astype(int)
    )

    batting_stats["Average"] = batting_stats.apply(
        lambda row: round(
            row["Runs"] / row["Dismissals"], 2
        ) if row["Dismissals"] > 0 else None,
        axis=1
    )

    batting_stats["Strike Rate"] = batting_stats.apply(
        lambda row: round(
            row["Runs"] / row["Balls_Faced"] * 100, 2
        ) if row["Balls_Faced"] > 0 else 0,
        axis=1
    )

    batting_stats = batting_stats.sort_values(
        "Runs", ascending=False
    )

    top_batsmen = batting_stats.head(10)

    if not top_batsmen.empty:

        fig = px.bar(
            top_batsmen.sort_values("Runs"),
            x="Runs",
            y="batsman",
            orientation="h",
            title="Top 10 Run Scorers",
            color="Runs",
            color_continuous_scale="Viridis"
        )

        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(
            batting_stats,
            x="Balls_Faced",
            y="Runs",
            size="Strike Rate",
            hover_name="batsman",
            title="Player Runs vs Balls Faced"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Complete Batting Statistics")

        st.dataframe(
            batting_stats.rename(columns={
                "batsman": "Player",
                "Balls_Faced": "Balls Faced"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Individual Player Analysis")

        player_list = batting_stats["batsman"].tolist()

        selected_player = st.selectbox(
            "Select Player",
            player_list
        )

        player_data = batting_stats[
            batting_stats["batsman"] == selected_player
        ].iloc[0]

        p1, p2, p3, p4 = st.columns(4)

        p1.metric("Total Runs", int(player_data["Runs"]))

        p2.metric(
            "Batting Average",
            player_data["Average"]
            if pd.notna(player_data["Average"]) else "N/A"
        )

        p3.metric("Strike Rate", player_data["Strike Rate"])

        p4.metric("Sixes", int(player_data["Sixes"]))

    else:

        st.info("No batting records found for the selected filters.")


# ==========================================================
# 10. BOWLING ANALYSIS
# ==========================================================

with bowling_tab:

    st.subheader("🎯 Bowling Performance Analysis")

    not_credited = [
        "run out",
        "retired hurt",
        "retired out",
        "obstructing the field"
    ]

    credited_wickets = filtered_deliveries[
        (filtered_deliveries["is_wicket"] == 1)
        & (
            ~filtered_deliveries["dismissal_kind"]
            .fillna("")
            .str.lower()
            .isin(not_credited)
        )
    ]

    bowling_stats = (
        credited_wickets.groupby("bowler")
        .size()
        .reset_index(name="Wickets")
    )

    bowling_details = (
        filtered_deliveries.groupby("bowler")
        .agg(
            Legal_Balls=("legal_ball", "sum"),
            Runs_Conceded=("bowler_runs", "sum")
        )
        .reset_index()
    )

    bowling_stats = bowling_stats.merge(
        bowling_details,
        on="bowler",
        how="outer"
    )

    bowling_stats["Wickets"] = (
        bowling_stats["Wickets"].fillna(0).astype(int)
    )

    bowling_stats["Economy"] = bowling_stats.apply(
        lambda row: round(
            row["Runs_Conceded"] * 6 / row["Legal_Balls"], 2
        ) if row["Legal_Balls"] > 0 else 0,
        axis=1
    )

    bowling_stats = bowling_stats.sort_values(
        "Wickets", ascending=False
    )

    top_bowlers = bowling_stats.head(10)

    if not top_bowlers.empty:

        fig = px.bar(
            top_bowlers.sort_values("Wickets"),
            x="Wickets",
            y="bowler",
            orientation="h",
            title="Top 10 Wicket Taking Bowlers",
            color="Wickets",
            color_continuous_scale="Reds"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Bowling Statistics")

        st.dataframe(
            bowling_stats.rename(columns={
                "bowler": "Bowler",
                "Legal_Balls": "Legal Balls",
                "Runs_Conceded": "Runs Conceded",
                "Economy": "Economy Rate"
            }),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No bowling records found for the selected filters.")


# ==========================================================
# 11. MATCH RECORDS
# ==========================================================

with match_tab:

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

    match_display = filtered_matches[
        display_columns
    ].copy()

    match_display = match_display.sort_values(
        "date", ascending=False
    )

    st.dataframe(
        match_display,
        use_container_width=True,
        hide_index=True
    )

    csv = match_display.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Match Records CSV",
        data=csv,
        file_name="ipl_match_records.csv",
        mime="text/csv"
    )


# ==========================================================
# 12. FOOTER
# ==========================================================

st.markdown("---")

st.success("IPL Cricket Analytics Dashboard Loaded Successfully!")

st.caption(
    "IPL Data Analytics Project | Python | Pandas | PyYAML | "
    "Parquet | Plotly | Streamlit"
)

st.caption(
    f"Loaded {len(matches):,} matches and "
    f"{len(deliveries):,} ball-by-ball records "
    f"from {file_count:,} YAML files."
)
