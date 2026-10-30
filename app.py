import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Premier League 2024-25 | Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

.stApp {
    background-color: #090E1A;
    color: #F5F7FA;
}

[data-testid="stHeader"] {
    background: rgba(9, 14, 26, 0.95);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #293750;
}

[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

h1, h2 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

h3 {
    color: #C4B5FD !important;
}

p, label {
    color: #CBD5E1;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172238, #111827);
    border: 1px solid #293750;
    padding: 20px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #A5B4CC !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #B8FF3B !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] > div {
    background-color: #172238;
    border: 1px solid #394966;
    border-radius: 8px;
}

[data-testid="stDataFrame"] {
    background-color: #111827;
    border: 1px solid #293750;
    border-radius: 10px;
}

[data-testid="stVegaLiteChart"],
[data-testid="stPyplot"] {
    background-color: #111827;
    border: 1px solid #293750;
    border-radius: 12px;
    padding: 10px;
}

.stButton > button {
    background-color: #B8FF3B;
    color: #090E1A;
    border: none;
    border-radius: 8px;
    font-weight: 700;
}

hr {
    border-top: 1px solid #293750;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


BACKGROUND = "#111827"
TEXT_COLOR = "#E5E7EB"
MUTED_COLOR = "#94A3B8"
GREEN = "#B8FF3B"
PURPLE = "#A78BFA"
BLUE = "#38BDF8"
RED = "#FB7185"
BORDER = "#293750"


def style_chart(ax, title, ylabel=None):
    ax.set_facecolor(BACKGROUND)
    ax.set_title(
        title,
        color=TEXT_COLOR,
        fontsize=13,
        fontweight="bold",
        pad=15
    )

    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED_COLOR)

    ax.tick_params(colors=MUTED_COLOR)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["left"].set_color(BORDER)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.2,
        color=MUTED_COLOR
    )

    ax.set_axisbelow(True)


