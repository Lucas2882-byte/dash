import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "team_tasks.db")

def _auto_sync_github():
    """Synchronise automatiquement la BDD avec GitHub après chaque modification"""
    try:
        import github_sync
        github_sync.auto_backup_on_change()
    except Exception:
        pass

def init_database():
    """Initialise la base de données avec la table des tâches"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            client_name TEXT,
            assigned_to TEXT NOT NULL,
            priority TEXT DEFAULT 'Normale',
            status TEXT DEFAULT 'À faire',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified_by TEXT,
            task_order INTEGER
        )
    ''')
    
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'client_name' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN client_name TEXT')
    if 'last_modified_by' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN last_modified_by TEXT')
    if 'task_order' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN task_order INTEGER')
    if 'deadline' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN deadline DATE')
    if 'category' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN category TEXT')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            website TEXT,
            category TEXT,
            description TEXT,
            status TEXT DEFAULT 'Active',
            google_listing_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            managed_by TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS local_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            service_type TEXT,
            provider TEXT,
            area_coverage TEXT,
            phone TEXT,
            email TEXT,
            description TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            managed_by TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gmb_workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            main_step TEXT NOT NULL,
            sub_step TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            notes TEXT,
            deadline DATE,
            FOREIGN KEY (listing_id) REFERENCES google_listings(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS local_service_workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            main_step TEXT NOT NULL,
            sub_step TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            notes TEXT,
            deadline DATE,
            FOREIGN KEY (service_id) REFERENCES local_services(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute("PRAGMA table_info(google_listings)")
    listing_columns = [column[1] for column in cursor.fetchall()]
    if 'current_step' not in listing_columns:
        cursor.execute('ALTER TABLE google_listings ADD COLUMN current_step TEXT DEFAULT "Fiche prise en compte"')
    if 'client_name' not in listing_columns:
        cursor.execute('ALTER TABLE google_listings ADD COLUMN client_name TEXT')
    
    cursor.execute("PRAGMA table_info(gmb_workflow_steps)")
    workflow_columns = [column[1] for column in cursor.fetchall()]
    if 'deadline' not in workflow_columns:
        cursor.execute('ALTER TABLE gmb_workflow_steps ADD COLUMN deadline DATE')
    
    conn.commit()
    conn.close()
    
    migrate_old_workflow_steps()
    ensure_all_listings_have_workflows()
    ensure_all_services_have_workflows()
    migrate_local_service_workflow_steps()

def mark_overdue_tasks_urgent():
    """Marque automatiquement les tâches comme urgentes si leur date d'échéance est atteinte ou dépassée"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET priority = 'Urgente', updated_at = CURRENT_TIMESTAMP
        WHERE deadline IS NOT NULL 
        AND deadline <= DATE('now')
        AND priority != 'Urgente'
        AND status != 'Terminée'
    ''')
    
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    if rows_updated > 0:
        _auto_sync_github()
    
    return rows_updated

def add_task(title, description, assigned_to, priority='Normale', client_name='', deadline=None, category=None):
    """Ajoute une nouvelle tâche"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Obtenir le prochain ordre pour cette personne
    cursor.execute('''
        SELECT COALESCE(MAX(task_order), 0) + 1
        FROM tasks
        WHERE assigned_to = ?
    ''', (assigned_to,))
    next_order = cursor.fetchone()[0]
    
    cursor.execute('''
        INSERT INTO tasks (title, description, client_name, assigned_to, priority, status, task_order, deadline, category)
        VALUES (?, ?, ?, ?, ?, 'À faire', ?, ?, ?)
    ''', (title, description, client_name, assigned_to, priority, next_order, deadline, category))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_all_tasks():
    """Récupère toutes les tâches"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_tasks_by_person(person):
    """Récupère les tâches d'une personne"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM tasks WHERE assigned_to = ? ORDER BY COALESCE(task_order, 999999), created_at DESC",
        conn,
        params=[person]
    )
    conn.close()
    return df

def update_task_status(task_id, new_status, modified_by=None):
    """Met à jour le statut d'une tâche"""
    task_id = int(task_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET status = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
        WHERE id = ?
    ''', (new_status, modified_by, task_id))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def update_task(task_id, title, description, client_name, assigned_to, priority, status, modified_by=None, deadline=None, category=None):
    """Met à jour tous les champs d'une tâche"""
    task_id = int(task_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET title = ?, description = ?, client_name = ?, assigned_to = ?, priority = ?, status = ?, deadline = ?, category = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
        WHERE id = ?
    ''', (title, description, client_name, assigned_to, priority, status, deadline, category, modified_by, task_id))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_task_by_id(task_id):
    """Récupère une tâche par son ID"""
    if task_id is None:
        return None
    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        return None
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM tasks WHERE id = ?",
        conn,
        params=[task_id]
    )
    conn.close()
    if not df.empty:
        return df.iloc[0]
    return None

def delete_task(task_id):
    """Supprime une tâche"""
    task_id = int(task_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def reorder_tasks(person, task_orders):
    """Réorganise les tâches d'une personne
    task_orders: dict {task_id: new_order}
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    for task_id, new_order in task_orders.items():
        task_id = int(task_id)
        cursor.execute('''
            UPDATE tasks
            SET task_order = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND assigned_to = ?
        ''', (new_order, task_id, person))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_urgent_tasks():
    """Récupère les tâches urgentes"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM tasks WHERE priority = 'Urgente' AND status != 'Terminée' ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df

def add_google_listing(business_name, address, phone, website, category, description, google_listing_url, managed_by, client_name=''):
    """Ajoute une nouvelle fiche Google avec workflow"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO google_listings (business_name, address, phone, website, category, description, google_listing_url, managed_by, client_name, status, current_step)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'En cours', 'Fiche prise en compte')
    ''', (business_name, address, phone, website, category, description, google_listing_url, managed_by, client_name))
    
    listing_id = cursor.lastrowid
    
    workflow_steps = [
        ('Fiche prise en compte', 'Fiche prise en compte'),
        ('Local Shark', 'Infos de Base remplis'),
        ('Local Shark', 'Répondre aux anciens avis'),
        ('Local Shark', 'Photo ajouté'),
        ('Local Shark', 'Publications ajouté'),
        ('SEO Fiche GMB', 'Titre optimisé'),
        ('SEO Fiche GMB', 'Horaires optimisé'),
        ('SEO Fiche GMB', 'Catégorie optimisé'),
        ('SEO Fiche GMB', 'Zone desservie optimisé'),
        ('SEO Fiche GMB', 'Infos de base à remplir'),
        ('SEO Fiche GMB', 'Services optimisé'),
        ('SEO Fiche GMB', 'Produits optimisé'),
        ('SEO Fiche GMB', 'FAQ remplis')
    ]
    
    for main_step, sub_step in workflow_steps:
        cursor.execute('''
            INSERT INTO gmb_workflow_steps (listing_id, main_step, sub_step, completed)
            VALUES (?, ?, ?, 0)
        ''', (listing_id, main_step, sub_step))
    
    conn.commit()
    conn.close()
    _auto_sync_github()
    return listing_id

