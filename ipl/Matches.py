import pandas as pd
import plotly.graph_objects as go
import ipywidgets as widgets
import plotly.io as pio
from IPython.display import display
import plotly.express as px
import math
from plotly.subplots import make_subplots

# Force Plotly to render in Colab
pio.renderers.default = 'colab'

# Load matches datas
matches_df = pd.read_csv('../datasets/matches.csv')
# Load deliveries dataset
deliveries_df = pd.read_csv('../datasets/deliveries.csv')

# Standardize team names
team_mapping = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
    'Rising Pune Supergiant': 'Rising Pune Supergiants',
}
matches_df.replace({'team1': team_mapping, 'team2': team_mapping, 'winner': team_mapping}, inplace=True)

# Total matches played per team per season
team_played = pd.melt(matches_df, id_vars=['season'], value_vars=['team1', 'team2'],
                      var_name='home_away', value_name='team')
team_played = team_played.groupby(['season', 'team']).size().reset_index(name='matches_played')

# Total matches won per team per season
team_wins = matches_df.groupby(['season', 'winner']).size().reset_index(name='matches_won')
team_wins.rename(columns={'winner': 'team'}, inplace=True)

# Merge and calculate win ratio
win_ratio = pd.merge(team_played, team_wins, on=['season', 'team'], how='left')
win_ratio['matches_won'] = win_ratio['matches_won'].fillna(0)
win_ratio['win_ratio'] = (win_ratio['matches_won'] / win_ratio['matches_played']).round(2)

# Use win_ratio DataFrame (assumed already computed)
teams = sorted(win_ratio['team'].unique())

# Clean season labels
win_ratio['season_clean'] = win_ratio['season'].str.extract(r'(\d{4})').astype(int)

# Build one trace per team — all hidden except default
fig = go.Figure()

for team in teams:
    team_data = win_ratio[win_ratio['team'] == team]
    fig.add_trace(go.Scatter(
        x=team_data['season_clean'],
        y=team_data['win_ratio'],
        mode='lines+markers',
        name=team,
        visible=(team == 'Mumbai Indians'),
        line=dict(width=4),
        marker=dict(size=8),
        hovertemplate='Season: %{x}<br>Win Ratio: %{y:.0%}<extra></extra>'
    ))

# Build dropdown buttons for team toggle
dropdown_buttons = [
    dict(label=team,
         method='update',
         args=[{'visible': [t == team for t in teams]},
               {'title': f'🏆 Win Ratio by Season: {team}'}])
    for team in teams
]

# Update layout with embedded dropdown
fig.update_layout(
    updatemenus=[dict(
        buttons=dropdown_buttons,
        direction="down",
        showactive=True,
        x=1.15,
        xanchor="left",
        y=1,
        yanchor="top",
        font=dict(size=8),
        pad=dict(r=0, t=0), 
    )],
    title="🏆 Win Ratio by Season: Mumbai Indians",
    xaxis_title="Season",
    yaxis_title="Win Ratio",
    yaxis=dict(tickformat=".0%", range=[0, 1]),
    xaxis=dict(type='category', tickangle=-45),
    font=dict(size=15),
    height=500,
    width=800
)

# Save the first plot as HTML
fig.write_html("static/game_plots/win_ratio_by_season_mumbai_indians.html")

# Total matches played per team
team_played_total = pd.melt(matches_df, value_vars=['team1', 'team2'], value_name='team')
team_played_total = team_played_total.groupby('team').size().reset_index(name='total_matches')

# Total matches won
team_wins_total = matches_df.groupby('winner').size().reset_index(name='total_wins')
team_wins_total.rename(columns={'winner': 'team'}, inplace=True)

# Trophies (title wins) – Only final match winners
finals = matches_df.dropna(subset=['season'])  # just in case
final_match_per_season = finals.groupby('season').apply(lambda x: x.iloc[-1]).reset_index(drop=True)
trophies = final_match_per_season['winner'].value_counts().reset_index()
trophies.columns = ['team', 'trophies']

# Merge all
win_summary = pd.merge(team_played_total, team_wins_total, on='team', how='left')
win_summary = pd.merge(win_summary, trophies, on='team', how='left')
win_summary.fillna(0, inplace=True)

# Calculate win %
win_summary['win_pct'] = (win_summary['total_wins'] / win_summary['total_matches'] * 100).round(2)

# Filter and sort
filtered = win_summary[win_summary['total_matches'] >= 50].copy()
filtered = filtered.sort_values(by='trophies', ascending=False).reset_index(drop=True)

# Grid setup
cols = 3
rows = math.ceil(len(filtered) / cols)

fig = make_subplots(
    rows=rows, cols=cols,
    specs=[[{"type": "indicator"}]*cols for _ in range(rows)]
)

# Add one gauge per team
for idx, row in filtered.iterrows():
    r = (idx // cols) + 1
    c = (idx % cols) + 1

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=row['win_pct'],
        number={'suffix': f"%\n🏆 {int(row['trophies'])}", 'font': {'size': 20}},
        title={'text': row['team'], 'font': {'size': 18}},  # Bigger team name
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': 'deepskyblue'},
               'bgcolor': 'lightgray',
               'steps': [{'range': [0, 50], 'color': "#ffcccc"},
                         {'range': [50, 75], 'color': "#ffe066"},
                         {'range': [75, 100], 'color': "#b7f0ad"}]},
        domain={'row': r-1, 'column': c-1}
    ), row=r, col=c)

