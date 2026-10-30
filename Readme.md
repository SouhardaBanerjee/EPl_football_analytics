# ⚽ Premier League 2024–25 Analytics Dashboard

An interactive football analytics dashboard built using Python, Pandas, Matplotlib and Streamlit to explore team performance, league standings, attacking and defensive statistics, and home advantage in the English Premier League 2024–25 season.

## Project Overview

This project analyzes the complete 2024–25 Premier League season using match-level football data.

The objective is to transform raw football match data into meaningful statistical insights through data cleaning, exploratory data analysis, visualization and an interactive dashboard.

## Dashboard Features

- **Season Overview:** Total matches, participating teams, total goals and average goals per match.
- **League Standings:** Automatically calculated league table with points, wins, draws, losses and goal difference.
- **Team Performance Centre:** Interactive club selection with detailed performance statistics.
- **Attacking Analysis:** Comparison of the top 10 goal-scoring teams.
- **Defensive Analysis:** Identification of the teams that conceded the fewest goals.
- **Home vs Away Analysis:** Investigation of home advantage and match outcomes.
- **Attack vs Points:** Relationship between goals scored and league points.
- **Defence vs Points:** Relationship between goals conceded and league points.
- **Goal Distribution:** Analysis of the number of goals scored in individual matches.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Pandas | Data manipulation and analysis |
| Matplotlib | Data visualization |
| Streamlit | Interactive dashboard |
| Git | Version control |
| GitHub | Project hosting |

## Project Structure

```text
epl-football-analysis/
│
├── app.py
├── explore_data.py
├── E0.csv
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/SouhardaBanerjee/EPL_football_analytics.git
```

### 2. Navigate into the project

```bash
cd EPL_football_analytics
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the dashboard

```bash
python -m streamlit run app.py
```

The dashboard will open in your browser.

## Dataset

The project uses Premier League 2024–25 match data from:

[Football-Data.co.uk](https://www.football-data.co.uk/)

The dataset contains match results, goals scored, goals conceded and other match-related information.

Dataset attribution: Football-Data.co.uk.

Please consult the provider's usage terms before redistributing or reusing the raw dataset.

## Key Analytical Areas

The project investigates questions such as:

- Do teams score more goals at home?
- Which teams have the strongest attacks?
- Which teams have the strongest defences?
- Is scoring more goals associated with earning more points?
- How does defensive performance relate to league position?
- What is the distribution of goals across Premier League matches?

## Future Improvements

- Add team crests and club branding.
- Add advanced football performance metrics.
- Introduce filters for match dates and opponents.
- Add expected goals (xG) analysis if suitable data becomes available.
- Improve interactive visualizations.
- Expand analysis to multiple Premier League seasons.

## Author

**Souharda Banerjee**

GitHub: [SouhardaBanerjee](https://github.com/SouhardaBanerjee)

---

*Built as a Python data analytics portfolio project.*