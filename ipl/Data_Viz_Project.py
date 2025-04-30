import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import bar_chart_race as bcr
import os

# Create directory for saving plots
PLOT_DIR = "static/auction_plots/"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

auction_df = pd.read_csv('../datasets/IPLPlayerAuctionData.csv')
matches_df = pd.read_csv('../datasets/matches.csv')
deliveries_df = pd.read_csv('../datasets/deliveries.csv')

#team spending over the years
auction_df['Year'] = pd.to_datetime(auction_df['Year'], format='%Y').dt.year
team_spending = auction_df.groupby(['Year', 'Team'])['Amount'].sum().reset_index()

fig = px.line(team_spending, x='Year', y='Amount', color='Team',
                 title='Team Spending Over the Years')
fig.write_html("static/auction_plots/team_spending_over_years.html") 


# Spending on bowlers vs batsmen over the years
bowlers_df = auction_df[auction_df['Role'] == 'Bowler']
batsmen_df = auction_df[auction_df['Role'] == 'Batsman']
bowlers_spending = bowlers_df.groupby('Year')['Amount'].sum().reset_index()
batsmen_spending = batsmen_df.groupby('Year')['Amount'].sum().reset_index()

fig = go.Figure()

fig.add_trace(go.Scatter(x=bowlers_spending['Year'], y=bowlers_spending['Amount'],
                         mode='lines', name='Bowlers'))
fig.add_trace(go.Scatter(x=batsmen_spending['Year'], y=batsmen_spending['Amount'],
                         mode='lines', name='Batsmen'))

fig.update_layout(title='Spending on Bowlers vs. Batsmen Over the Years',
                  xaxis_title='Year',
                  yaxis_title='Total Spending')
fig.write_html("static/auction_plots/spending_on_bowlers_vs_batsmen.html")


# Streamgraph of Amount by Role over Years
grouped = auction_df.groupby(['Year', 'Role'])['Amount'].sum().reset_index()

chart = alt.Chart(grouped).mark_area(
    interpolate='basis' 
).encode(
    x='Year:O',
    y='Amount:Q',
    color='Role:N'
).properties(
    width=700,
    height=400,
    title='Streamgraph of Amount by Role over Years'
)

chart.save("static/auction_plots/streamgraph_amount_by_role_over_years.html") 


# Value of players over the years
player_year = (
    auction_df
    .groupby(['Player', 'Year'])['Amount']
    .sum()
    .reset_index()
)
player_year = player_year.sort_values(by=['Player', 'Year'])

player_year['Amount_Diff'] = player_year.groupby('Player')['Amount'].diff()
player_year['Amount_Pct_Change'] = player_year.groupby('Player')['Amount'].pct_change()


wildest_rise = player_year.sort_values('Amount_Pct_Change', ascending=False).head(10)
wildest_crash = player_year.sort_values('Amount_Pct_Change').head(10)

target_player = wildest_rise.iloc[3]['Player']

player_data = player_year[player_year['Player'] == target_player]

fig = px.line(
    player_data,
    x='Year',
    y='Amount',
    markers=True,
    title=f'Valuation Over Years: {target_player}',
    labels={'Amount': 'Auction Amount'}
)
fig.write_html(f"static/auction_plots/{target_player}_valuation_over_years.html") 


#Rocket chart for multiple players
player_with_diff = player_year.dropna(subset=['Amount_Diff'])

rockets = player_with_diff.sort_values('Amount_Diff', ascending=False).head(5)
crashes = player_with_diff.sort_values('Amount_Diff', ascending=True).head(5)

player_list_rocket = rockets['Player'].tolist()
player_list_crashes = rockets['Player'].tolist()

fig = px.line(
    player_year[player_year['Player'].isin(player_list_rocket)],
    x='Year',
    y='Amount',
    color='Player',
    markers=True,
    line_shape='spline',
    title= "Top 5 Player Valuation Rockets",
    labels={'Amount': 'Auction Amount (₹)'}
)
fig.update_traces(mode="lines+markers+text", textposition="top right")
fig.update_layout(
    title_font_size=24,
    font=dict(size=14),
    legend_title_text='Player',
    hovermode='x unified',
    height=600,
    width=900
)
fig.write_html("static/auction_plots/top_5_player_rockets.html")    

