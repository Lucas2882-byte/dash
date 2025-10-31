# Team Task Management Dashboard

## Overview

This is a team task management application built with Streamlit and SQLite. It provides a collaborative dashboard where team members (Franck, Lise, and Lucas) can create, view, edit, and track tasks. The application features a simple interface for managing task assignments, priorities, and statuses across the team.

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
- **Schema Design**: Single `tasks` table with the following structure:
  - `id`: Auto-incrementing primary key
  - `title`: Required task title
  - `description`: Optional task description
  - `assigned_to`: Required team member assignment
  - `priority`: Task priority (default: 'Normale', options: 'Normale', 'Urgente')
  - `status`: Task status (default: 'À faire', options: 'À faire', 'En cours', 'Terminée')
  - `created_at`: Automatic timestamp on creation
  - `updated_at`: Automatic timestamp for modifications
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