def get_all_google_listings():
    """Récupère toutes les fiches Google"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM google_listings ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_google_listing_by_id(listing_id):
    """Récupère une fiche Google par son ID"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM google_listings WHERE id = ?",
        conn,
        params=[listing_id]
    )
    conn.close()
    if not df.empty:
        return df.iloc[0]
    return None

def update_google_listing(listing_id, business_name, address, phone, website, category, description, google_listing_url, status, managed_by):
    """Met à jour une fiche Google"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE google_listings 
        SET business_name = ?, address = ?, phone = ?, website = ?, category = ?, description = ?, 
            google_listing_url = ?, status = ?, updated_at = CURRENT_TIMESTAMP, managed_by = ?
        WHERE id = ?
    ''', (business_name, address, phone, website, category, description, google_listing_url, status, managed_by, listing_id))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def delete_google_listing(listing_id):
    """Supprime une fiche Google"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM google_listings WHERE id = ?', (listing_id,))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def add_local_service(service_name, service_type, provider, area_coverage, phone, email, description, managed_by):
    """Ajoute un nouveau service local"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO local_services (service_name, service_type, provider, area_coverage, phone, email, description, managed_by, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
    ''', (service_name, service_type, provider, area_coverage, phone, email, description, managed_by))
    
    service_id = cursor.lastrowid
    
    workflow_steps = [
        ('INFOS FACTURATION', 'INFOS FACTURATION'),
        ('ASSURANCE', 'ASSURANCE'),
        ('SIRET/SIREN', 'SIRET/SIREN'),
        ('KBIS', 'KBIS'),
        ('FICHE GMB LINK', 'FICHE GMB LINK'),
        ('AVIS LINK', 'AVIS LINK'),
        ('BUDGET/SEMAINE', 'BUDGET/SEMAINE'),
        ('DATE DOCUMENT', 'DATE DOCUMENT'),
        ('DATE LANCEMENT', 'DATE LANCEMENT')
    ]
    
    for main_step, sub_step in workflow_steps:
        cursor.execute('''
            INSERT INTO local_service_workflow_steps (service_id, main_step, sub_step, completed)
            VALUES (?, ?, ?, 0)
        ''', (service_id, main_step, sub_step))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_all_local_services():
    """Récupère tous les services locaux"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM local_services ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_local_service_by_id(service_id):
    """Récupère un service local par son ID"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM local_services WHERE id = ?",
        conn,
        params=[service_id]
    )
    conn.close()
    if not df.empty:
        return df.iloc[0]
    return None

def update_local_service(service_id, service_name, service_type, provider, area_coverage, phone, email, description, status, managed_by):
    """Met à jour un service local"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE local_services 
        SET service_name = ?, service_type = ?, provider = ?, area_coverage = ?, phone = ?, 
            email = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP, managed_by = ?
        WHERE id = ?
    ''', (service_name, service_type, provider, area_coverage, phone, email, description, status, managed_by, service_id))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def delete_local_service(service_id):
    """Supprime un service local"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM local_services WHERE id = ?', (service_id,))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_workflow_steps(listing_id):
    """Récupère toutes les étapes du workflow pour une fiche"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM gmb_workflow_steps WHERE listing_id = ? ORDER BY id",
        conn,
        params=[listing_id]
    )
    conn.close()
    return df

def update_workflow_step(step_id, completed, notes=None, deadline=None):
    """Met à jour une étape du workflow"""
    step_id = int(step_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    if notes is not None and deadline is not None:
        if completed:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, notes = ?, deadline = ?
                WHERE id = ?
            ''', (notes, deadline, step_id))
        else:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 0, completed_at = NULL, notes = ?, deadline = ?
                WHERE id = ?
            ''', (notes, deadline, step_id))
    elif notes is not None:
        if completed:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, notes = ?
                WHERE id = ?
            ''', (notes, step_id))
        else:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 0, completed_at = NULL, notes = ?
                WHERE id = ?
            ''', (notes, step_id))
    elif deadline is not None:
        if completed:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, deadline = ?
                WHERE id = ?
            ''', (deadline, step_id))
        else:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 0, completed_at = NULL, deadline = ?
                WHERE id = ?
            ''', (deadline, step_id))
    else:
        if completed:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (step_id,))
        else:
            cursor.execute('''
                UPDATE gmb_workflow_steps 
                SET completed = 0, completed_at = NULL
                WHERE id = ?
            ''', (step_id,))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def update_listing_current_step(listing_id, current_step):
    """Met à jour l'étape principale courante d'une fiche"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE google_listings 
        SET current_step = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (current_step, listing_id))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_workflow_progress(listing_id):
    """Calcule la progression du workflow pour une fiche"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_steps,
            SUM(completed) as completed_steps
        FROM gmb_workflow_steps
        WHERE listing_id = ?
    ''', (listing_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] > 0:
        total = result[0]
        completed = result[1] if result[1] else 0
        return {'total': total, 'completed': completed, 'percentage': round((completed / total) * 100)}
    return {'total': 0, 'completed': 0, 'percentage': 0}

