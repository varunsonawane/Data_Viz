import pandas as pd
import plotly.express as px

# Read and preprocess data
fow_df = pd.read_csv("../datasets/ipl_fow_card.csv")
historical_df = pd.read_csv("../datasets/ipl_historical.csv")

fow_df = fow_df.rename(columns={"overs": "over_number", "team": "batting_team"})
fow_df = fow_df.dropna(subset=["over_number"])
fow_df["over_number"] = fow_df["over_number"].astype(int)
fow_df = fow_df[(fow_df["over_number"] >= 1) & (fow_df["over_number"] <= 20)]

# Prepare data for plot
teams = fow_df["batting_team"].unique()
all_overs = list(range(1, 21))
all_combinations = pd.MultiIndex.from_product([teams, all_overs], names=["batting_team", "over_number"])
base_df = pd.DataFrame(index=all_combinations).reset_index()

wickets_actual = fow_df.groupby(["batting_team", "over_number"]).size().reset_index(name="wicket_count")
wickets_by_team_over = pd.merge(base_df, wickets_actual, on=["batting_team", "over_number"], how="left").fillna(0)
wickets_by_team_over["wicket_count"] = wickets_by_team_over["wicket_count"].astype(int)

# Create a bar chart for the first team
fig = px.bar(
    wickets_by_team_over[wickets_by_team_over["batting_team"] == teams[0]],
    x="over_number",
    y="wicket_count",
    title=f"Wickets Fallen by Over - {teams[0]}",
    labels={"over_number": "Over", "wicket_count": "Wickets Fallen"},
)

# Add dropdown for selecting different teams
fig.update_layout(
    updatemenus=[{
        "buttons": [
            {
                "label": team,
                "method": "update",
                "args": [
                    {
                        "x": [wickets_by_team_over[wickets_by_team_over["batting_team"] == team]["over_number"]],
                        "y": [wickets_by_team_over[wickets_by_team_over["batting_team"] == team]["wicket_count"]],
                        "type": "bar"
                    },
                    {"title": f"Wickets Fallen by Over - {team}"}
                ],
            } for team in teams
        ],
        "direction": "down",
        "showactive": True,
    }]
)

# Save the updated figure with dropdown as HTML
fig.write_html("static/player_plots/wickets_fallen_by_over.html")

# Historical data processing

match_results = historical_df[['match_id', 'team1_name', 'team2_name', 'toss_winner',
                               'toss_winner_choice', 'match_winner']].dropna(subset=['match_winner'])

def get_batting_first(row):
    if row['toss_winner_choice'] == 'bat':
        return row['toss_winner']
    else:
        return row['team2_name'] if row['toss_winner'] == row['team1_name'] else row['team1_name']

match_results['batting_first'] = match_results.apply(get_batting_first, axis=1)

match_results['win_type'] = match_results.apply(
    lambda row: 'Defended' if row['match_winner'] == row['batting_first'] else 'Chased',
    axis=1
)

team_win_type = match_results.groupby(['match_winner', 'win_type']).size().reset_index(name='count')
team_win_type = team_win_type.rename(columns={'match_winner': 'Team'})

team_totals = team_win_type.groupby('Team')['count'].sum().reset_index(name='total_wins')
team_win_type = team_win_type.merge(team_totals, on='Team')

team_win_type['percent'] = round((team_win_type['count'] / team_win_type['total_wins']) * 100, 1)

# Create a bar chart for Chasing vs. Defending success rate by team
fig = px.bar(
    team_win_type,
    x='Team',
    y='count',
    color='win_type',
    barmode='group',
    title='Chasing vs. Defending Success Rate by Team',
    labels={'count': 'Matches Won', 'win_type': 'Victory Type'},
    custom_data=['win_type', 'percent']
)

fig.update_traces(
    hovertemplate='<b>%{x}</b><br>Victory Type=%{customdata[0]}<br>Matches Won=%{y}<br>Percent=%{customdata[1]}%'
)

fig.update_layout(
    xaxis={'categoryorder': 'total descending'},
    legend_title_text='Victory Type'
)

# Save the Chasing vs. Defending chart as HTML
fig.write_html("static/player_plots/chasing_vs_defending_success_rate_by_team.html")
