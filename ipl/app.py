from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Path to the folder where HTML plot files are saved
PLOT_DIR = "static/plots"

@app.route('/')
def index():
    # List all HTML files in the plot directory
    plot_files = [f for f in os.listdir(PLOT_DIR) if f.endswith('.html')]

    # If no plot files are available
    if not plot_files:
        return "No plots found. Please generate them first."

    return render_template('index.html', plot_files=plot_files)

@app.route('/plots/<filename>')
def plot(filename):
    # Serve plot HTML files
    return send_from_directory(PLOT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)






















# from flask import Flask, render_template, send_from_directory
# import os

# app = Flask(__name__)

# # Path to the folder where plot images are saved
# PLOT_DIR = "static/plots"

# @app.route('/')
# def index():
#     # List all files in the plot directory
#     plot_files = os.listdir(PLOT_DIR)

#     # Make sure that plot files are available
#     if not plot_files:
#         return "No plots found. Please ensure the plots are generated."

#     return render_template('index.html', plot_files=plot_files)

# @app.route('/plots/<filename>')
# def plot(filename):
#     # Serve plot images from the 'static/plots' folder
#     return send_from_directory(PLOT_DIR, filename)

# if __name__ == '__main__':
#     app.run(debug=True)