def create_workflow_steps_for_listing(listing_id, auto_sync=True):
    """Crée les étapes de workflow pour une fiche existante qui n'en a pas"""
    listing_id = int(listing_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM gmb_workflow_steps WHERE listing_id = ?', (listing_id,))
    count = cursor.fetchone()[0]
    
    changes_made = False
    if count == 0:
        workflow_steps = [
            ('Fiche prise en compte', 'Fiche prise en compte'),
            ('Local Shark', 'Infos de Base remplis'),
            ('Local Shark', 'Répondre aux anciens avis'),
            ('Local Shark', 'Photo ajouté'),
            ('Local Shark', 'Publications ajouté'),
            ('SEO Fiche GMB', 'Titre optimisé'),
            ('SEO Fiche GMB', 'Horaires optimisé'),
            ('SEO Fiche GMB', 'Catégorie optimisé'),
            ('SEO Fiche GMB', 'Zone desservie optimisé'),
            ('SEO Fiche GMB', 'Infos de base à remplir'),
            ('SEO Fiche GMB', 'Services optimisé'),
            ('SEO Fiche GMB', 'Produits optimisé'),
            ('SEO Fiche GMB', 'FAQ remplis')
        ]
        
        for main_step, sub_step in workflow_steps:
            cursor.execute('''
                INSERT INTO gmb_workflow_steps (listing_id, main_step, sub_step, completed)
                VALUES (?, ?, ?, 0)
            ''', (listing_id, main_step, sub_step))
        
        conn.commit()
        changes_made = True
    
    conn.close()
    
    if changes_made and auto_sync:
        _auto_sync_github()
    
    return changes_made

def migrate_old_workflow_steps():
    """Migre les anciennes étapes de workflow vers la nouvelle structure"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT listing_id FROM gmb_workflow_steps 
        WHERE sub_step IN ('Réception de la fiche', 'Vérification des informations', 'Création du dossier client',
                           'Configuration du compte', 'Optimisation locale', 'Validation',
                           'Optimisation de la fiche', 'Publication du contenu', 'Suivi des performances')
    ''')
    old_listings = cursor.fetchall()
    
    changes_made = len(old_listings) > 0
    
    for (listing_id,) in old_listings:
        cursor.execute('DELETE FROM gmb_workflow_steps WHERE listing_id = ?', (listing_id,))
        
        workflow_steps = [
            ('Fiche prise en compte', 'Fiche prise en compte'),
            ('Local Shark', 'Infos de Base remplis'),
            ('Local Shark', 'Répondre aux anciens avis'),
            ('Local Shark', 'Photo ajouté'),
            ('Local Shark', 'Publications ajouté'),
            ('SEO Fiche GMB', 'Titre optimisé'),
            ('SEO Fiche GMB', 'Horaires optimisé'),
            ('SEO Fiche GMB', 'Catégorie optimisé'),
            ('SEO Fiche GMB', 'Zone desservie optimisé'),
            ('SEO Fiche GMB', 'Infos de base à remplir'),
            ('SEO Fiche GMB', 'Services optimisé'),
            ('SEO Fiche GMB', 'Produits optimisé'),
            ('SEO Fiche GMB', 'FAQ remplis')
        ]
        
        for main_step, sub_step in workflow_steps:
            cursor.execute('''
                INSERT INTO gmb_workflow_steps (listing_id, main_step, sub_step, completed)
                VALUES (?, ?, ?, 0)
            ''', (listing_id, main_step, sub_step))
    
    conn.commit()
    conn.close()
    
    if changes_made:
        _auto_sync_github()

def ensure_all_listings_have_workflows():
    """S'assure que toutes les fiches Google ont des workflow steps"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM google_listings')
    listings = cursor.fetchall()
    conn.close()
    
    any_changes = False
    for listing in listings:
        if create_workflow_steps_for_listing(listing[0], auto_sync=False):
            any_changes = True
    
    if any_changes:
        _auto_sync_github()