# Player crashes for multiple players
fig = px.line(
    player_year[player_year['Player'].isin(player_list_crashes)],
    x='Year',
    y='Amount',
    color='Player',
    markers=True,
    line_shape='spline',
    title= "Top 5 Player Valuation Crashes",
    labels={'Amount': 'Auction Amount (₹)'}
)
fig.update_traces(mode="lines+markers+text", textposition="top right")
fig.update_layout(
    title_font_size=24,
    font=dict(size=14),
    legend_title_text='Player',
    hovermode='x unified',
    height=600,
    width=900
)
fig.write_html("static/auction_plots/top_5_player_crashes.html")    

#smootherd ricket

player_year_team = (
    auction_df
    .sort_values('Amount', ascending=False)
    .groupby(['Player', 'Year'])
    .first()
    .reset_index()
)

# Now player_year_team has Player, Year, Amount, Team

# Sort properly
player_year_team = player_year_team.sort_values(by=['Player', 'Year'])

df_rocket = player_year_team[player_year_team['Player'].isin(player_list_rocket)]
df_crashes = player_year_team[player_year_team['Player'].isin(player_list_crashes)]

fig = go.Figure()

for player in player_list_rocket:
    player_df = df_rocket[df_rocket['Player'] == player]
    fig.add_trace(go.Scatter(
        x=player_df['Year'],
        y=player_df['Amount'],
        mode='lines+markers',
        name=player,
        hovertemplate=(
            'Player: %{text}<br>'
            'Year: %{x}<br>'
            'Amount: ₹%{y}<br>'
            'Team: %{customdata}'
        ),
        text=[player]*len(player_df),
        customdata=player_df['Team'],
        line=dict(width=3, shape='spline'),  
        marker=dict(size=8)
    ))

fig.update_layout(
    title='Top 5 Rockets (Smoothed)',
    height=600,
    width=950,
    font=dict(size=14),
    hovermode='closest',  
    legend_title_text='Player'
)
fig.write_html("static/auction_plots/top_5_player_rockets_smoothed.html")


#crashes smoothed
fig = go.Figure()

for player in player_list_crashes:
    player_df = df_crashes[df_crashes['Player'] == player]
    fig.add_trace(go.Scatter(
        x=player_df['Year'],
        y=player_df['Amount'],
        mode='lines+markers',
        name=player,
        hovertemplate=(
            'Player: %{text}<br>'
            'Year: %{x}<br>'
            'Amount: ₹%{y}<br>'
            'Team: %{customdata}'
        ),
        text=[player]*len(player_df),
        customdata=player_df['Team'],
        line=dict(width=3, shape='spline'),  
        marker=dict(size=8)
    ))

fig.update_layout(
    title='Top 5 Crashes (Smoothed)',
    height=600,
    width=950,
    font=dict(size=14),
    hovermode='closest',  
    legend_title_text='Player'
)
fig.write_html("static/auction_plots/top_5_player_crashes_smoothed.html")



#Pat Cummings chart

def clean_season(season):
    if isinstance(season, str) and '/' in season:
        return int(season.split('/')[0])
    return int(season)

matches_df['season'] = matches_df['season'].apply(clean_season)

# Merge to get season info
deliveries = deliveries_df.merge(matches_df[['id', 'season']], left_on='match_id', right_on='id', how='left')

# Batting stats
cummins_batting = deliveries[deliveries['batter'] == 'PJ Cummins']
batting_stats = cummins_batting.groupby('season').agg(
    runs_scored=('batsman_runs', 'sum'),
    balls_faced=('ball', 'count')
).reset_index()
batting_stats['strike_rate'] = (batting_stats['runs_scored'] / batting_stats['balls_faced']) * 100

# Bowling stats
cummins_bowling = deliveries[deliveries['bowler'] == 'PJ Cummins']
bowling_stats = cummins_bowling.groupby('season').agg(
    balls_bowled=('ball', 'count'),
    runs_conceded=('total_runs', 'sum'),
    wickets=('is_wicket', 'sum')
).reset_index()
bowling_stats['overs'] = bowling_stats['balls_bowled'] // 6 + (bowling_stats['balls_bowled'] % 6) / 10
bowling_stats['economy_rate'] = bowling_stats['runs_conceded'] / (bowling_stats['balls_bowled'] / 6)

