import subprocess
import sys
from pathlib import Path

def save_database_to_github(db_filename="team_tasks.db", commit_message=None):
    """
    Sauvegarde la base de données sur GitHub en utilisant Git natif.
    
    Args:
        db_filename: Nom du fichier de base de données à sauvegarder
        commit_message: Message de commit personnalisé (optionnel)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    
    # Vérifier que le fichier existe
    db_path = Path(db_filename)
    if not db_path.exists():
        return False, f"❌ Fichier {db_filename} introuvable"
    
    try:
        # 1. Vérifier s'il y a des changements dans le fichier (vs dernier commit)
        result = subprocess.run(
            ["git", "diff", "--quiet", db_filename],
            capture_output=True,
            timeout=10
        )
        
        # Si returncode == 0, il n'y a rien à commiter
        if result.returncode == 0:
            return True, "✅ Aucun changement à sauvegarder"
        
        # 2. Créer le message de commit
        if not commit_message:
            from datetime import datetime
            commit_message = f"update database - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 3. Ajouter le fichier ET commiter en une seule opération atomique
        # On refait git add juste avant commit pour capturer le dernier état
        result = subprocess.run(
            ["git", "add", db_filename],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, f"❌ Erreur git add: {result.stderr}"
        
        # 4. Créer le commit immédiatement après le add
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, f"❌ Erreur git commit: {result.stderr}"
        
        # 5. Pull avant push pour éviter les conflits (fast-forward seulement)
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Ignorer les erreurs de pull si on est déjà à jour ou si fast-forward n'est pas possible
        # (dans ce cas, on essaie quand même de pusher)
        
        # 6. Push sur GitHub
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "rejected" in error_msg.lower():
                return False, "❌ Push rejeté: des changements existent sur GitHub. Veuillez synchroniser manuellement."
            return False, f"❌ Erreur git push: {error_msg}"
        
        return True, "✅ Base de données sauvegardée sur GitHub"
    
    except subprocess.TimeoutExpired:
        return False, "❌ Timeout: l'opération Git a pris trop de temps"
    except FileNotFoundError:
        return False, "❌ Git n'est pas installé ou accessible"
    except Exception as e:
        return False, f"❌ Erreur inattendue: {str(e)}"


if __name__ == "__main__":
    # Permet d'appeler le script directement
    success, message = save_database_to_github()
    print(message)
    sys.exit(0 if success else 1)
