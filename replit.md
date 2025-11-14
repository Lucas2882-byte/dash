# Team Task Management Dashboard

## Overview

This is a team task management application built with Streamlit and SQLite. It provides a collaborative dashboard where team members (Franck, Lise, and Lucas) can create, view, edit, and track tasks. The application features two main modules:

1. **Task Management**: Manage team tasks with assignments, priorities, and statuses
2. **Google My Business Management**: Manage GMB listings with multi-step workflow tracking for client projects

## Recent Changes

### November 13, 2025 - GitHub Auto-Sync Integration
- **Added automatic GitHub synchronization** for database backup
- **Upload automatique** : La base de données `team_tasks.db` est automatiquement uploadée sur GitHub à chaque modification
- **Écrasement automatique** : L'ancienne version est toujours écrasée (pas de multiples backups)
- **Configuration sécurisée** : Utilise l'intégration GitHub de Replit ou secrets Streamlit
- **Déclencheurs automatiques** :
  - Ajout de tâche → upload automatique
  - Modification de tâche → upload automatique
  - Ajout de fiche Google → upload automatique
  - Ajout de service local → upload automatique
- **Contrôles manuels** : Boutons Upload/Download dans la sidebar pour forcer la synchronisation

### October 31, 2025 - Google My Business Workflow System
- Added comprehensive workflow tracking system for Google My Business listings
- Three main workflow stages with sub-steps:
  - Fiche prise en compte (Form taken into account): Reception, Verification, Folder creation
  - Local Shark: Account setup, Local optimization, Validation
  - SEO Fiche GMB: Listing optimization, Content publishing, Performance tracking
- Each listing now tracks client name and current workflow stage
- Progress visualization with completion percentages
- Notes capability for each workflow sub-step
- Automatic workflow initialization for all listings (new and existing)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit
- **Rationale**: Streamlit provides a rapid development framework for creating interactive web applications with Python, eliminating the need for separate HTML/CSS/JavaScript code
- **Layout**: Wide layout mode for optimal dashboard viewing
- **State Management**: Uses Streamlit's session_state for managing UI state (e.g., tracking which task is being edited)
- **Dialog Pattern**: Implements modal dialogs for task editing to maintain context and improve UX

### Backend Architecture
- **Language**: Python
- **Database Layer**: Separate database module (`database.py`) for data persistence operations
- **Data Access Pattern**: Direct SQL queries with Pandas integration for data retrieval and display
- **Application Entry Point**: `main.py` serves as the main application controller

### Data Storage
- **Database**: SQLite (file-based)
- **Database File**: `team_tasks.db`
- **Schema Design**: Multiple tables supporting different features:
  
  **tasks table** - Team task tracking:
  - `id`: Auto-incrementing primary key
  - `title`: Required task title
  - `description`: Optional task description
  - `client_name`: Optional client name
  - `assigned_to`: Required team member assignment
  - `priority`: Task priority (default: 'Normale', options: 'Normale', 'Urgente')
  - `status`: Task status (default: 'À faire', options: 'À faire', 'En cours', 'Terminée')
  - `created_at`: Automatic timestamp on creation
  - `updated_at`: Automatic timestamp for modifications
  - `last_modified_by`: User who last modified the task
  - `task_order`: Order of task per person for custom sorting
  
  **google_listings table** - Google My Business listings:
  - `id`: Auto-incrementing primary key
  - `business_name`: Business name (required)
  - `client_name`: Client name (required)
  - `address`, `phone`, `website`: Contact information
  - `category`, `description`: Business details
  - `google_listing_url`: GMB listing URL
  - `status`: Listing status (default: 'En cours')
  - `current_step`: Current workflow stage
  - `managed_by`: Team member managing this listing
  - `created_at`, `updated_at`: Timestamps
  
  **gmb_workflow_steps table** - Workflow tracking for GMB listings:
  - `id`: Auto-incrementing primary key
  - `listing_id`: Foreign key to google_listings
  - `main_step`: Main workflow stage (e.g., 'Fiche prise en compte')
  - `sub_step`: Sub-step within the stage
  - `completed`: Boolean completion status
  - `completed_at`: Timestamp when completed
  - `notes`: Optional notes for the step
  
  **local_services table** - Local services catalog
  
- **Rationale**: SQLite chosen for simplicity and zero-configuration deployment, suitable for small team collaboration without requiring a separate database server

### Application Logic
- **Team Members**: Hardcoded list of three team members (Franck, Lise, Lucas)
- **Task Operations**: CRUD operations exposed through database module functions
- **Automatic Initialization**: Database and tables are created automatically on application startup

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **sqlite3**: Built-in Python library for SQLite database operations
- **pandas**: Data manipulation and analysis, used for converting SQL query results to DataFrames for display

### Database
- **SQLite**: Embedded relational database (no external server required)
- **File Storage**: Local file-based storage (`team_tasks.db`)

### No External APIs or Services
This application operates entirely standalone with no external API integrations or third-party services.