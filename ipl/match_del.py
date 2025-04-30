import os
import pandas as pd
import altair as alt
import plotly.express as px
import networkx as nx
from pyvis.network import Network

# Ensure plots are saved to the 'static/plots' directory
PLOT_DIR = "static/plots"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

# Load matches data
# matches = pd.read_csv('D:\DataViz\project\Data_Viz\datasets\matches.csv')
matches = pd.read_csv('../datasets/matches.csv')

# Clean and convert season to integer
# matches['season'] = matches['season'].str.extract('(\d+)')
matches['season'] = matches['season'].str.extract(r'(\d+)')

matches['season'] = matches['season'].astype(int)

# Prepare wins per team per season
team_wins = matches.groupby(['season', 'winner']).size().reset_index(name='wins')
team_wins = team_wins.dropna(subset=['winner'])

# Create slider
season_slider = alt.binding_range(min=team_wins['season'].min(), max=team_wins['season'].max(), step=1)
season_select = alt.param('Season', bind=season_slider, value=team_wins['season'].min())

# Race bar chart
race_chart = alt.Chart(team_wins).transform_filter(
    alt.datum.season == season_select
).mark_bar().encode(
    x=alt.X('wins:Q', title='Number of Wins'),
    y=alt.Y('winner:N', sort='-x', title='Teams'),
    color='winner:N',
    tooltip=['winner:N', 'wins:Q']
).add_params(
    season_select
).properties(
    title='🏆 IPL Team Wins Over Seasons (Race Chart)',
    width=1000,
    height=700
)

# Save the race chart as HTML
race_chart.save(f"{PLOT_DIR}/race_chart.html")

# Load deliveries data
# deliveries = pd.read_csv('D:\DataViz\project\Data_Viz\datasets\deliveries.csv')
deliveries = pd.read_csv('../datasets/deliveries.csv')

# Prepare partnership data
partnerships = deliveries.groupby(['batter', 'non_striker'])['batsman_runs'].sum().reset_index()

# Filter: Only strong partnerships (> 400 runs together)
strong_partnerships = partnerships[partnerships['batsman_runs'] > 400]

# Build Graph
G = nx.Graph()

for index, row in strong_partnerships.iterrows():
    # G.add_edge(row['batter'], row['non_striker'])
    G.add_edge(row['batter'], row['non_striker'], weight=row['batsman_runs']*0.01)

# Create PyVis Network
# net = Network(height="700px", width="100%", bgcolor="transparent", font_color="white")
net = Network(height="500px", width="100%", bgcolor="#1A1A1A", font_color="white")

import json
# Set node background color to transparent or the desired color
options = {
    "nodes": {
        "color": {
            "background": "#1A1A1A",
        }
    }
}
options_json = json.dumps(options)
net.set_options(options_json)

net.from_nx(G)

# Save PyVis Network graph as HTML
net.write_html(f"{PLOT_DIR}/batsman_partnerships.html")

# Bubble chart for batsman stats
batsman_stats = deliveries.groupby('batter').agg(
    runs=('batsman_runs', 'sum'),
    balls=('ball', 'count')
).reset_index()

batsman_stats['strike_rate'] = (batsman_stats['runs'] / batsman_stats['balls']) * 100
batsman_stats = batsman_stats[batsman_stats['balls'] >= 200]  # Only serious players

bubble_chart = alt.Chart(batsman_stats).mark_circle().encode(
    x=alt.X('balls:Q', title='Balls Faced'),
    y=alt.Y('strike_rate:Q', title='Strike Rate'),
    size=alt.Size('runs:Q', scale=alt.Scale(range=[20, 1000])),
    color=alt.Color('batter:N', legend=None),
    tooltip=['batter:N', 'runs:Q', 'balls:Q', 'strike_rate:Q']
).properties(
    title="💥 Batsman Strike Rate vs Balls Faced (Bubble Chart)",
    width=1000,
    height=700
).interactive()

# Save the bubble chart as HTML
bubble_chart.save(f"{PLOT_DIR}/batsman_bubble_chart.html")

# Dismissal types pie chart
dismissals = deliveries['dismissal_kind'].value_counts().reset_index()
dismissals.columns = ['Dismissal Type', 'Count']

dismissal_pie = px.pie(
    dismissals,
    names='Dismissal Type',
    values='Count',
    title='Wicket Dismissal Types in IPL',
    hole=0.4
)