# Layout polish
fig.update_layout(
    title_text="IPL Legacy Dashboard: Win Percentage & Trophies of Teams",
    height=230 * rows,
    width=800,
    font=dict(size=8),
    margin=dict(t=100),
    title_font=dict(size=24)
)

# Save the second plot (Win Percentage & Trophies) as HTML
fig.write_html("static/game_plots/ipl_legacy_dashboard_win_percentage_trophies.html")



toss_won = matches_df['toss_winner'].value_counts().reset_index()
toss_won.columns = ['team', 'toss_wins']

toss_match_win = matches_df[matches_df['toss_winner'] == matches_df['winner']]['toss_winner'].value_counts().reset_index()
toss_match_win.columns = ['team', 'toss_and_match_wins']

# Toss-to-Match Conversion Breakdown
df = pd.merge(toss_won, toss_match_win, on='team', how='left').fillna(0)
df['toss_and_match_losses'] = df['toss_wins'] - df['toss_and_match_wins']
df = df.sort_values(by='toss_wins', ascending=False).reset_index(drop=True)

# Stacked bar chart
fig = go.Figure()

# Bar: Toss → Match Wins
fig.add_trace(go.Bar(
    x=df['team'],
    y=df['toss_and_match_wins'],
    name='Toss → Match Wins',
    marker_color='#80dfff',
    text=df['toss_and_match_wins'],
    textposition='outside',
    hovertemplate='Toss Wins Converted: %{y}<br>Team: %{x}<extra></extra>'
))

# Bar: Toss → Match Losses
fig.add_trace(go.Bar(
    x=df['team'],
    y=df['toss_and_match_losses'],
    name='Toss → Match Losses',
    marker_color='#1e3f66',
    text=df['toss_and_match_losses'],
    textposition='outside',
    hovertemplate='Toss Wins Not Converted: %{y}<br>Team: %{x}<extra></extra>'
))

# Layout beautification
fig.update_layout(
    barmode='stack',
    title='Toss-to-Match Conversion Breakdown',
    xaxis=dict(title='Team', tickangle=-40, tickfont=dict(size=12)),
    yaxis=dict(title='Total Toss Wins', gridcolor='lightgray'),
    font=dict(family='Arial', size=14),
    height=450,
    width=900,
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(x=1.02, y=1, bgcolor='rgba(255,255,255,0)', bordercolor='gray'),
    margin=dict(t=80, b=100)
)

# Save the third plot (Toss-to-Match Conversion) as HTML
fig.write_html("static/game_plots/toss_to_match_conversion_breakdown.html")

# Stadiums map plot


# Standardize team names
team_mapping = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
    'Rising Pune Supergiant': 'Rising Pune Supergiants',
}
matches_df.replace({'team1': team_mapping, 'team2': team_mapping, 'winner': team_mapping}, inplace=True)

# Merge venue into deliveries
merged_df = deliveries_df.merge(matches_df[['id', 'venue']], left_on='match_id', right_on='id')

# Total runs scored per venue
venue_runs = merged_df.groupby('venue')['total_runs'].sum().reset_index()

# Matches played per venue
venue_matches = matches_df['venue'].value_counts().reset_index()
venue_matches.columns = ['venue', 'matches_played']

# Combine run + match data
venue_stats = pd.merge(venue_runs, venue_matches, on='venue')
venue_stats['avg_runs_per_match'] = (venue_stats['total_runs'] / venue_stats['matches_played']).round(2)

# Manually assign coordinates (expand this as needed)
stadium_coords = {
    'Wankhede Stadium': (18.9388, 72.8258),
    'M. Chinnaswamy Stadium': (12.9788, 77.5996),
    'Eden Gardens': (22.5646, 88.3433),
    'Narendra Modi Stadium': (23.0918, 72.5977),
    'Arun Jaitley Stadium': (28.6229, 77.2430),
    'Rajiv Gandhi Intl. Stadium': (17.4062, 78.5506),
    'MA Chidambaram Stadium': (13.0624, 80.2791),
    'Sawai Mansingh Stadium': (26.8945, 75.8039),
    'Himachal Pradesh Cricket Association Stadium': (32.1976, 76.3254),
    'Dr DY Patil Sports Academy': (19.0330, 73.0297),
    'Punjab Cricket Association Stadium': (30.7036, 76.7183),
    'Green Park': (26.4725, 80.3467),
    'Sheikh Zayed Stadium': (24.4672, 54.3717),
    'Sharjah Cricket Stadium': (25.3187, 55.4211),
    'Dubai International Cricket Stadium': (25.0458, 55.2319)
}

# Map coordinates to venue_stats
venue_stats['lat'] = venue_stats['venue'].map(lambda x: stadium_coords.get(x, (None, None))[0])
venue_stats['lon'] = venue_stats['venue'].map(lambda x: stadium_coords.get(x, (None, None))[1])

# Filter out venues with missing coords
venue_stats = venue_stats.dropna(subset=['lat', 'lon'])

fig = px.scatter_mapbox(
    venue_stats,
    lat='lat',
    lon='lon',
    hover_name='venue',
    hover_data={'total_runs': True, 'matches_played': True, 'avg_runs_per_match': True},
    size='total_runs',
    color='avg_runs_per_match',
    color_continuous_scale='Plasma',
    size_max=40,
    zoom=3.5,
    height=600,
    title='📍 All IPL Stadiums — Total Runs & Avg Runs per Match',
)

fig.update_layout(
    mapbox_style='carto-positron',
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    font=dict(size=14)
)

# Save the map plot as HTML
fig.write_html("static/game_plots/ipl_stadiums_map.html")
