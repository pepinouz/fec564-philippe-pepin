# Optimisation de Portefeuille - FEC 564

Ce projet implémente une application web d'optimisation de portefeuille, en utilisant Python, Dash, et Plotly. L'application permet de visualiser la frontière efficiente et d’explorer divers portefeuilles pour trouver un équilibre optimal entre le rendement et le risque, dans le contexte de gestion d'un portefeuille de caisse de retraite.

## Fonctionnalités

- **Frontière efficiente** : Génération et visualisation de la frontière efficiente, montrant les portefeuilles offrant le meilleur ratio rendement/risque.
- **Tableau de portefeuilles** : Affichage d'un tableau des portefeuilles sur la frontière, avec les informations sur le rendement, le risque, le ratio de Sharpe et la répartition des actifs.
- **Portefeuille optimal** : Identification et affichage du portefeuille optimal en fonction des contraintes spécifiques (ici, le portefeuille 17).
- **Portefeuille actuel** : Comparaison du portefeuille actuel avec les portefeuilles optimaux pour évaluer les opportunités d'amélioration.

## Structure du Code

- **app.py** : Fichier principal contenant le code de l'application Dash.
- **assets/** : Dossier pour les fichiers CSS, images, et autres ressources.
- **README.md** : Guide du projet et des fonctionnalités.

## Installation

1. Clonez ce dépôt :
    ```bash
    git clone https://github.com/pepinouz/fec564-philippe-pepin.git
    ```
2. Installez les dépendances dans un environnement virtuel :
    ```bash
    python3 -m venv env
    source env/bin/activate  # ou `env\Scripts\activate` sous Windows
    pip install -r requirements.txt
    ```
3. Lancez l'application :
    ```bash
    python app.py
    ```

## Utilisation

Après avoir lancé l'application, ouvrez un navigateur à l'adresse `http://127.0.0.1:8050`. Vous y trouverez :
- **Graphique de la frontière efficiente** : visualisation des portefeuilles optimaux en fonction du rendement et du risque.
- **Tableau des portefeuilles** : exploration des portefeuilles en pourcentages, incluant le portefeuille actuel et le portefeuille optimal (portefeuille 17).
- **Carte du portefeuille optimal** : détails sur le portefeuille 17, choisi pour son excellent ratio rendement/risque.

## Contexte Économique et Justification

L’application a été conçue dans le cadre d’une analyse de portefeuille de caisse de retraite, répondant aux contraintes d’optimisation tout en respectant les restrictions de répartition d’actifs (variation maximale de 10 % et ajout limité à 10 % pour tout nouvel actif).

## Contributeurs

- **Philippe Pepin** - Créateur du projet

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier [LICENSE](LICENSE) pour plus d’informations.