# Save the dismissal pie chart as HTML
dismissal_pie.write_html(f"{PLOT_DIR}/dismissal_pie_chart.html")

# Bowler stats bubble chart
bowler_stats = deliveries.groupby('bowler').agg(
    runs_conceded=('total_runs', 'sum'),
    balls_bowled=('ball', 'count'),
    wickets=('player_dismissed', 'count')
).reset_index()

bowler_stats['overs'] = bowler_stats['balls_bowled'] / 6
bowler_stats['economy'] = bowler_stats['runs_conceded'] / bowler_stats['overs']

# Filter serious bowlers
bowler_stats = bowler_stats[bowler_stats['overs'] >= 100]

bowler_bubble = alt.Chart(bowler_stats).mark_circle().encode(
    x=alt.X('economy:Q', title='Economy Rate'),
    y=alt.Y('wickets:Q', title='Wickets Taken'),
    size=alt.Size('overs:Q', scale=alt.Scale(range=[20, 800])),
    color=alt.Color('bowler:N', legend=None),
    tooltip=['bowler:N', 'economy:Q', 'wickets:Q', 'overs:Q']
).properties(
    title="🎯 Bowler Economy Rate vs Wickets Taken (Bubble Chart)",
    width=1000,
    height=700
).interactive()

# Save the bowler bubble chart as HTML
bowler_bubble.save(f"{PLOT_DIR}/bowler_bubble_chart.html")

# Combine both datasets (matches and deliveries)
combined_df = deliveries.merge(matches, how='left', left_on='match_id', right_on='id')

# Batsman performance in winning matches
batsman_wins = combined_df[combined_df['winner'] == combined_df['batting_team']]
batsman_performance = batsman_wins.groupby('batter')['batsman_runs'].sum().reset_index()

# Top 10 batsmen
top_batsmen = batsman_performance.sort_values(by='batsman_runs', ascending=False).head(10)

# Plot batsman performance
top_batsman_chart = alt.Chart(top_batsmen).mark_bar().encode(
    x=alt.X('batsman_runs:Q', title='Total Runs in Winning Matches'),
    y=alt.Y('batter:N', sort='-x', title='Batsman'),
    color='batter:N',
    tooltip=['batter:N', 'batsman_runs:Q']
).properties(
    title="🏆 Top 10 Batsmen by Runs in Winning Matches",
    width=1000,
    height=700
)

# Save the batsman performance chart as HTML
top_batsman_chart.save(f"{PLOT_DIR}/top_batsmen_performance.html")

# Bowler economy in winning matches
bowler_wins = combined_df[combined_df['winner'] == combined_df['bowling_team']]
bowler_stats = bowler_wins.groupby('bowler').agg(
    total_runs=('total_runs', 'sum'),
    balls_bowled=('ball', 'count')
).reset_index()

bowler_stats['overs'] = bowler_stats['balls_bowled'] / 6
bowler_stats['economy'] = bowler_stats['total_runs'] / bowler_stats['overs']

# Filter for serious bowlers
bowler_stats = bowler_stats[bowler_stats['overs'] >= 30]

# Top 10 best economy
best_economy = bowler_stats.sort_values('economy').head(10)

# Plot best economy bowlers
best_bowler_chart = alt.Chart(best_economy).mark_bar().encode(
    x=alt.X('economy:Q', title='Economy Rate in Wins'),
    y=alt.Y('bowler:N', sort='x', title='Bowler'),
    color='bowler:N',
    tooltip=['bowler:N', 'economy:Q', 'overs:Q']
).properties(
    title="🎯 Top 10 Best Economy Bowlers in Winning Matches",
    width=1000,
    height=700
)

# Save the best bowler economy chart as HTML
best_bowler_chart.save(f"{PLOT_DIR}/best_bowler_economy.html")

# Toss winner decision vs match winner pie chart
combined_df['toss_match_result'] = combined_df.apply(lambda row: 'Won Toss and Match' if row['toss_winner'] == row['winner'] else 'Lost After Toss', axis=1)

toss_outcomes = combined_df[['match_id', 'toss_match_result']].drop_duplicates()

fig = px.pie(toss_outcomes, names='toss_match_result', title='🧠 Toss Impact on Winning Matches')

# Save the toss outcome pie chart as HTML
# fig.write_html(f"{PLOT_DIR}/toss_outcome_pie_chart.html")

