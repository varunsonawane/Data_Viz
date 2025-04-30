# import plotly.graph_objects as go
# import plotly.express as px
# import kaleido

# # Test if Plotly can generate and save an image
# fig = px.scatter(x=[1, 2, 3], y=[4, 5, 6], title="Test Plot")
# # fig.write_image("test_plot.png")
# fig.write_image("test_plot.jpg", engine="kaleido")

# # fig.show()


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import plotly.express as px

# Set up Selenium for headless browser
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# # Generate Plotly plot
# fig = px.scatter(x=[1, 2, 3], y=[4, 5, 6], title="Test Plot")

# # Show the plot in the browser
# fig.write_html('plot.html')


import altair as alt
import pandas as pd

# Sample data
data = pd.DataFrame({
    'Fruit': ['Apples', 'Bananas', 'Oranges', 'Grapes'],
    'Sales': [100, 150, 80, 120]
})

# Create the chart
chart = alt.Chart(data).mark_bar().encode(
    x='Fruit',
    y='Sales'
)

# chart
chart.save('plot.html')

# Capture a screenshot of the plot using Selenium
driver.get("file:///D:/DataViz/plot.html")  # Replace with the correct path to plot.html
driver.save_screenshot("plot_screenshot.png")
driver.quit()