def check_deadlines_and_create_tasks():
    """Vérifie les deadlines dépassées et crée des tâches pour Lise"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ws.id, ws.listing_id, ws.sub_step, ws.deadline, gl.business_name, gl.client_name
        FROM gmb_workflow_steps ws
        JOIN google_listings gl ON ws.listing_id = gl.id
        WHERE ws.deadline IS NOT NULL 
        AND ws.deadline <= DATE('now')
        AND ws.completed = 0
        AND ws.sub_step IN ('Photo ajouté', 'Publications ajouté')
    ''')
    
    overdue_steps = cursor.fetchall()
    
    tasks_created = False
    for step_id, listing_id, sub_step, deadline, business_name, client_name in overdue_steps:
        task_title = f"Relancer {sub_step.lower()} pour {business_name}"
        task_description = f"La deadline du {deadline} est dépassée pour l'étape '{sub_step}' de la fiche {business_name}"
        if client_name:
            task_description += f" (Client: {client_name})"
        
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE title = ? AND assigned_to = 'Lise' AND status != 'Terminée'
        ''', (task_title,))
        
        existing_task = cursor.fetchone()[0]
        
        if existing_task == 0:
            cursor.execute('''
                SELECT COALESCE(MAX(task_order), 0) + 1
                FROM tasks
                WHERE assigned_to = 'Lise'
            ''')
            next_order = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO tasks (title, description, client_name, assigned_to, priority, status, task_order)
                VALUES (?, ?, ?, 'Lise', 'Urgente', 'À faire', ?)
            ''', (task_title, task_description, client_name or '', next_order))
            tasks_created = True
    
    conn.commit()
    conn.close()
    
    if tasks_created:
        _auto_sync_github()

def get_service_workflow_steps(service_id):
    """Récupère les étapes de workflow d'un service local"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM local_service_workflow_steps WHERE service_id = ? ORDER BY id",
        conn,
        params=[service_id]
    )
    conn.close()
    return df

