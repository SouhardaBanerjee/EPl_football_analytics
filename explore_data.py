"""
EPL 2024-25: Match and Team Performance Analysis

Place this script in the same folder as E0.csv.
Run it from the project's activated virtual environment.

Packages required:
    python -m pip install pandas matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD THE DATA
# ============================================================

df = pd.read_csv("E0.csv")

print("Dataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nDataset information:")
df.info()

print("\nTotal missing values:", df.isna().sum().sum())
print("\nColumns containing missing values:")
missing_values = df.isna().sum()
print(missing_values[missing_values > 0].sort_values(ascending=False))

print("\nDuplicate rows:", df.duplicated().sum())


# ============================================================
# 2. CHECK THE IMPORTANT MATCH DATA
# ============================================================

# These columns are essential for our analysis.
core_columns = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
]

print("\nMissing values in important columns:")
print(df[core_columns].isna().sum())

print("\nNumber of home teams:", df["HomeTeam"].nunique())
print("Number of away teams:", df["AwayTeam"].nunique())

print("\nFull-time result counts (H=home win, D=draw, A=away win):")
print(df["FTR"].value_counts())

print("\nFull-time result percentages:")
print(df["FTR"].value_counts(normalize=True).mul(100).round(2))

# Check that result codes contain only H, D, or A.
invalid_results = df.loc[~df["FTR"].isin(["H", "D", "A"]), "FTR"]
print("\nInvalid full-time results:")
print(invalid_results)

# A team cannot play itself in a match.
same_team_matches = df["HomeTeam"] == df["AwayTeam"]
print("\nMatches where home and away teams are identical:")
print(same_team_matches.sum())

# Check whether the recorded result agrees with the score.
home_win_mismatch = (df["FTR"] == "H") & (df["FTHG"] <= df["FTAG"])
away_win_mismatch = (df["FTR"] == "A") & (df["FTAG"] <= df["FTHG"])
draw_mismatch = (df["FTR"] == "D") & (df["FTHG"] != df["FTAG"])

result_mismatches = home_win_mismatch | away_win_mismatch | draw_mismatch

print("\nNumber of result-score inconsistencies:")
print(result_mismatches.sum())

if result_mismatches.any():
    print("\nInconsistent match records:")
    print(
        df.loc[
            result_mismatches,
            ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"],
        ]
    )


# ============================================================
# 3. COUNT WINS, DRAWS, AND LOSSES FOR EACH TEAM
# ============================================================

# Get the complete list of teams.
# Using reindex later ensures that a team with zero results
# in a category still receives a value of 0, not NaN.
teams = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))

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

# Build the team-level DataFrame.
# Team names become the index, allowing Pandas to align Series
# by team name when we combine them.
team_data = pd.DataFrame(
    {
        "HomeWins": home_wins,
        "AwayWins": away_wins,
        "HomeDraws": home_draws,
        "AwayDraws": away_draws,
        "HomeLosses": home_losses,
        "AwayLosses": away_losses,
    }
)


# ============================================================
# 4. CALCULATE TOTAL RESULTS AND POINTS
# ============================================================

team_data["TotalWins"] = team_data["HomeWins"] + team_data["AwayWins"]
team_data["TotalDraws"] = team_data["HomeDraws"] + team_data["AwayDraws"]
team_data["TotalLosses"] = team_data["HomeLosses"] + team_data["AwayLosses"]

# Premier League points: 3 for a win, 1 for a draw, 0 for a loss.
team_data["Points"] = team_data["TotalWins"] * 3 + team_data["TotalDraws"]

team_data["TotalMatches"] = (
    team_data["TotalWins"]
    + team_data["TotalDraws"]
    + team_data["TotalLosses"]
)

print("\nTeam results:")
print(
    team_data[
        ["TotalWins", "TotalDraws", "TotalLosses", "TotalMatches", "Points"]
    ].to_string()
)

print("\nDo all teams have 38 matches?")
print((team_data["TotalMatches"] == 38).all())


# ============================================================
# 5. CALCULATE GOALS SCORED AND CONCEDED
# ============================================================

# Goals scored at home and away.
home_goals = df.groupby("HomeTeam")["FTHG"].sum()
away_goals = df.groupby("AwayTeam")["FTAG"].sum()

# Goals conceded at home and away.
# A home team concedes FTAG; an away team concedes FTHG.
home_goals_conceded = df.groupby("HomeTeam")["FTAG"].sum()
away_goals_conceded = df.groupby("AwayTeam")["FTHG"].sum()

# Pandas aligns these Series by their team-name indexes.
team_data["Home Goals Scored"] = home_goals
team_data["Away Goals Scored"] = away_goals
team_data["Home Goals Conceded"] = home_goals_conceded
team_data["Away Goals Conceded"] = away_goals_conceded

team_data["Total Goals Scored"] = home_goals + away_goals
team_data["Total Goals Conceded"] = (
    home_goals_conceded + away_goals_conceded
)

team_data["Goal Difference"] = (
    team_data["Total Goals Scored"] - team_data["Total Goals Conceded"]
)


# ============================================================
# 6. CREATE THE LEAGUE TABLE
# ============================================================

# Rank by points, then goal difference, then goals scored.
league_table = (
    team_data[
        [
            "TotalWins",
            "TotalDraws",
            "TotalLosses",
            "Points",
            "Total Goals Scored",
            "Total Goals Conceded",
            "Goal Difference",
        ]
    ]
    .sort_values(
        by=["Points", "Goal Difference", "Total Goals Scored"],
        ascending=[False, False, False],
    )
    .reset_index()
    .rename(columns={"index": "Team"})
)

# Add a rank column beginning at 1.
league_table.insert(0, "Position", range(1, len(league_table) + 1))

print("\nPremier League table:")
print(league_table.to_string(index=False))


# ============================================================
# 7. ANALYSE HOME ADVANTAGE
# ============================================================

team_data["Home Goal Difference"] = (
    team_data["Home Goals Scored"] - team_data["Home Goals Conceded"]
)

team_data["Away Goal Difference"] = (
    team_data["Away Goals Scored"] - team_data["Away Goals Conceded"]
)

# This is the difference between a team's home and away goal differences.
# It describes a pattern; it does not prove that playing at home caused it.
team_data["Home Advantage"] = (
    team_data["Home Goal Difference"] - team_data["Away Goal Difference"]
)

home_advantage_table = (
    team_data[
        ["Home Goal Difference", "Away Goal Difference", "Home Advantage"]
    ]
    .sort_values(by="Home Advantage", ascending=False)
    .reset_index()
    .rename(columns={"index": "Team"})
)

print("\nTop five teams by home advantage:")
print(home_advantage_table.head(5).to_string(index=False))


# Chart 1: Home advantage for the top five teams.
top_five_home_advantage = home_advantage_table.head(5).iloc[::-1]

fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.barh(
    top_five_home_advantage["Team"],
    top_five_home_advantage["Home Advantage"],
)

ax.bar_label(bars, padding=3)
ax.set_xlabel("Home Advantage (Goal Difference)")
ax.set_ylabel("Team")
ax.set_title("Top 5 Teams by Home Advantage")

plt.tight_layout()
plt.show()


# Chart 2: Home wins versus away wins for the top five teams by points.
top_five_teams = league_table.head(5)["Team"]

win_comparison = team_data.loc[top_five_teams, ["HomeWins", "AwayWins"]]

ax = win_comparison.plot(
    kind="barh",
    figsize=(9, 5),
    title="Home Wins vs Away Wins — Top 5 EPL Teams",
)

ax.set_xlabel("Number of Wins")
ax.set_ylabel("Team")
ax.legend(["Home Wins", "Away Wins"])
ax.invert_yaxis()

plt.tight_layout()
plt.show()


# ============================================================
# 8. LEAGUE-WIDE HOME AND AWAY WIN ANALYSIS
# ============================================================

total_matches = len(df)
total_home_wins = home_wins.sum()
total_away_wins = away_wins.sum()
total_draws = (df["FTR"] == "D").sum()

home_win_percentage = total_home_wins / total_matches * 100
away_win_percentage = total_away_wins / total_matches * 100
draw_percentage = total_draws / total_matches * 100

win_percentage_difference = home_win_percentage - away_win_percentage

print("\nMatch outcomes across the league:")
print(f"Home wins: {total_home_wins} ({home_win_percentage:.2f}%)")
print(f"Away wins: {total_away_wins} ({away_win_percentage:.2f}%)")
print(f"Draws: {total_draws} ({draw_percentage:.2f}%)")
print(f"Home-away win-rate difference: {win_percentage_difference:.2f} percentage points")


# ============================================================
# 9. AVERAGE GOALS PER MATCH
# ============================================================

avg_home_goals = df["FTHG"].mean()
avg_away_goals = df["FTAG"].mean()

print("\nAverage goals scored per match:")
print("Home teams:", round(avg_home_goals, 2))
print("Away teams:", round(avg_away_goals, 2))
print("Home-away difference:", round(avg_home_goals - avg_away_goals, 2))

# Goals conceded are the opponent's goals.
avg_home_goals_conceded = df["FTAG"].mean()
avg_away_goals_conceded = df["FTHG"].mean()

print("\nAverage goals conceded per match:")
print("Home teams:", round(avg_home_goals_conceded, 2))
print("Away teams:", round(avg_away_goals_conceded, 2))

avg_home_goal_difference = avg_home_goals - avg_home_goals_conceded
avg_away_goal_difference = avg_away_goals - avg_away_goals_conceded

print("\nAverage goal difference per match:")
print("Home teams:", round(avg_home_goal_difference, 2))
print("Away teams:", round(avg_away_goal_difference, 2))


# ============================================================
# 10. TOTAL GOALS AND GOAL DISTRIBUTION
# ============================================================

total_home_goals = df["FTHG"].sum()
total_away_goals = df["FTAG"].sum()
total_goals = total_home_goals + total_away_goals

avg_total_goals = total_goals / total_matches

print("\nTotal home goals:", total_home_goals)
print("Total away goals:", total_away_goals)
print("Total goals in the season:", total_goals)
print("Average total goals per match:", round(avg_total_goals, 2))

# Add the goals from both teams to get the total goals in each match.
df["Total Match Goals"] = df["FTHG"] + df["FTAG"]

# Count matches with 0 goals, 1 goal, 2 goals, and so on.
goal_distribution = df["Total Match Goals"].value_counts().sort_index()

print("\nNumber of matches for each total-goal count:")
print(goal_distribution)

ax = goal_distribution.plot(
    kind="bar",
    figsize=(9, 5),
    title="Distribution of Total Goals per Match",
)

ax.set_xlabel("Total Goals in a Match")
ax.set_ylabel("Number of Matches")

plt.tight_layout()
plt.show()


# ============================================================
# 11. ATTACKING AND DEFENSIVE RANKINGS
# ============================================================

top_scoring_teams = (
    team_data[["Total Goals Scored"]]
    .sort_values(by="Total Goals Scored", ascending=False)
    .reset_index()
    .rename(columns={"index": "Team"})
)

print("\nTop 10 teams by goals scored:")
print(top_scoring_teams.head(10).to_string(index=False))

best_defensive_teams = (
    team_data[["Total Goals Conceded"]]
    .sort_values(by="Total Goals Conceded", ascending=True)
    .reset_index()
    .rename(columns={"index": "Team"})
)

print("\nTop 10 teams by fewest goals conceded:")
print(best_defensive_teams.head(10).to_string(index=False))


# ============================================================
# 12. RELATIONSHIPS BETWEEN TEAM STATISTICS
# ============================================================

# Each dot represents one team.
ax = team_data.plot(
    kind="scatter",
    x="Total Goals Scored",
    y="Points",
    figsize=(9, 5),
    title="Goals Scored vs League Points",
)

ax.set_xlabel("Total Goals Scored")
ax.set_ylabel("Total Points")

plt.tight_layout()
plt.show()

goals_points_correlation = team_data["Total Goals Scored"].corr(
    team_data["Points"]
)

print("\nCorrelation between goals scored and points:")
print(round(goals_points_correlation, 3))


ax = team_data.plot(
    kind="scatter",
    x="Total Goals Conceded",
    y="Points",
    figsize=(9, 5),
    title="Goals Conceded vs League Points",
)

ax.set_xlabel("Total Goals Conceded")
ax.set_ylabel("Total Points")

plt.tight_layout()
plt.show()

goals_conceded_points_correlation = team_data["Total Goals Conceded"].corr(
    team_data["Points"]
)

print("\nCorrelation between goals conceded and points:")
print(round(goals_conceded_points_correlation, 3))

# Compare correlations among the main performance measures.
correlation_analysis = team_data[
    [
        "Total Goals Scored",
        "Total Goals Conceded",
        "Goal Difference",
        "Points",
    ]
].corr()



import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(9, 6))

sns.heatmap(
    correlation_analysis,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("EPL Team Performance Correlation Heatmap")
plt.tight_layout()
plt.show()



print("\nCorrelation matrix:")
print(correlation_analysis.round(2))


# ============================================================
# 13. ATTACK-TO-DEFENCE RATIO
# ============================================================

# A higher ratio means a team scored more goals relative to the
# number it conceded. This is an exploratory measure, not an
# official league-ranking rule.
team_data["Attack Defence Ratio"] = (
    team_data["Total Goals Scored"]
    / team_data["Total Goals Conceded"]
).round(2)

attack_defence_table = (
    team_data[
        ["Total Goals Scored", "Total Goals Conceded", "Attack Defence Ratio"]
    ]
    .sort_values(by="Attack Defence Ratio", ascending=False)
    .reset_index()
    .rename(columns={"index": "Team"})
)

print("\nTop five teams by attack-to-defence ratio:")
print(attack_defence_table.head(5).to_string(index=False))


# ============================================================
# 14. FINAL DATA VALIDATION
# ============================================================

# The sum of goals scored by all teams must equal the sum of
# goals conceded by all teams. Every goal has a scoring team
# and a conceding team.
total_team_goals_scored = team_data["Total Goals Scored"].sum()
total_team_goals_conceded = team_data["Total Goals Conceded"].sum()

print("\nFinal validation checks:")
print("All teams played 38 matches:", (team_data["TotalMatches"] == 38).all())
print("Team goals scored match dataset total:", total_team_goals_scored == total_goals)
print("Team goals conceded match dataset total:", total_team_goals_conceded == total_goals)
print("Total goals scored equal total goals conceded:",
      total_team_goals_scored == total_team_goals_conceded)
print("Total match outcomes add up to all matches:",
      total_home_wins + total_away_wins + total_draws == total_matches)

print(correlation_analysis["Points"].sort_values(ascending=False))



team_data["Home-Away Win Difference"] = team_data["HomeWins"] - team_data["AwayWins"]
balanced_teams = team_data["Home-Away Win Difference"].abs()
print("\nTeams with the largest home-away win differences:")
print(balanced_teams.sort_values(ascending=True).head(5).to_string())

team_data["Total Wins"] = team_data["HomeWins"] + team_data["AwayWins"]

print(team_data[["HomeWins", "AwayWins", "Total Wins"]].sort_values(
    by="Total Wins", ascending=False
).head(5))

consistent_teams = team_data[["Total Wins","Home-Away Win Difference"]].sort_values(ascending=False)
print("\nTeams with the most consistent performance (total wins):")
print(consistent_teams.head(5).to_string())