@st.cache_data
def load_data():
    data = pd.read_csv("E0.csv")

    required_columns = [
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data["FTHG"] = pd.to_numeric(data["FTHG"], errors="coerce")
    data["FTAG"] = pd.to_numeric(data["FTAG"], errors="coerce")

    data = data.dropna(subset=required_columns).copy()

    invalid_scores = (data["FTHG"] < 0) | (data["FTAG"] < 0)
    if invalid_scores.any():
        raise ValueError("The dataset contains negative goal values.")

    valid_results = data["FTR"].isin(["H", "D", "A"])
    if not valid_results.all():
        raise ValueError("The dataset contains an unknown match result.")

    result_mismatch = (
        ((data["FTHG"] > data["FTAG"]) & (data["FTR"] != "H"))
        | ((data["FTHG"] < data["FTAG"]) & (data["FTR"] != "A"))
        | ((data["FTHG"] == data["FTAG"]) & (data["FTR"] != "D"))
    )
    if result_mismatch.any():
        raise ValueError("Some match results do not agree with the final scores.")

    return data


try:
    df = load_data()

except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


teams = sorted(
    set(df["HomeTeam"].unique()) |
    set(df["AwayTeam"].unique())
)


home_wins = (
    df.loc[df["FTR"] == "H", "HomeTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)

away_wins = (
    df.loc[df["FTR"] == "A", "AwayTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)

home_draws = (
    df.loc[df["FTR"] == "D", "HomeTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)

away_draws = (
    df.loc[df["FTR"] == "D", "AwayTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)

home_losses = (
    df.loc[df["FTR"] == "A", "HomeTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)

away_losses = (
    df.loc[df["FTR"] == "H", "AwayTeam"]
    .value_counts()
    .reindex(teams, fill_value=0)
)


home_goals = (
    df.groupby("HomeTeam")["FTHG"]
    .sum()
    .reindex(teams, fill_value=0)
)

away_goals = (
    df.groupby("AwayTeam")["FTAG"]
    .sum()
    .reindex(teams, fill_value=0)
)


home_conceded = (
    df.groupby("HomeTeam")["FTAG"]
    .sum()
    .reindex(teams, fill_value=0)
)

away_conceded = (
    df.groupby("AwayTeam")["FTHG"]
    .sum()
    .reindex(teams, fill_value=0)
)


team_data = pd.DataFrame(index=teams)

team_data["Home Wins"] = home_wins
team_data["Away Wins"] = away_wins

team_data["Home Draws"] = home_draws
team_data["Away Draws"] = away_draws

team_data["Home Losses"] = home_losses
team_data["Away Losses"] = away_losses

team_data["Wins"] = (
    team_data["Home Wins"] +
    team_data["Away Wins"]
)

team_data["Draws"] = (
    team_data["Home Draws"] +
    team_data["Away Draws"]
)

team_data["Losses"] = (
    team_data["Home Losses"] +
    team_data["Away Losses"]
)

team_data["Played"] = (
    team_data["Wins"] +
    team_data["Draws"] +
    team_data["Losses"]
)

team_data["Points"] = (
    team_data["Wins"] * 3 +
    team_data["Draws"]
)

team_data["Home Goals"] = home_goals
team_data["Away Goals"] = away_goals

team_data["Home Conceded"] = home_conceded
team_data["Away Conceded"] = away_conceded

team_data["Goals For"] = (
    team_data["Home Goals"] +
    team_data["Away Goals"]
)

team_data["Goals Against"] = (
    team_data["Home Conceded"] +
    team_data["Away Conceded"]
)

team_data["GD"] = (
    team_data["Goals For"] -
    team_data["Goals Against"]
)


st.html("""
<div style="
    background: linear-gradient(110deg, #25164A, #111827);
    padding: 30px;
    border-radius: 16px;
    border: 1px solid #49377A;
    margin-bottom: 25px;
">

    <div style="
        color: #B8FF3B;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 3px;
    ">
        FOOTBALL INTELLIGENCE
    </div>

    <h1 style="
        color: white;
        font-size: 38px;
        margin: 10px 0;
    ">
        PREMIER LEAGUE
    </h1>

    <div style="
        color: #C4B5FD;
        font-size: 20px;
        font-weight: 600;
    ">
        2024 / 25 SEASON ANALYTICS
    </div>

    <p style="
        color: #A5B4CC;
        font-size: 14px;
        margin-top: 15px;
    ">
        A data-driven breakdown of team performance,
        scoring patterns and league statistics.
    </p>

</div>
""")


total_matches = len(df)
total_teams = len(teams)

total_goals = int(
    df["FTHG"].sum() + df["FTAG"].sum()
)

average_goals = total_goals / total_matches

home_win_count = int((df["FTR"] == "H").sum())
away_win_count = int((df["FTR"] == "A").sum())
draw_count = int((df["FTR"] == "D").sum())


st.markdown("## SEASON OVERVIEW")


st.html("""
<style>
.kpi-card {
    background: linear-gradient(145deg, #172238, #111827);
    border: 1px solid #293750;
    border-radius: 12px;
    padding: 20px;
    min-height: 125px;
    margin-bottom: 10px;
}

.kpi-label {
    color: #A5B4CC;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.kpi-value {
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 800;
    margin-top: 12px;
}

.kpi-accent {
    height: 4px;
    width: 42px;
    border-radius: 5px;
    margin-top: 12px;
}
</style>
""")


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Matches</div>
        <div class="kpi-value">{total_matches}</div>
        <div class="kpi-accent" style="background:#B8FF3B;"></div>
    </div>
    """)

with kpi2:
    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Teams</div>
        <div class="kpi-value">{total_teams}</div>
        <div class="kpi-accent" style="background:#A78BFA;"></div>
    </div>
    """)

with kpi3:
    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Goals</div>
        <div class="kpi-value">{total_goals:,}</div>
        <div class="kpi-accent" style="background:#38BDF8;"></div>
    </div>
    """)

with kpi4:
    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">Goals Per Match</div>
        <div class="kpi-value">{average_goals:.2f}</div>
        <div class="kpi-accent" style="background:#FB7185;"></div>
    </div>
    """)

st.markdown("---")


st.markdown("## LEAGUE STANDINGS")


league_table = (
    team_data.sort_values(
        by=["Points", "GD", "Goals For"],
        ascending=False
    )
    .reset_index()
    .rename(columns={"index": "Team"})
)

league_table.insert(
    0,
    "Position",
    range(1, len(league_table) + 1)
)


display_columns = [
    "Position",
    "Team",
    "Played",
    "Wins",
    "Draws",
    "Losses",
    "Goals For",
    "Goals Against",
    "GD",
    "Points"
]

display_table = league_table[display_columns].copy()


def style_position(row):
    position = row["Position"]

    if position <= 4:
        return ["background-color: #163323; color: #B8FF3B; font-weight: bold;"] * len(row)

    elif position == 5:
        return ["background-color: #292044; color: #C4B5FD;"] * len(row)

    elif position >= 18:
        return ["background-color: #3B1D29; color: #FB7185;"] * len(row)

    return ["background-color: #141B2D; color: #E5E7EB;"] * len(row)


styled_table = (
    display_table.style
    .apply(style_position, axis=1)
    .format({
        "Position": "{:.0f}",
        "Played": "{:.0f}",
        "Wins": "{:.0f}",
        "Draws": "{:.0f}",
        "Losses": "{:.0f}",
        "Goals For": "{:.0f}",
        "Goals Against": "{:.0f}",
        "GD": "{:+.0f}",
        "Points": "{:.0f}"
    })
    .set_properties(**{
        "text-align": "center",
        "border": "1px solid #293750",
        "padding": "10px"
    })
    .set_properties(
        subset=["Team"],
        **{
            "text-align": "left",
            "font-weight": "bold"
        }
    )
    .set_properties(
        subset=["Points"],
        **{
            "color": "#B8FF3B",
            "font-weight": "bold"
        }
    )
)

st.dataframe(
    styled_table,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


st.markdown("## TEAM PERFORMANCE CENTRE")


selected_team = st.selectbox(
    "SELECT A CLUB",
    teams,
    key="team_selector"
)

selected_stats = team_data.loc[selected_team]


st.html(f"""
<div style="
    background: linear-gradient(110deg, #25164A, #172238);
    border: 1px solid #49377A;
    border-radius: 14px;
    padding: 22px 25px;
    margin-top: 15px;
    margin-bottom: 20px;
">

    <div style="
        color: #B8FF3B;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
    ">
        CLUB PERFORMANCE REPORT
    </div>

    <div style="
        color: white;
        font-size: 28px;
        font-weight: 800;
        margin-top: 8px;
    ">
        {selected_team.upper()}
    </div>

    <div style="
        color: #C4B5FD;
        font-size: 13px;
        margin-top: 5px;
    ">
        PREMIER LEAGUE 2024 / 25
    </div>

</div>
""")


st.markdown("### SEASON STATISTICS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "POINTS",
        int(selected_stats["Points"])
    )

with col2:
    st.metric(
        "WINS",
        int(selected_stats["Wins"])
    )

with col3:
    st.metric(
        "GOALS SCORED",
        int(selected_stats["Goals For"])
    )

with col4:
    st.metric(
        "GOAL DIFFERENCE",
        f'{int(selected_stats["GD"]):+d}'
    )


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "MATCHES PLAYED",
        int(selected_stats["Played"])
    )

with col2:
    st.metric(
        "DRAWS",
        int(selected_stats["Draws"])
    )

with col3:
    st.metric(
        "LOSSES",
        int(selected_stats["Losses"])
    )

with col4:
    st.metric(
        "GOALS CONCEDED",
        int(selected_stats["Goals Against"])
    )

st.markdown("---")


st.markdown("### HOME VS AWAY PERFORMANCE")

fig, ax = plt.subplots(figsize=(11, 4))

fig.patch.set_facecolor(BACKGROUND)

categories = ["Wins", "Draws", "Losses"]

home_values = [
    selected_stats["Home Wins"],
    selected_stats["Home Draws"],
    selected_stats["Home Losses"]
]

away_values = [
    selected_stats["Away Wins"],
    selected_stats["Away Draws"],
    selected_stats["Away Losses"]
]

x = range(len(categories))
width = 0.35

bars1 = ax.bar(
    [i - width / 2 for i in x],
    home_values,
    width,
    label="HOME",
    color=GREEN
)

bars2 = ax.bar(
    [i + width / 2 for i in x],
    away_values,
    width,
    label="AWAY",
    color=PURPLE
)

ax.set_xticks(list(x))
ax.set_xticklabels(categories)

style_chart(
    ax,
    f"{selected_team.upper()} — HOME VS AWAY RESULTS"
)

ax.legend(
    facecolor=BACKGROUND,
    labelcolor=TEXT_COLOR,
    frameon=False
)

ax.bar_label(
    bars1,
    color=TEXT_COLOR,
    padding=3
)

ax.bar_label(
    bars2,
    color=TEXT_COLOR,
    padding=3
)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("---")


st.markdown("## ATTACKING PERFORMANCE")

top_scoring = (
    team_data.sort_values(
        by="Goals For",
        ascending=False
    )
    .head(10)
)

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BACKGROUND)

bars = ax.barh(
    top_scoring.index[::-1],
    top_scoring["Goals For"][::-1],
    color=GREEN,
    height=0.65
)

style_chart(
    ax,
    "TOP 10 ATTACKING TEAMS",
    "Goals Scored"
)

ax.bar_label(
    bars,
    color=TEXT_COLOR,
    padding=5,
    fontweight="bold"
)

ax.set_xlim(
    0,
    top_scoring["Goals For"].max() * 1.15
)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("### ATTACKING RANKINGS")

st.dataframe(
    top_scoring[
        ["Goals For", "Goals Against", "GD", "Points"]
    ],
    use_container_width=True
)

st.markdown("---")


st.markdown("## DEFENSIVE PERFORMANCE")

best_defence = (
    team_data.sort_values(
        by="Goals Against",
        ascending=True
    )
    .head(10)
)

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BACKGROUND)

bars = ax.barh(
    best_defence.index[::-1],
    best_defence["Goals Against"][::-1],
    color=BLUE,
    height=0.65
)

style_chart(
    ax,
    "BEST DEFENSIVE TEAMS",
    "Goals Conceded"
)

ax.bar_label(
    bars,
    color=TEXT_COLOR,
    padding=5,
    fontweight="bold"
)

ax.set_xlim(
    0,
    best_defence["Goals Against"].max() * 1.15
)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("### DEFENSIVE RANKINGS")

st.dataframe(
    best_defence[
        ["Goals Against", "Goals For", "GD", "Points"]
    ],
    use_container_width=True
)

st.markdown("---")


st.markdown("## HOME VS AWAY ANALYSIS")


home_win_rate = home_win_count / total_matches * 100
draw_rate = draw_count / total_matches * 100
away_win_rate = away_win_count / total_matches * 100

home_average = df["FTHG"].mean()
away_average = df["FTAG"].mean()

home_goal_difference = (
    df["FTHG"].sum() - df["FTAG"].sum()
)


st.markdown("### MATCH RESULT DISTRIBUTION")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "HOME WINS",
        home_win_count,
        f"{home_win_rate:.2f}%"
    )

with col2:
    st.metric(
        "DRAWS",
        draw_count,
        f"{draw_rate:.2f}%"
    )

with col3:
    st.metric(
        "AWAY WINS",
        away_win_count,
        f"{away_win_rate:.2f}%"
    )

fig, ax = plt.subplots(figsize=(11, 4))
fig.patch.set_facecolor(BACKGROUND)

result_labels = ["Home Wins", "Draws", "Away Wins"]
result_values = [
    home_win_count,
    draw_count,
    away_win_count
]

bars = ax.bar(
    result_labels,
    result_values,
    color=[GREEN, PURPLE, BLUE],
    width=0.55
)

style_chart(
    ax,
    "HOME ADVANTAGE — MATCH OUTCOMES",
    "Number of Matches"
)

ax.bar_label(
    bars,
    color=TEXT_COLOR,
    padding=5,
    fontweight="bold"
)

ax.set_ylim(0, max(result_values) * 1.18)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("---")


st.markdown("### GOAL SCORING COMPARISON")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "AVERAGE HOME GOALS",
        f"{home_average:.2f}"
    )

with col2:
    st.metric(
        "AVERAGE AWAY GOALS",
        f"{away_average:.2f}"
    )

fig, ax = plt.subplots(figsize=(11, 4))
fig.patch.set_facecolor(BACKGROUND)

goal_labels = ["Home Goals", "Away Goals"]
goal_values = [home_average, away_average]

bars = ax.bar(
    goal_labels,
    goal_values,
    color=[GREEN, PURPLE],
    width=0.45
)

style_chart(
    ax,
    "AVERAGE GOALS PER MATCH",
    "Goals"
)

ax.bar_label(
    bars,
    fmt="%.2f",
    color=TEXT_COLOR,
    padding=5,
    fontweight="bold"
)

ax.set_ylim(0, max(goal_values) * 1.25)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("---")


st.markdown("### HOME ADVANTAGE SUMMARY")

st.html(f"""
<div style="
    background: linear-gradient(110deg, #172238, #25164A);
    border: 1px solid #49377A;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 15px;
">

    <div style="
        color: #A5B4CC;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
    ">
        HOME GOAL ADVANTAGE
    </div>

    <div style="
        color: #B8FF3B;
        font-size: 32px;
        font-weight: 800;
        margin-top: 8px;
    ">
        +{home_goal_difference}
    </div>

    <div style="
        color: #CBD5E1;
        font-size: 13px;
        margin-top: 5px;
    ">
        More goals scored at home than away across the season.
    </div>

</div>
""")

st.markdown("---")


st.markdown("## ATTACK VS POINTS")

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BACKGROUND)

ax.scatter(
    team_data["Goals For"],
    team_data["Points"],
    color=GREEN,
    s=120,
    alpha=0.85,
    edgecolors="white",
    linewidths=0.5
)

style_chart(
    ax,
    "GOALS SCORED VS LEAGUE POINTS",
    "League Points"
)

ax.set_xlabel("Goals Scored", color=MUTED_COLOR)

for team in team_data.index:
    ax.annotate(
        team,
        (
            team_data.loc[team, "Goals For"],
            team_data.loc[team, "Points"]
        ),
        fontsize=7,
        color=TEXT_COLOR,
        xytext=(4, 4),
        textcoords="offset points"
    )

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("---")


st.markdown("## DEFENCE VS POINTS")

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BACKGROUND)

ax.scatter(
    team_data["Goals Against"],
    team_data["Points"],
    color=PURPLE,
    s=120,
    alpha=0.85,
    edgecolors="white",
    linewidths=0.5
)

style_chart(
    ax,
    "GOALS CONCEDED VS LEAGUE POINTS",
    "League Points"
)

ax.set_xlabel("Goals Conceded", color=MUTED_COLOR)

for team in team_data.index:
    ax.annotate(
        team,
        (
            team_data.loc[team, "Goals Against"],
            team_data.loc[team, "Points"]
        ),
        fontsize=7,
        color=TEXT_COLOR,
        xytext=(4, 4),
        textcoords="offset points"
    )

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.markdown("---")


st.markdown("## MATCH GOAL DISTRIBUTION")


df["Total Match Goals"] = df["FTHG"] + df["FTAG"]

goal_distribution = (
    df["Total Match Goals"]
    .value_counts()
    .sort_index()
)

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BACKGROUND)

bars = ax.bar(
    goal_distribution.index.astype(str),
    goal_distribution.values,
    color=GREEN,
    width=0.65
)

style_chart(
    ax,
    "HOW MANY GOALS WERE SCORED IN EACH MATCH?",
    "Number of Matches"
)

ax.set_xlabel("Total Goals in a Match", color=MUTED_COLOR)

ax.bar_label(
    bars,
    color=TEXT_COLOR,
    padding=4,
    fontweight="bold"
)

ax.set_ylim(
    0,
    goal_distribution.max() * 1.15
)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)


st.markdown("### GOAL DISTRIBUTION DATA")

distribution_table = goal_distribution.reset_index()

distribution_table.columns = [
    "Goals in Match",
    "Number of Matches"
]

distribution_table["Percentage"] = (
    distribution_table["Number of Matches"]
    / total_matches * 100
).round(2)

st.dataframe(
    distribution_table,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


st.html("""
<div style="
    background: linear-gradient(110deg, #172238, #111827);
    border: 1px solid #293750;
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    margin-top: 30px;
">

    <div style="
        color: #B8FF3B;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 1.5px;
    ">
        PREMIER LEAGUE 2024/25 ANALYTICS
    </div>

    <p style="
        color: #94A3B8;
        font-size: 13px;
        margin-top: 12px;
    ">
        Built with Python, Pandas, Matplotlib and Streamlit.
    </p>

    <p style="
        color: #64748B;
        font-size: 12px;
        margin-top: 8px;
    ">
        Data source: Football-Data.co.uk
    </p>

</div>
""")