# End of script


























# import os
# import pandas as pd
# import altair as alt
# import plotly.express as px
# import networkx as nx
# from pyvis.network import Network

# # Ensure plots are saved to the 'static/plots' directory
# PLOT_DIR = "static/plots"
# if not os.path.exists(PLOT_DIR):
#     os.makedirs(PLOT_DIR)

# # Load matches data
# matches = pd.read_csv('../datasets/matches.csv')

# # Clean and convert season to integer
# matches['season'] = matches['season'].str.extract('(\d+)')
# matches['season'] = matches['season'].astype(int)

# # Prepare wins per team per season
# team_wins = matches.groupby(['season', 'winner']).size().reset_index(name='wins')
# team_wins = team_wins.dropna(subset=['winner'])

# # Create slider
# season_slider = alt.binding_range(min=team_wins['season'].min(), max=team_wins['season'].max(), step=1)
# season_select = alt.param('Season', bind=season_slider, value=team_wins['season'].min())

# # Race bar chart
# race_chart = alt.Chart(team_wins).transform_filter(
#     alt.datum.season == season_select
# ).mark_bar().encode(
#     x=alt.X('wins:Q', title='Number of Wins'),
#     y=alt.Y('winner:N', sort='-x', title='Teams'),
#     color='winner:N',
#     tooltip=['winner:N', 'wins:Q']
# ).add_params(
#     season_select
# ).properties(
#     title='🏆 IPL Team Wins Over Seasons (Race Chart)',
#     width=700,
#     height=400
# )

# # Save the race chart as an image
# import altair_saver
# altair_saver.save(race_chart, f"{PLOT_DIR}/race_chart.png")

# # Load deliveries data
# deliveries = pd.read_csv('datasets/deliveries.csv')

# # Prepare partnership data
# partnerships = deliveries.groupby(['batter', 'non_striker'])['batsman_runs'].sum().reset_index()

# # Filter: Only strong partnerships (> 400 runs together)
# strong_partnerships = partnerships[partnerships['batsman_runs'] > 400]

# # Build Graph
# G = nx.Graph()

# for index, row in strong_partnerships.iterrows():
#     G.add_edge(row['batter'], row['non_striker'], weight=row['batsman_runs'])

# # Create PyVis Network
# net = Network(height="700px", width="100%", bgcolor="#1A1A1A", font_color="white")
# net.from_nx(G)

# # Save manually (safe way)
# net.write_html(f"{PLOT_DIR}/batsman_partnerships.html")

# # Bubble chart for batsman stats
# batsman_stats = deliveries.groupby('batter').agg(
#     runs=('batsman_runs', 'sum'),
#     balls=('ball', 'count')
# ).reset_index()

# batsman_stats['strike_rate'] = (batsman_stats['runs'] / batsman_stats['balls']) * 100
# batsman_stats = batsman_stats[batsman_stats['balls'] >= 200]  # Only serious players

# bubble_chart = alt.Chart(batsman_stats).mark_circle().encode(
#     x=alt.X('balls:Q', title='Balls Faced'),
#     y=alt.Y('strike_rate:Q', title='Strike Rate'),
#     size=alt.Size('runs:Q', scale=alt.Scale(range=[20, 1000])),
#     color=alt.Color('batter:N', legend=None),
#     tooltip=['batter:N', 'runs:Q', 'balls:Q', 'strike_rate:Q']
# ).properties(
#     title="💥 Batsman Strike Rate vs Balls Faced (Bubble Chart)",
#     width=700,
#     height=500
# ).interactive()

# # Save the bubble chart as an image
# altair_saver.save(bubble_chart, f"{PLOT_DIR}/batsman_bubble_chart.png")

# # Dismissal types pie chart
# dismissals = deliveries['dismissal_kind'].value_counts().reset_index()
# dismissals.columns = ['Dismissal Type', 'Count']

# dismissal_pie = px.pie(
#     dismissals,
#     names='Dismissal Type',
#     values='Count',
#     title='Wicket Dismissal Types in IPL',
#     hole=0.4
# )

# # Save the dismissal pie chart as an image
# dismissal_pie.write_image(f"{PLOT_DIR}/dismissal_pie_chart.png")

