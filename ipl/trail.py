import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Ensure plots are saved to the 'static/plots' directory
PLOT_DIR = "static/plots"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

# Setup Selenium WebDriver for headless browsing
options = Options()
options.headless = True

# Initialize the WebDriver with options
driver = webdriver.Chrome(options=options)

# Load auction data
auction = pd.read_csv('../datasets/IPLPlayerAuctionData.csv')

# Clean data
auction = auction.dropna(subset=['Year'])
auction['Year'] = auction['Year'].astype(int)

# ------------------------------
# 1️⃣ Treemap with Plotly
team_spend = auction.groupby('Team', as_index=False)['Amount'].sum()
fig = px.treemap(team_spend, 
                 path=['Team'], 
                 values='Amount',
                 title='Total Auction Spending by Team (2013–2024)',
                 color='Amount', 
                 color_continuous_scale='Blues',
                 hover_data={'Amount': True, 'Team': True})

# Save Plotly figure as HTML
fig.write_html(f"{PLOT_DIR}/treemap.html")

# ------------------------------
# 2️⃣ Sankey Diagram with Plotly
top_auction = auction.sort_values(by='Amount', ascending=False).head(20)
teams = top_auction['Team'].unique().tolist()
players = top_auction['Player'].tolist()
labels = teams + players
sources = [teams.index(team) for team in top_auction['Team']]
targets = [len(teams) + players.index(player) for player in top_auction['Player']]
values = top_auction['Amount'].tolist()

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=30,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values
    )
)])

# Save Sankey figure as HTML
fig.write_html(f"{PLOT_DIR}/sankey_diagram.html")

# ------------------------------
# 3️⃣ Bar Chart with Altair (Team Spending)
highlight = alt.selection_point(on='mouseover', fields=['Team'], nearest=True)
team_spend = auction.groupby('Team', as_index=False)['Amount'].sum()

chart = alt.Chart(team_spend).mark_bar(size=25).encode(
    x=alt.X('Amount:Q', title='Total Amount (INR)'),
    y=alt.Y('Team:N', sort='-x', title='Teams'),
    color=alt.condition(highlight, 'Team:N', alt.value('lightgray')),
    tooltip=[alt.Tooltip('Team:N'), alt.Tooltip('Amount:Q')]
).add_params(
    highlight
).properties(
    title='Auction Spending by Teams (Hover Highlight)',
    width=1000,
    height=700
)

# Save Altair chart as HTML
chart.save(f"{PLOT_DIR}/bar_chart.html")

# ------------------------------
# 4️⃣ Scatterplot with Altair (Player Prices Over Years)
scatter = alt.Chart(auction).mark_circle(size=100).encode(
    x=alt.X('Year:O', title='Auction Year'),
    y=alt.Y('Amount:Q', title='Amount (INR)'),
    color='Team:N',
    tooltip=['Player:N', 'Role:N', 'Amount:Q', 'Team:N', 'Player Origin:N']
).properties(
    width=1000,
    height=700,
    title='Auction Player Prices Over Years (Click and Zoom Supported)'
).interactive()

# Save the scatterplot as HTML
scatter.save(f"{PLOT_DIR}/scatter_plot.html")

# ------------------------------
# 5️⃣ Race Chart with Altair (Top Paid Players Per Year)
race = auction.groupby(['Year', 'Player'], as_index=False)['Amount'].sum()
race = race.sort_values('Amount', ascending=False).groupby('Year').head(10)

year_slider = alt.binding_range(min=race['Year'].min(), max=race['Year'].max(), step=1)
year_select = alt.param(name='YearSelector', bind=year_slider, value=race['Year'].min())

race_chart = alt.Chart(race).transform_filter(
    alt.datum.Year == year_select
).mark_bar().encode(
    x=alt.X('Amount:Q', title='Auction Amount (INR)'),
    y=alt.Y('Player:N', sort='-x', title='Player'),
    color='Player:N',
    tooltip=['Player:N', 'Amount:Q', 'Year:O']
).add_params(
    year_select
).properties(
    width=1000,
    height=700,
    title="Top Paid Players per Year (Interactive Slider)"
)

# Save the race chart as HTML
race_chart.save(f"{PLOT_DIR}/race_chart.html")

# ------------------------------
# End of script

# Quit the WebDriver after capturing the images
driver.quit()



# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import altair as alt
# import altair_saver
# import os

# # Ensure plots are saved to the 'static/plots' directory
# PLOT_DIR = "static/plots"
# if not os.path.exists(PLOT_DIR):
#     os.makedirs(PLOT_DIR)

