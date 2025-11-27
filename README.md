# portolio_project

portfolio_project

Ce projet est un moteur de backtesting univarié permettant de tester des stratégies quantitatives sur un seul actif. Il inclut la récupération des données, la génération de signaux, la simulation du portefeuille et le calcul des métriques de performance.

1. Fonctionnalités

Récupération automatique des données de marché

Construction des signaux (momentum, breakout, moyennes mobiles, etc.)

Génération des positions

Simulation PnL et equity curve

Calcul des principales métriques : Sharpe, drawdown, volatilité annuelle, CAGR

Architecture modulaire (utils, core, components)

2. Structure du projet
portfolio_project/
│
├── app.py                          # Script principal
│
├── portfolio_module/
│   ├── portfolio_core.py           # Logique du backtest
│   ├── components.py               # Fonctions génériques
│
├── utils/
│   ├── data_fetcher.py             # Gestion des données
│   ├── __init__.py
│
└── README.md

3. Installation

Cloner le projet :

git clone https://github.com/<username>/portfolio_project.git
cd portfolio_project


Installer les dépendances :

pip install -r requirements.txt

4. Exécution du projet
Méthode 1 : Exécuter le script principal
python app.py


Ce script exécute un backtest complet avec les paramètres définis dans app.py.



5. Personnalisation

Les paramètres de backtest peuvent être modifiés dans :

app.py pour l’exécution directe

portfolio_module/portfolio_core.py pour ajuster la logique du moteur

utils/data_fetcher.py pour changer la source de données

6. Prochaines évolutions

Support multi-actifs

Interface Streamlit

Optimisation automatique des hyperparamètres

Ajout des frais de transaction et slippage

Si tu veux une version plus concise, ou une version plus "professionnelle GitHub", je peux te la faire aussi.