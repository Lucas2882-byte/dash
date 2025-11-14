import streamlit as st
import base64
import requests
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

class GitHubBackupService:
    """Service pour sauvegarder la base de données SQLite sur GitHub"""

    def __init__(self):
        self.token = self._get_github_token()
        try:
            self.repo_owner = self._get_config("repo_owner", "GITHUB_REPO_OWNER")
            self.repo_name = self._get_config("repo_name", "GITHUB_REPO_NAME")
            self.branch = self._get_config("branch", "GITHUB_BRANCH", default="main")
            if self.repo_owner and self.repo_name:
                self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"
            else:
                self.api_url = None
        except:
            self.repo_owner = None
            self.repo_name = None
            self.branch = "main"
            self.api_url = None

    def _get_github_token(self):
        """Récupère le token GitHub de manière sécurisée"""
        try:
            if hasattr(st, 'secrets') and 'github' in st.secrets and 'token' in st.secrets['github']:
                return st.secrets['github']['token']
        except:
            pass

        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        return token

    def _get_config(self, key, env_key, default=None):
        """Récupère une configuration depuis Streamlit secrets ou variables d'environnement"""
        try:
            if hasattr(st, 'secrets') and 'github' in st.secrets and key in st.secrets['github']:
                return st.secrets['github'][key]
        except:
            pass

        value = os.getenv(env_key)
        if value:
            return value

        return default

    def is_configured(self):
        """Vérifie si GitHub est configuré correctement"""
        return all([self.token, self.repo_owner, self.repo_name, self.branch])

    def create_snapshot(self, db_path):
        """
        Crée un snapshot atomique de la base de données SQLite.
        Utilise database.flush_and_snapshot() pour garantir que toutes les modifications
        en cache (WAL) sont écrites sur le disque avant la copie.

        Args:
            db_path: Chemin vers le fichier de base de données à sauvegarder

        Returns:
            str: Chemin du fichier snapshot temporaire

        Raises:
            FileNotFoundError: Si le fichier de base de données n'existe pas
            sqlite3.Error: Si le checkpoint WAL ou la création du snapshot échoue
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de données introuvable: {db_path}")

        # Import local pour éviter les dépendances circulaires
        import database as db
        
        # Utiliser la fonction centralisée qui force le checkpoint WAL
        # et crée un snapshot atomique thread-safe.
        # L'erreur est propagée si le snapshot échoue - pas de fallback dangereux
        # vers shutil.copy2 qui pourrait copier des données incohérentes.
        return db.flush_and_snapshot(db_path)

    def fetch_existing_sha(self, repo_filename):
        """Récupère le SHA du fichier existant sur GitHub"""
        if not self.is_configured():
            return None

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(
                f"{self.api_url}/{repo_filename}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('sha')

            return None
        except Exception as e:
            st.warning(f"Impossible de récupérer le SHA: {e}")
            return None

    def upload_database(self, db_path, repo_filename="team_tasks.db", commit_message=None):
        """Upload et écrase la base de données sur GitHub"""

        if not self.is_configured():
            return False, "Configuration GitHub manquante"

        snapshot_path = None
        try:
            snapshot_path = self.create_snapshot(db_path)

            with open(snapshot_path, "rb") as f:
                file_bytes = f.read()

            if len(file_bytes) > 100 * 1024 * 1024:
                return False, "❌ Fichier trop volumineux (>100MB). Utilisez Git LFS."

            content_b64 = base64.b64encode(file_bytes).decode('utf-8')

            sha = self.fetch_existing_sha(repo_filename)

            if not commit_message:
                commit_message = f"Backup BDD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            payload = {
                "message": commit_message,
                "content": content_b64,
                "branch": self.branch
            }

            if sha:
                payload["sha"] = sha

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            response = requests.put(
                f"{self.api_url}/{repo_filename}",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return True, "✅ Synchronisé sur GitHub"
            else:
                error_msg = f"❌ Erreur lors de l'upload: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    error_msg += f" - {response.text[:200]}"
                return False, error_msg

        except FileNotFoundError as e:
            return False, f"❌ Fichier introuvable: {e}"
        except Exception as e:
            return False, f"❌ Erreur inattendue: {str(e)}"
        finally:
            if snapshot_path and os.path.exists(snapshot_path):
                try:
                    os.unlink(snapshot_path)
                except:
                    pass

    def download_database(self, db_path, repo_filename="team_tasks.db"):
        """Télécharge la base de données depuis GitHub"""

        if not self.is_configured():
            return False, "Configuration GitHub manquante"

        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

            response = requests.get(
                f"{self.api_url}/{repo_filename}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                content_b64 = data.get('content', '').replace('\n', '')
                file_bytes = base64.b64decode(content_b64)

                backup_path = f"{db_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)

                with open(db_path, 'wb') as f:
                    f.write(file_bytes)

                return True, f"✅ Base de données restaurée depuis GitHub ! (backup: {os.path.basename(backup_path)})"
            else:
                return False, f"❌ Erreur lors du téléchargement: {response.status_code}"

        except Exception as e:
            return False, f"❌ Erreur: {str(e)}"

backup_service = GitHubBackupService()

def upload_to_github(db_path, commit_message=None, repo_filename="team_tasks.db"):
    """Upload automatique de la base de données sur GitHub (écrase l'ancienne)"""
    return backup_service.upload_database(db_path, repo_filename, commit_message)

def download_from_github(db_path, repo_filename="team_tasks.db"):
    """Télécharge la base de données depuis GitHub"""
    return backup_service.download_database(db_path, repo_filename)

def is_github_configured():
    """Vérifie si GitHub est configuré"""
    return backup_service.is_configured()

def auto_upload(db_path):
    """Upload automatique silencieux après modification"""
    if not is_github_configured():
        return
    try:
        upload_to_github(db_path)
    except:
        pass
