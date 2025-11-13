# 📋 Application de Gestion de Tâches et Fiches

Application Streamlit pour la gestion de tâches d'équipe et de fiches Google My Business / Services Locaux.

## 🚀 Déploiement sur Streamlit Cloud

### Prérequis
- Un compte GitHub
- Un compte Streamlit Cloud (gratuit sur https://streamlit.io/cloud)

### Étapes de déploiement

1. **Préparer les fichiers** (déjà fait ✅)
   - `main.py` : Application principale
   - `database.py` : Gestion de la base de données
   - `style.css` : Styles personnalisés
   - `requirements.txt` : Dépendances Python
   - `.gitignore` : Fichiers à ignorer par Git

2. **Créer un dépôt GitHub**
   ```bash
   # Initialiser Git dans le dossier Python
   git init
   git add main.py database.py style.css requirements.txt README.md
   git commit -m "Initial commit - Gestion de Tâches"
   
   # Créer un nouveau dépôt sur GitHub et le lier
   git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
   git branch -M main
   git push -u origin main
   ```

3. **Déployer sur Streamlit Cloud**
   - Allez sur https://share.streamlit.io/
   - Connectez-vous avec votre compte GitHub
   - Cliquez sur "New app"
   - Sélectionnez votre dépôt GitHub
   - Branche : `main`
   - Fichier principal : `main.py`
   - Cliquez sur "Deploy!"

## 📦 Structure du projet

```
Python/
├── main.py              # Application principale Streamlit
├── database.py          # Gestion SQLite de la base de données
├── style.css            # Styles CSS personnalisés
├── requirements.txt     # Dépendances Python
├── .gitignore          # Fichiers ignorés par Git
└── README.md           # Ce fichier
```

## 🛠️ Installation locale

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run main.py
```

## ✨ Fonctionnalités

### Gestion de Tâches
- ✅ Création et modification de tâches
- 👥 Assignment par membre d'équipe (Franck, Lise, Lucas)
- ⚡ Priorités (Normale / Urgente)
- 📊 Statuts (À faire / En cours / Terminée)
- 🔍 Filtres et recherche
- 📋 Vue tableau avec modification en masse
- 🎨 Couleurs selon la priorité (rouge pour urgente, vert pour normale)

### Gestion de Fiches
- 📍 Fiches Google My Business
- 🛠️ Services Locaux
- ✏️ Modification et suppression

## 🎨 Personnalisation

L'application utilise un thème sombre moderne défini dans `style.css`. Les couleurs principales :
- Violet (#8B5CF6) pour les actions principales
- Rouge (#EF4444) pour les urgences
- Vert (#22C55E) pour les tâches normales
- Bleu (#60A5FA) pour les tâches en cours

## 📝 Notes importantes

- La base de données SQLite (`team_tasks.db`) est créée automatiquement
- Les données sont sauvegardées localement
- Pour Streamlit Cloud, les données seront réinitialisées à chaque redéploiement (utiliser une base de données externe pour la production)