# # Load auction data
# auction = pd.read_csv('../datasets/IPLPlayerAuctionData.csv')

# # Clean data
# auction = auction.dropna(subset=['Year'])
# auction['Year'] = auction['Year'].astype(int)

# # print(auction)

# # ------------------------------
# 1️⃣ Treemap with Plotly
# team_spend = auction.groupby('Team', as_index=False)['Amount'].sum()
# fig = px.treemap(team_spend, 
#                  path=['Team'], 
#                  values='Amount',
#                  title='Total Auction Spending by Team (2013–2024)',
#                  color='Amount', 
#                  color_continuous_scale='Blues',
#                  hover_data={'Amount': True, 'Team': True})

# # Save the plot as an image file
# fig.write_image(f"{PLOT_DIR}/treemap.png")

# # ------------------------------
# # 2️⃣ Sankey Diagram with Plotly
# top_auction = auction.sort_values(by='Amount', ascending=False).head(20)
# teams = top_auction['Team'].unique().tolist()
# players = top_auction['Player'].tolist()
# labels = teams + players
# sources = [teams.index(team) for team in top_auction['Team']]
# targets = [len(teams) + players.index(player) for player in top_auction['Player']]
# values = top_auction['Amount'].tolist()

# fig = go.Figure(data=[go.Sankey(
#     node=dict(
#         pad=30,
#         thickness=20,
#         line=dict(color="black", width=0.5),
#         label=labels
#     ),
#     link=dict(
#         source=sources,
#         target=targets,
#         value=values
#     )
# )])

# # Save the Sankey diagram as an image
# fig.write_image(f"{PLOT_DIR}/sankey_diagram.png")

# # ------------------------------
# # 3️⃣ Bar Chart with Altair (Team Spending)
# highlight = alt.selection_point(on='mouseover', fields=['Team'], nearest=True)
# team_spend = auction.groupby('Team', as_index=False)['Amount'].sum()

# chart = alt.Chart(team_spend).mark_bar(size=25).encode(
#     x=alt.X('Amount:Q', title='Total Amount (INR)'),
#     y=alt.Y('Team:N', sort='-x', title='Teams'),
#     color=alt.condition(highlight, 'Team:N', alt.value('lightgray')),
#     tooltip=[alt.Tooltip('Team:N'), alt.Tooltip('Amount:Q')]
# ).add_params(
#     highlight
# ).properties(
#     title='Auction Spending by Teams (Hover Highlight)',
#     width=700,
#     height=450
# )

# Save the Altair chart as an image using altair_saver
# altair_saver.save(chart, f"{PLOT_DIR}/bar_chart.png")

# # ------------------------------
# # 4️⃣ Scatterplot with Altair (Player Prices Over Years)
# scatter = alt.Chart(auction).mark_circle(size=100).encode(
#     x=alt.X('Year:O', title='Auction Year'),
#     y=alt.Y('Amount:Q', title='Amount (INR)'),
#     color='Team:N',
#     tooltip=['Player:N', 'Role:N', 'Amount:Q', 'Team:N', 'Player Origin:N']
# ).properties(
#     width=700,
#     height=500,
#     title='Auction Player Prices Over Years (Click and Zoom Supported)'
# ).interactive()

# # Save the scatterplot as an image using altair_saver
# altair_saver.save(scatter, f"{PLOT_DIR}/scatter_plot.png")

# # ------------------------------
# # 5️⃣ Race Chart with Altair (Top Paid Players Per Year)
# race = auction.groupby(['Year', 'Player'], as_index=False)['Amount'].sum()
# race = race.sort_values('Amount', ascending=False).groupby('Year').head(10)

# year_slider = alt.binding_range(min=race['Year'].min(), max=race['Year'].max(), step=1)
# year_select = alt.param(name='YearSelector', bind=year_slider, value=race['Year'].min())

# race_chart = alt.Chart(race).transform_filter(
#     alt.datum.Year == year_select
# ).mark_bar().encode(
#     x=alt.X('Amount:Q', title='Auction Amount (INR)'),
#     y=alt.Y('Player:N', sort='-x', title='Player'),
#     color='Player:N',
#     tooltip=['Player:N', 'Amount:Q', 'Year:O']
# ).add_params(
#     year_select
# ).properties(
#     width=700,
#     height=400,
#     title="Top Paid Players per Year (Interactive Slider)"
# )

# # Save the race chart as an image using altair_saver
# altair_saver.save(race_chart, f"{PLOT_DIR}/race_chart.png")

# # ------------------------------
# # End of script
