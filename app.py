
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="SupeRR Selector | RR 2027",
    page_icon="🏏",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "RR_2027_Master_Shortlist.csv"
METHOD_FILE = Path(__file__).parent / "RR_2027_Methodology.json"

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    with open(METHOD_FILE, "r", encoding="utf-8") as file:
        methodology = json.load(file)
    return df, methodology

try:
    df, methodology = load_data()
except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()

batters = df[df["player_category"] == "Batter"].copy()
bowlers = df[df["player_category"] == "Bowler"].copy()

# --------------------------------------------------
# Header and sidebar
# --------------------------------------------------
st.title("🏏 SupeRR Selector")
st.subheader("Rajasthan Royals | IPL 2027 Auction Strategy")
st.caption("Round 1 — Identifying reliable players under pressure")

st.sidebar.title("Dashboard Navigation")
page = st.sidebar.radio(
    "Choose a section",
    ["Overview", "Batters", "Bowlers", "Methodology"]
)

st.sidebar.divider()
st.sidebar.caption("Historical analysis of IPL and T20I data")

# --------------------------------------------------
# Overview
# --------------------------------------------------
if page == "Overview":

    st.header("Selection Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Players shortlisted", len(df))
    c2.metric("Batters", len(batters))
    c3.metric("Bowlers", len(bowlers))
    c4.metric(
        "Pace : Spin",
        f"{(bowlers['role'] == 'Pace').sum()} : "
        f"{(bowlers['role'] == 'Spin').sum()}"
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Batter selection scores")
        fig = px.bar(
            batters.sort_values("selection_score", ascending=True),
            x="selection_score",
            y="player_name",
            orientation="h",
            color="selection_score",
            color_continuous_scale="Blues",
            labels={
                "selection_score": "Composite score",
                "player_name": "Player"
            }
        )
        fig.update_layout(height=520, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Bowler selection scores")
        fig = px.bar(
            bowlers.sort_values("selection_score", ascending=True),
            x="selection_score",
            y="player_name",
            orientation="h",
            color="selection_score",
            color_continuous_scale="Reds",
            labels={
                "selection_score": "Composite score",
                "player_name": "Player"
            }
        )
        fig.update_layout(height=520, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Final shortlisted players")
    st.dataframe(
        df[[
            "player_name", "player_category", "role",
            "selection_score", "matches_high"
        ]],
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# Batter analysis
# --------------------------------------------------
elif page == "Batters":

    st.header("🏏 Batter Performance")

    selected_role = st.selectbox(
        "Filter by batting role",
        ["All"] + sorted(batters["role"].dropna().unique().tolist())
    )

    view = batters.copy()

    if selected_role != "All":
        view = view[view["role"] == selected_role]

    st.metric("Batters displayed", len(view))

    fig = px.scatter(
        view,
        x="strike_rate_high",
        y="batting_average_high",
        size="runs_high",
        color="role",
        hover_name="player_name",
        hover_data=["matches_high", "selection_score"],
        labels={
            "strike_rate_high": "High-pressure strike rate",
            "batting_average_high": "High-pressure batting average",
            "runs_high": "High-pressure runs"
        },
        title="Strike Rate vs Batting Average"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Batter leaderboard")
    st.dataframe(
        view[[
            "player_name", "role", "selection_score",
            "runs_high", "strike_rate_high",
            "batting_average_high", "matches_high"
        ]].sort_values("selection_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    player = st.selectbox(
        "View individual batter",
        view["player_name"].tolist()
    )

    if player:
        row = view[view["player_name"] == player].iloc[0]
        a, b, c, d = st.columns(4)
        a.metric("Runs", int(row["runs_high"]))
        b.metric("Strike rate", f"{row['strike_rate_high']:.2f}")
        c.metric("Average", f"{row['batting_average_high']:.2f}")
        d.metric("Pressure matches", int(row["matches_high"]))

# --------------------------------------------------
# Bowler analysis
# --------------------------------------------------
elif page == "Bowlers":

    st.header("🎯 Bowler Performance")

    selected_type = st.selectbox(
        "Filter bowling type",
        ["All", "Pace", "Spin"]
    )

    view = bowlers.copy()

    if selected_type != "All":
        view = view[view["role"] == selected_type]

    st.metric("Bowlers displayed", len(view))

    fig = px.scatter(
        view,
        x="economy_high",
        y="wickets_high",
        size="matches_high",
        color="role",
        hover_name="player_name",
        hover_data=[
            "dot_percentage_high",
            "ipl_matches",
            "selection_score"
        ],
        labels={
            "economy_high": "High-pressure economy",
            "wickets_high": "High-pressure wickets",
            "matches_high": "Pressure matches"
        },
        title="Wickets vs Economy"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bowler leaderboard")
    st.dataframe(
        view[[
            "player_name", "role", "selection_score",
            "wickets_high", "economy_high",
            "dot_percentage_high", "matches_high",
            "ipl_matches", "ipl_wickets", "ipl_economy"
        ]].sort_values("selection_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    player = st.selectbox(
        "View individual bowler",
        view["player_name"].tolist()
    )

    if player:
        row = view[view["player_name"] == player].iloc[0]
        a, b, c, d = st.columns(4)
        a.metric("Wickets", int(row["wickets_high"]))
        b.metric("Economy", f"{row['economy_high']:.2f}")
        c.metric("Dot-ball %", f"{row['dot_percentage_high']:.2f}%")
        d.metric("Pressure matches", int(row["matches_high"]))

# --------------------------------------------------
# Methodology
# --------------------------------------------------
elif page == "Methodology":

    st.header("📊 Analytical Methodology")

    st.subheader("Project objective")
    st.write(methodology["objective"])

    st.subheader("Data scope")
    st.json(methodology["data_scope"])

    st.subheader("Pressure definition")
    st.json(methodology["pressure_definition"])

    st.subheader("Batter model")
    st.json(methodology["batter_model"])

    st.subheader("Bowler model")
    st.json(methodology["bowler_model"])

    st.subheader("Known limitations")
    for item in methodology["limitations"]:
        st.warning(item)

    st.caption(
        "Composite scores are analytical ranking indicators, "
        "not probabilities of future success."
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "SupeRR Selector Season 2 | IPL 2027 Auction Strategy | "
    "Data-driven player evaluation"
)
