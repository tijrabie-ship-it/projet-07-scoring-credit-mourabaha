# Projet 07 — Scoring du risque de crédit en mourabaha

Application académique développée en Python avec Flask pour évaluer le risque de défaut associé à un financement par mourabaha.

Elle utilise un modèle préentraîné chargé depuis `xgboost_mourabaha_final.pkl`, complété par des règles expertes.

## Données utilisées

L’application transmet au modèle 14 variables de base décrivant le client et le financement : âge, salaire, ancienneté professionnelle, nombre d’enfants, sexe, niveau d’études, situation familiale, type de mourabaha, montant du financement, mensualité, durée, marge, garanties et année du contrat.

La marge est calculée automatiquement dans l’interface comme la différence entre le total des mensualités et le montant financé.

Six indicateurs supplémentaires sont calculés côté serveur :

- EAD : fixé à 80 % du montant financé.
- DTI : mensualité rapportée au salaire.
- LTV : financement rapporté à la valeur des garanties.
- Couverture des garanties : garanties rapportées au financement.
- Ratio EAD : EAD rapporté au financement.
- Rapport mensualité / financement.

## Fonctionnement

### 1. Vérification de l’âge en fin de contrat

Si l’âge du client à la fin du contrat dépasse 75 ans, l’application classe automatiquement le dossier à risque élevé et attribue une valeur conventionnelle de 0,99.

### 2. Prédiction et ajustements

Dans les autres cas, l’application obtient le score du modèle puis applique des ajustements prédéfinis :

- Une majoration pour les clients de moins de 20 ans ou de plus de 55 ans.
- Une majoration lorsque l’ancienneté professionnelle est inférieure à trois ans.
- Une réduction lorsque cette ancienneté atteint dix ans.

Le score ajusté est limité à l’intervalle [0 ; 0,98]. La décision finale utilise un seuil de 0,50.

Ces ajustements constituent des règles expertes ; leur présence ne démontre pas une calibration statistique du score.

### 3. Affichage

L’interface affiche la classification du dossier et le score final en pourcentage.

Elle vérifie également que le total des mensualités couvre le montant financé avant l’envoi du formulaire.

## Fichiers

- `app.py` : serveur Flask, préparation des variables et évaluation.
- `inspect_model.py` : script auxiliaire d’inspection du modèle.
- `xgboost_mourabaha_final.pkl` : modèle préentraîné.
- `templates/index.html` : formulaire et affichage des résultats.
- `static/style.css` : présentation de l’interface.
- `requirements.txt` : dépendances.
- `start.bat` : lancement sous Windows.

Les données et les scripts d’entraînement du modèle ne sont pas inclus dans cette version.

## Installation

Depuis le dossier du projet :

```bash
python -m pip install -r requirements.txt
```

Conserver les versions précisées dans `requirements.txt` pour limiter les incompatibilités avec le modèle enregistré.

## Lancement local

```bash
python app.py
```

Ouvrir ensuite :

http://127.0.0.1:5000

Sous Windows, le fichier `start.bat` propose également l’installation des dépendances et le lancement.

## Portée

Le projet constitue une démonstration académique. Le score affiché combine la sortie du modèle et des règles expertes ; il nécessite une validation avant d’être interprété comme une probabilité de défaut calibrée.

L’évaluation porte sur le risque de crédit et ne constitue pas une validation juridique ou une certification de conformité à la charia.

Le serveur est configuré pour un usage en mode développement.