def update_service_workflow_step(step_id, completed, notes=None, deadline=None):
    """Met à jour une étape de workflow de service local"""
    step_id = int(step_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    if notes is not None and deadline is not None:
        if completed:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, notes = ?, deadline = ?
                WHERE id = ?
            ''', (notes, deadline, step_id))
        else:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 0, completed_at = NULL, notes = ?, deadline = ?
                WHERE id = ?
            ''', (notes, deadline, step_id))
    elif notes is not None:
        if completed:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, notes = ?
                WHERE id = ?
            ''', (notes, step_id))
        else:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 0, completed_at = NULL, notes = ?
                WHERE id = ?
            ''', (notes, step_id))
    elif deadline is not None:
        if completed:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP, deadline = ?
                WHERE id = ?
            ''', (deadline, step_id))
        else:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 0, completed_at = NULL, deadline = ?
                WHERE id = ?
            ''', (deadline, step_id))
    else:
        if completed:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (step_id,))
        else:
            cursor.execute('''
                UPDATE local_service_workflow_steps 
                SET completed = 0, completed_at = NULL
                WHERE id = ?
            ''', (step_id,))
    
    conn.commit()
    conn.close()
    _auto_sync_github()

def get_service_workflow_progress(service_id):
    """Calcule la progression du workflow pour un service local"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_steps,
            SUM(completed) as completed_steps
        FROM local_service_workflow_steps
        WHERE service_id = ?
    ''', (service_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] > 0:
        total = result[0]
        completed = result[1] if result[1] else 0
        return {'total': total, 'completed': completed, 'percentage': round((completed / total) * 100)}
    return {'total': 0, 'completed': 0, 'percentage': 0}

def create_workflow_steps_for_service(service_id, auto_sync=True):
    """Crée les étapes de workflow pour un service existant qui n'en a pas"""
    service_id = int(service_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM local_service_workflow_steps WHERE service_id = ?', (service_id,))
    count = cursor.fetchone()[0]
    
    changes_made = False
    if count == 0:
        workflow_steps = [
            ('INFOS FACTURATION', 'INFOS FACTURATION'),
            ('ASSURANCE', 'ASSURANCE'),
            ('SIRET/SIREN', 'SIRET/SIREN'),
            ('KBIS', 'KBIS'),
            ('FICHE GMB LINK', 'FICHE GMB LINK'),
            ('AVIS LINK', 'AVIS LINK'),
            ('BUDGET/SEMAINE', 'BUDGET/SEMAINE'),
            ('DATE DOCUMENT', 'DATE DOCUMENT'),
            ('DATE LANCEMENT', 'DATE LANCEMENT')
        ]
        
        for main_step, sub_step in workflow_steps:
            cursor.execute('''
                INSERT INTO local_service_workflow_steps (service_id, main_step, sub_step, completed)
                VALUES (?, ?, ?, 0)
            ''', (service_id, main_step, sub_step))
        
        conn.commit()
        changes_made = True
    
    conn.close()
    
    if changes_made and auto_sync:
        _auto_sync_github()
    
    return changes_made

def ensure_all_services_have_workflows():
    """S'assure que tous les services locaux ont des workflow steps"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM local_services')
    services = cursor.fetchall()
    conn.close()
    
    any_changes = False
    for service in services:
        if create_workflow_steps_for_service(service[0], auto_sync=False):
            any_changes = True
    
    if any_changes:
        _auto_sync_github()

def migrate_local_service_workflow_steps():
    """Migre les étapes de workflow des services locaux vers la nouvelle structure"""
    # Cette fonction ne fait plus rien - elle est gardée pour compatibilité
    # Les workflows sont maintenant créés automatiquement via ensure_all_services_have_workflows()
    pass
