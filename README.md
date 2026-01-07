Voici le code Markdown pur, sobre et structuré, idéal pour un profil GitHub professionnel.

Markdown

# Portfolio Project: Quantitative Finance Dashboards

Ce dépôt regroupe deux applications interactives développées avec Streamlit pour l'analyse quantitative et la gestion de portefeuille.

---

## 1. Single Asset Strategy Dashboard
Interface dédiée au backtesting de stratégies systématiques sur un titre unique.

### Fonctionnalités
* **Fetch & Visualize** : Récupération des données historiques et visualisation des prix.
* **Backtesting** : Test de stratégies basées sur des règles définies.
* **Performance** : Évaluation des rendements cumulés et des drawdowns.
* **Benchmark** : Comparaison systématique avec la stratégie Buy & Hold.

### Stratégies intégrées
* Buy & Hold
* End-of-Month & Volatility Breakout
* Trend Following (Golden Cross, MACD Crossover)
* RSI Oversold

### Métriques calculées
* Rendement total et annualisé
* Volatilité et Ratio de Sharpe
* Max Drawdown et temps de récupération

### Structure du module
```text
single_asset/
├── data_fetcher.py # Récupération des prix historiques
├── strategies.py   # Implémentation des règles de trading
├── charts.py       # Fonctions de visualisation
├── metrics.py      # Calculs de performance
└── app.py          # Interface Streamlit
Lancement :

Bash

pip install streamlit pandas numpy yfinance plotly
streamlit run single_asset/app.py
2. Quant B – Multi-Asset Portfolio Dashboard
Plateforme d'analyse de portefeuille multi-actifs intégrant des diagnostics de risque avancés.

Fonctionnalités
Portfolio Analytics : Calcul des statistiques de risque et rendement.

Allocation : Visualisation de la répartition des actifs.

Risk Management : Analyse des corrélations, VaR (Value at Risk) et CVaR.

Advanced Analytics : Exposant de Hurst, Variance Ratio et détection de régimes.

Régimes de marché détectés
Bull / Bear

Sideways (Latéral)

High Volatility

Métriques avancées
Ratios : Sharpe, Sortino, Calmar

Alpha et Beta par rapport au benchmark

Matrice de corrélation

Structure du module
Plaintext

FinalApp.py             # Interface principale
portfolio_module/
├── portfolio_core.py   # Métriques de base
├── advanced_analytics.py # Hurst, variance ratio, régimes
└── components.py       # Composants UI
utils/
└── data_fetcher.py     # Gestion des données Yahoo Finance
Lancement :

Bash

pip install streamlit pandas numpy yfinance plotly scipy
streamlit run FinalApp.py
Stack Technique
Langage : Python

Interface : Streamlit

Analyse de données : Pandas, NumPy, SciPy

Visualisation : Plotly

Données : Yahoo Finance API
