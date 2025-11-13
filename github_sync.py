import streamlit as st
import base64
import requests
from datetime import datetime
import os

def get_github_config():
    """Récupère la configuration GitHub depuis les secrets Streamlit"""
    try:
        github_token = st.secrets["github"]["token"]
        repo_owner = st.secrets["github"]["repo_owner"]
        repo_name = st.secrets["github"]["repo_name"]
        return github_token, repo_owner, repo_name
    except Exception as e:
        # Ne pas afficher d'erreur si la configuration n'existe pas
        return None, None, None

def upload_database_to_github(db_file_path="team_tasks.db"):
    """Upload la base de données sur GitHub"""
    github_token, repo_owner, repo_name = get_github_config()
    
    if not all([github_token, repo_owner, repo_name]):
        return False, "Configuration GitHub manquante"
    
    # Lire le fichier de la base de données
    try:
        with open(db_file_path, 'rb') as f:
            content = f.read()
            content_base64 = base64.b64encode(content).decode('utf-8')
    except FileNotFoundError:
        return False, "Fichier de base de données introuvable"
    
    # Chemin dans le repo GitHub
    file_path = "backups/team_tasks.db"
    
    # URL de l'API GitHub
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    # Headers pour l'authentification
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Vérifier si le fichier existe déjà pour obtenir le SHA
    response = requests.get(api_url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get('sha')
    
    # Créer le message de commit
    commit_message = f"Backup BDD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Préparer les données pour le commit
    data = {
        "message": commit_message,
        "content": content_base64,
        "branch": "main"
    }
    
    # Ajouter le SHA si le fichier existe déjà
    if sha:
        data["sha"] = sha
    
    # Faire le commit
    response = requests.put(api_url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        return True, "✅ Base de données synchronisée avec succès sur GitHub"
    else:
        return False, f"❌ Erreur lors de la synchronisation: {response.status_code} - {response.text}"

def download_database_from_github(db_file_path="team_tasks.db"):
    """Télécharge la base de données depuis GitHub"""
    github_token, repo_owner, repo_name = get_github_config()
    
    if not all([github_token, repo_owner, repo_name]):
        return False, "Configuration GitHub manquante"
    
    # Chemin dans le repo GitHub
    file_path = "backups/team_tasks.db"
    
    # URL de l'API GitHub
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    # Headers pour l'authentification
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Récupérer le fichier
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        content_base64 = response.json().get('content')
        content = base64.b64decode(content_base64)
        
        # Sauvegarder le fichier
        with open(db_file_path, 'wb') as f:
            f.write(content)
        
        return True, "✅ Base de données téléchargée depuis GitHub"
    else:
        return False, f"❌ Erreur lors du téléchargement: {response.status_code}"

def auto_backup_on_change():
    """Fonction à appeler après chaque modification de la BDD"""
    db_file = os.path.join(os.path.dirname(__file__), "team_tasks.db")
    success, message = upload_database_to_github(db_file)
    if success:
        st.toast(message, icon="✅")
    else:
        st.toast(message, icon="⚠️")