# # Bowler stats bubble chart
# bowler_stats = deliveries.groupby('bowler').agg(
#     runs_conceded=('total_runs', 'sum'),
#     balls_bowled=('ball', 'count'),
#     wickets=('player_dismissed', 'count')
# ).reset_index()

# bowler_stats['overs'] = bowler_stats['balls_bowled'] / 6
# bowler_stats['economy'] = bowler_stats['runs_conceded'] / bowler_stats['overs']

# # Filter serious bowlers
# bowler_stats = bowler_stats[bowler_stats['overs'] >= 100]

# bowler_bubble = alt.Chart(bowler_stats).mark_circle().encode(
#     x=alt.X('economy:Q', title='Economy Rate'),
#     y=alt.Y('wickets:Q', title='Wickets Taken'),
#     size=alt.Size('overs:Q', scale=alt.Scale(range=[20, 800])),
#     color=alt.Color('bowler:N', legend=None),
#     tooltip=['bowler:N', 'economy:Q', 'wickets:Q', 'overs:Q']
# ).properties(
#     title="🎯 Bowler Economy Rate vs Wickets Taken (Bubble Chart)",
#     width=700,
#     height=500
# ).interactive()

# # Save the bowler bubble chart as an image
# altair_saver.save(bowler_bubble, f"{PLOT_DIR}/bowler_bubble_chart.png")

# # Combine both datasets (matches and deliveries)
# combined_df = deliveries.merge(matches, how='left', left_on='match_id', right_on='id')

# # Batsman performance in winning matches
# batsman_wins = combined_df[combined_df['winner'] == combined_df['batting_team']]
# batsman_performance = batsman_wins.groupby('batter')['batsman_runs'].sum().reset_index()

# # Top 10 batsmen
# top_batsmen = batsman_performance.sort_values(by='batsman_runs', ascending=False).head(10)

# # Plot batsman performance
# top_batsman_chart = alt.Chart(top_batsmen).mark_bar().encode(
#     x=alt.X('batsman_runs:Q', title='Total Runs in Winning Matches'),
#     y=alt.Y('batter:N', sort='-x', title='Batsman'),
#     color='batter:N',
#     tooltip=['batter:N', 'batsman_runs:Q']
# ).properties(
#     title="🏆 Top 10 Batsmen by Runs in Winning Matches",
#     width=600,
#     height=400
# )

# # Save the batsman performance chart as an image
# altair_saver.save(top_batsman_chart, f"{PLOT_DIR}/top_batsmen_performance.png")

# # Bowler economy in winning matches
# bowler_wins = combined_df[combined_df['winner'] == combined_df['bowling_team']]
# bowler_stats = bowler_wins.groupby('bowler').agg(
#     total_runs=('total_runs', 'sum'),
#     balls_bowled=('ball', 'count')
# ).reset_index()

# bowler_stats['overs'] = bowler_stats['balls_bowled'] / 6
# bowler_stats['economy'] = bowler_stats['total_runs'] / bowler_stats['overs']

# # Filter for serious bowlers
# bowler_stats = bowler_stats[bowler_stats['overs'] >= 30]

# # Top 10 best economy
# best_economy = bowler_stats.sort_values('economy').head(10)

# # Plot best economy bowlers
# best_bowler_chart = alt.Chart(best_economy).mark_bar().encode(
#     x=alt.X('economy:Q', title='Economy Rate in Wins'),
#     y=alt.Y('bowler:N', sort='x', title='Bowler'),
#     color='bowler:N',
#     tooltip=['bowler:N', 'economy:Q', 'overs:Q']
# ).properties(
#     title="🎯 Top 10 Best Economy Bowlers in Winning Matches",
#     width=600,
#     height=400
# )

# # Save the best bowler economy chart as an image
# altair_saver.save(best_bowler_chart, f"{PLOT_DIR}/best_bowler_economy.png")

# # Toss winner decision vs match winner pie chart
# combined_df['toss_match_result'] = combined_df.apply(lambda row: 'Won Toss and Match' if row['toss_winner'] == row['winner'] else 'Lost After Toss', axis=1)

# toss_outcomes = combined_df[['match_id', 'toss_match_result']].drop_duplicates()

# fig = px.pie(toss_outcomes, names='toss_match_result', title='🧠 Toss Impact on Winning Matches')

# # Save the toss outcome pie chart as an image
# fig.write_image(f"{PLOT_DIR}/toss_outcome_pie_chart.png")

# # End of script
