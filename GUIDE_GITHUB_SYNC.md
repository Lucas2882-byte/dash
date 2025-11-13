# 🔄 Guide de Synchronisation GitHub

## 📋 Résumé
Ce guide vous explique comment configurer la synchronisation automatique de votre base de données avec GitHub pour Streamlit Cloud.

---

## 🎯 Configuration pour Streamlit Cloud

### 1️⃣ Créer un Token GitHub

1. Allez sur GitHub → **Settings** (paramètres de votre profil)
2. Allez dans **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Cliquez sur **Generate new token** → **Generate new token (classic)**
4. Donnez un nom au token : `streamlit-app-backup`
5. Sélectionnez les permissions suivantes :
   - ✅ **repo** (accès complet aux repos)
6. Cliquez sur **Generate token**
7. **⚠️ COPIEZ LE TOKEN IMMÉDIATEMENT** (vous ne pourrez plus le voir après)

### 2️⃣ Configurer les Secrets dans Streamlit Cloud

1. Allez sur [Streamlit Cloud](https://share.streamlit.io)
2. Ouvrez votre application
3. Cliquez sur **⚙️ Settings** (en haut à droite)
4. Allez dans l'onglet **Secrets**
5. Ajoutez le contenu suivant :

```toml
[github]
token = "ghp_votre_token_ici"
repo_owner = "votre_nom_utilisateur_github"
repo_name = "nom_de_votre_repo"
```

**Exemple concret :**
```toml
[github]
token = "ghp_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
repo_owner = "john-doe"
repo_name = "mon-dashboard"
```

6. Cliquez sur **Save**
7. Votre application va redémarrer automatiquement

### 3️⃣ Créer le dossier de backup sur GitHub

1. Sur votre repo GitHub, créez un dossier `backups/`
2. Ou laissez l'application le créer automatiquement lors de la première synchronisation

---

## 💻 Configuration pour Replit (développement local)

### 1️⃣ Créer le fichier de secrets

Dans le dossier `Python/.streamlit/`, créez un fichier `secrets.toml` :

```bash
cd Python/.streamlit
cp secrets.toml.example secrets.toml
```

### 2️⃣ Modifier le fichier

Ouvrez `secrets.toml` et ajoutez vos informations :

```toml
[github]
token = "ghp_votre_token_ici"
repo_owner = "votre_nom_utilisateur"
repo_name = "nom_du_repo"
```

**⚠️ IMPORTANT :** Ce fichier est déjà dans `.gitignore` pour ne pas exposer votre token !

---

## 🚀 Utilisation

### Dans la Sidebar de l'Application

Vous verrez une section **🔄 Synchronisation GitHub** avec deux boutons :

1. **📤 Upload BDD** : Sauvegarde votre base de données actuelle sur GitHub
   - Crée un commit automatique avec la date et l'heure
   - Écrase le fichier précédent (backup incrémental)

2. **📥 Download BDD** : Restaure la base de données depuis GitHub
   - Télécharge la dernière version sauvegardée
   - Recharge automatiquement l'application

### Workflow Recommandé

#### Sur Streamlit Cloud :
1. **Avant de fermer l'app** : Cliquez sur **📤 Upload BDD**
2. **Au démarrage** : Si besoin, cliquez sur **📥 Download BDD** pour restaurer

#### Sur Replit :
1. Après des modifications importantes : **📤 Upload BDD**
2. Pour synchroniser avec la version Cloud : **📥 Download BDD**

---

## 📁 Structure sur GitHub

Votre repo aura cette structure :

```
votre-repo/
├── Python/
│   ├── main.py
│   ├── database.py
│   ├── github_sync.py
│   ├── requirements.txt
│   └── ...
└── backups/
    └── team_tasks.db  ← Votre base de données sauvegardée
```

---

## ⚠️ Points Importants

### Sécurité
- ✅ Le token GitHub est stocké dans les **secrets**, jamais dans le code
- ✅ Le fichier `.gitignore` empêche de commit le token par erreur
- ❌ Ne partagez JAMAIS votre token GitHub publiquement

### Limitations
- La synchronisation est **manuelle** (vous devez cliquer sur les boutons)
- Streamlit Cloud **réinitialise la BDD** à chaque redémarrage si vous ne la restaurez pas
- Le fichier sur GitHub est **écrasé** à chaque upload (pas d'historique multiple)

### Conseils
- 💡 Faites des backups réguliers avec **📤 Upload BDD**
- 💡 Gardez votre repo GitHub **privé** si la BDD contient des données sensibles
- 💡 Pour un historique complet, GitHub garde les versions dans l'historique des commits

---

## 🐛 Dépannage

### Erreur "Configuration GitHub manquante"
➡️ Vérifiez que vous avez bien configuré les secrets (voir section 2️⃣)

### Erreur 404 lors de l'upload/download
➡️ Vérifiez que :
- Le `repo_owner` et `repo_name` sont corrects
- Le token a les permissions `repo`
- Le repo existe bien

### Erreur 401 Unauthorized
➡️ Le token GitHub est invalide ou expiré. Créez-en un nouveau.

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs de l'application
2. Vérifiez que le token GitHub est valide
3. Vérifiez que les secrets sont bien configurés

---

Bonne synchronisation ! 🎉