import plotly.graph_objects as go

# Create a single-row subplot figure for bowling only
fig = go.Figure()

# Add Wickets (Bar)
fig.add_trace(go.Bar(
    x=bowling_stats['season'],
    y=bowling_stats['wickets'],
    name="Wickets",
    marker_color='blue'
))

# Add Economy Rate (Line)
fig.add_trace(go.Scatter(
    x=bowling_stats['season'],
    y=bowling_stats['economy_rate'],
    name="Economy Rate",
    yaxis="y2",
    marker_color='red',
    mode='lines+markers'
))

# Layout adjustments
fig.update_layout(
    height=500,
    title_text="PJ Cummins' Bowling Performance Over the Years",
    yaxis=dict(title='Wickets'),
    yaxis2=dict(
        overlaying='y',
        side='right',
        title='Economy Rate'
    ),
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)
fig.write_html("static/auction_plots/pj_cummins_bowling_performance.html")


#########################################################################################################################################


# # Team spending over the years
# team_spending = auction_df.groupby(['Year', 'Team'])['Amount'].sum().reset_index()
# fig = px.line(team_spending, x='Year', y='Amount', color='Team', title='Team Spending Over the Years')
# fig.write_html(f"{PLOT_DIR}/team_spending_over_years.html")

# # Spending on bowlers vs batsmen over the years
# bowlers_spending = bowlers_df.groupby('Year')['Amount'].sum().reset_index()
# batsmen_spending = batsmen_df.groupby('Year')['Amount'].sum().reset_index()
# fig = go.Figure()
# fig.add_trace(go.Scatter(x=bowlers_spending['Year'], y=bowlers_spending['Amount'],
#                          mode='lines', name='Bowlers'))
# fig.add_trace(go.Scatter(x=batsmen_spending['Year'], y=batsmen_spending['Amount'],
#                          mode='lines', name='Batsmen'))
# fig.update_layout(title='Spending on Bowlers vs. Batsmen Over the Years',
#                   xaxis_title='Year',
#                   yaxis_title='Total Spending')
# fig.write_html(f"{PLOT_DIR}/spending_on_bowlers_vs_batsmen.html")

# # Streamgraph of Amount by Role over Years
# grouped = auction_df.groupby(['Year', 'Role'])['Amount'].sum().reset_index()
# chart = alt.Chart(grouped).mark_area(interpolate='basis').encode(
#     x='Year:O',
#     y='Amount:Q',
#     color='Role:N'
# ).properties(width=1000, height=600, title='Streamgraph of Amount by Role over Years')
# chart.save(f"{PLOT_DIR}/streamgraph_amount_by_role_over_years.html")

# team_race = (
#     auction_df
#     .groupby(['Year', 'Team'])['Amount']
#     .sum()
#     .reset_index()
# )
# # Bar chart race for top spending teams
# pivot_team = team_race.pivot(index='Year', columns='Team', values='Amount').fillna(0)
# bcr.bar_chart_race(
#     df=pivot_team,
#     filename=f"{PLOT_DIR}/top_spending_teams_race.html",
#     n_bars=4,
#     steps_per_period=40,
#     period_length=2000,
#     title='Top 4 Spending Teams by Year',
#     bar_size=.90,
#     figsize=(6, 4),
#     interpolate_period=True,
#     period_label={'x': .95, 'y': .25, 'ha': 'right', 'va': 'center'},
#     cmap='bold',
#     fixed_order=False,
#     fixed_max=True,
#     filter_column_colors=True,
# )

# # Player valuation rockets
# fig = px.line(player_data, x='Year', y='Amount', markers=True, title=f'Valuation Over Years: {target_player}')
# fig.write_html(f"static/auction_plots/{target_player}_valuation_over_years.html")

# # Player valuation rockets & crashes for multiple players
# fig = go.Figure()
# for player in player_list:
#     player_df = df[df['Player'] == player]
#     fig.add_trace(go.Scatter(x=player_df['Year'], y=player_df['Amount'], mode='lines+markers', name=player))
# fig.update_layout(title=title, height=600, width=950, font=dict(size=14), hovermode='closest', legend_title_text='Player')
# fig.write_html(f"static/auction_plots/{title.replace(' ', '_')}_player_trends.html")

