# NBA Analytics Dashboard

An interactive data analysis dashboard built with Python and Streamlit, covering NBA statistics from 1947 to 2026. Developed as an academic project.

![NBA Analytics Dashboard]
<img width="1568" height="669" alt="image" src="https://github.com/user-attachments/assets/429cabae-3587-46f8-9191-8c57fad59214" />

---

## Overview

This project explores nearly 80 years of professional basketball data through statistical analysis, feature engineering, and an interactive multi-page dashboard. The goal is to make historical NBA data accessible and interpretable — for analysts, fans, and anyone curious about how the game has evolved.

The work is divided into two parts:

- **Part I — Exploratory Analysis**: dataset description, statistical analysis, feature engineering, graphical analysis, and data normalisation, all developed in Jupyter notebooks.
- **Part II — Dashboard**: a Streamlit application that brings the analysis to life through interactive visualisations.

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| **League Overview** | Historical scoring trends segmented by era, 3-point revolution analysis, efficiency KPIs vs historical averages |
| **Player Profile** | Career stats, shooting percentages, draft information, temporal evolution chart with dual axis, radar chart |
| **Player Comparison** | Head-to-head statistical table, comparative radar, butterfly bar chart, career evolution by selectable metric |
| **Team Analysis** | Win/loss history, offensive and defensive ratings, pace vs league average, team roster, league scatter by season |
| **Rankings & Talents** | Historical career rankings, best players by season, multi-filter talent discovery tool, player tier distribution |

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| `01_descricao_dataset.ipynb` | Dataset inventory, null analysis, deduplication, consolidated dataset construction |
| `02_analise_estatistica.ipynb` | Central tendency, dispersion, correlations, analysis by position and historical era |
| `03_features_engineering.ipynb` | 50+ engineered features across efficiency, era, tier, physical, recognition and draft categories |
| `04_analise_grafica.ipynb` | Histograms, boxplots, scatter plots, heatmaps, temporal evolution, All-Star and MVP analysis |
| `05_normalizacao.ipynb` | Min-Max normalisation and Z-Score standardisation with visual comparison of distributions |

---

## Dataset

**NBA Stats (1947–2026)** — available on Kaggle:  
[https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats](https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats)

The dataset contains 22 CSV files with player per-game statistics, advanced metrics, team summaries, draft history, All-Star selections, award shares, and more.

---

## Tech Stack

- **Python** — pandas, numpy, plotly, streamlit
- **Jupyter Notebooks** — exploratory analysis
- **Streamlit** — multi-page interactive dashboard
- **Plotly** — interactive charts

---



## How to Run

**1. Clone the repository**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. Install dependencies**
```bash
pip install -r frontend/requirements.txt
```

**3. Run the notebooks** (in order) to generate the processed datasets in `outputs/`

**4. Launch the dashboard**
```bash
cd frontend
streamlit run Home.py
```

---

## Academic Context

Developed for the **Data Analysis Lab** curricular unit, **Degree in Informatic Engineer**, 2025/2026.
