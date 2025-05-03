
# 🏏 Indian Data Premier League – IPL Data Visualization (2008–2023)

## 📌 Overview

This project is an interactive web-based data visualization dashboard that explores key facets of the Indian Premier League (IPL) from 2008 to 2023. Focused on **exploratory data analysis (EDA)** rather than prediction or machine learning, it provides insights into:

- 🧾 Auction strategies and spending patterns  
- 🏟️ Match outcomes and season dynamics  
- 🧑‍💼 Player performance trends and roles

All visuals are built using Python libraries: **Plotly**, **Matplotlib**, **Seaborn**, and **Altair**.

---

## 🛠️ How to Run Locally

1. Open a terminal in the project directory.
2. Run a local server:

```bash
python -m http.server 8000
```

3. Open the following URL in your browser:

```
http://localhost:8000/src/html/index.html
```

---

## 🧠 Abstract

This project presents a comprehensive and interactive platform to analyze and interpret IPL data spanning from 2008 to 2023. By leveraging pre-cleaned datasets, it emphasizes descriptive statistics and visual storytelling over predictive modeling.

We use a combination of:
- **Plotly** for interactivity
- **Seaborn** and **Matplotlib** for detailed statistical visuals
- **Altair** for clean, declarative plots

The dashboard is split into three sections:
1. **Auction Analytics**
2. **Game Analysis**
3. **Team Performance**

Each section includes dynamic charts and annotated insights to explore the IPL from multiple analytical lenses. The goal is to reveal relationships such as:
- Correlation between spending and performance  
- Venue-specific win biases  
- Evolving trends in player performance

---

## 📚 Introduction

The Indian Premier League (IPL) combines high-performance cricket with strategic financial planning. With data spanning auctions, match outcomes, and individual metrics, it provides a high-dimensional playground for data analysis.

### 🎯 Objectives:
- Build a centralized, interactive platform for IPL data visualization.
- Empower both technical and non-technical users to extract insights.
- Practice advanced visualization techniques learned in the Data Visualization course.

### 🔍 Analytical Focus Areas:
1. **Auction Analytics** – Exploring financial trends and player buys across seasons.
2. **Match Analysis** – Understanding the influence of toss, venue, and match conditions.
3. **Player Insights** – Highlighting batting and bowling trends, anomalies, and role changes.

The narrative follows the IPL season’s flow:  
**Auction Table → Match Field → Individual Brilliance**

---

## 📁 Project Structure

```
src/
├── html/
│   └── index.html      # Main entry point for the dashboard
datasets/
├── ...                 # Pre-cleaned IPL CSV datasets
visualizations/
├── ...                 # Jupyter notebooks and plot scripts
```

---

## 👨‍💻 Technologies Used

- Python (Jupyter, Pandas, Plotly, Seaborn, Matplotlib, Altair)
- HTML/CSS for dashboard layout
- GitHub Pages for static site hosting
