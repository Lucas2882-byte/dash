import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "team_tasks.db")

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
            last_modified_by TEXT
        )
    ''')
    
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'client_name' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN client_name TEXT')
    if 'last_modified_by' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN last_modified_by TEXT')
    
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
    
    conn.commit()
    conn.close()

def add_task(title, description, assigned_to, priority='Normale', client_name=''):
    """Ajoute une nouvelle tâche"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (title, description, client_name, assigned_to, priority, status)
        VALUES (?, ?, ?, ?, ?, 'À faire')
    ''', (title, description, client_name, assigned_to, priority))
    
    conn.commit()
    conn.close()

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
        "SELECT * FROM tasks WHERE assigned_to = ? ORDER BY created_at DESC",
        conn,
        params=[person]
    )
    conn.close()
    return df

def update_task_status(task_id, new_status, modified_by=None):
    """Met à jour le statut d'une tâche"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET status = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
        WHERE id = ?
    ''', (new_status, modified_by, task_id))
    
    conn.commit()
    conn.close()

def update_task(task_id, title, description, client_name, assigned_to, priority, status, modified_by=None):
    """Met à jour tous les champs d'une tâche"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET title = ?, description = ?, client_name = ?, assigned_to = ?, priority = ?, status = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
        WHERE id = ?
    ''', (title, description, client_name, assigned_to, priority, status, modified_by, task_id))
    
    conn.commit()
    conn.close()

def get_task_by_id(task_id):
    """Récupère une tâche par son ID"""
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
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()

def get_urgent_tasks():
    """Récupère les tâches urgentes"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM tasks WHERE priority = 'Urgente' AND status != 'Terminée' ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df

def add_google_listing(business_name, address, phone, website, category, description, google_listing_url, managed_by):
    """Ajoute une nouvelle fiche Google"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO google_listings (business_name, address, phone, website, category, description, google_listing_url, managed_by, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
    ''', (business_name, address, phone, website, category, description, google_listing_url, managed_by))
    
    conn.commit()
    conn.close()

def get_all_google_listings():
    """Récupère toutes les fiches Google"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM google_listings ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_google_listing_by_id(listing_id):
    """Récupère une fiche Google par son ID"""
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

def delete_google_listing(listing_id):
    """Supprime une fiche Google"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM google_listings WHERE id = ?', (listing_id,))
    
    conn.commit()
    conn.close()

def add_local_service(service_name, service_type, provider, area_coverage, phone, email, description, managed_by):
    """Ajoute un nouveau service local"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO local_services (service_name, service_type, provider, area_coverage, phone, email, description, managed_by, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
    ''', (service_name, service_type, provider, area_coverage, phone, email, description, managed_by))
    
    conn.commit()
    conn.close()

def get_all_local_services():
    """Récupère tous les services locaux"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM local_services ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_local_service_by_id(service_id):
    """Récupère un service local par son ID"""
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

def delete_local_service(service_id):
    """Supprime un service local"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM local_services WHERE id = ?', (service_id,))
    
    conn.commit()
    conn.close()
