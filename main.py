import streamlit as st
import database as db
import pandas as pd
from datetime import datetime
import html

st.set_page_config(
    page_title="Dashboard Équipe",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os
css_path = os.path.join(os.path.dirname(__file__), 'style.css')
with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

db.init_database()

if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Franck"
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None
if 'show_table_person' not in st.session_state:
    st.session_state.show_table_person = None

team_members = ["Franck", "Lise", "Lucas"]

team_colors = {
    "Franck": "#7A9A7E",
    "Lise": "#D4A574", 
    "Lucas": "#6B8CAE"
}

def escape_html(text):
    """Échappe les caractères HTML spéciaux pour éviter l'injection de code"""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    return html.escape(str(text))

@st.dialog("✏️ Modifier la tâche")
def edit_task_dialog(task_id):
    task = db.get_task_by_id(task_id)
    if task is None:
        st.error("Tâche introuvable")
        return
    
    with st.form("edit_task_form"):
        st.markdown("### 📝 Modifier les détails")
        title = st.text_input("Titre de la tâche *", value=task['title'])
        client_name = st.text_input("Nom du client", value=task['client_name'] if task['client_name'] else "", placeholder="Ex: Entreprise ABC")
        description = st.text_area("Description", value=task['description'] if task['description'] else "")
        
        col1, col2 = st.columns(2)
        with col1:
            assigned_to = st.selectbox("Assigner à *", team_members, index=team_members.index(task['assigned_to']))
        with col2:
            priority = st.selectbox("Priorité *", ["Normale", "Urgente"], index=0 if task['priority'] == "Normale" else 1)
        
        status = st.selectbox("Statut *", ["À faire", "En cours", "Terminée"], index=["À faire", "En cours", "Terminée"].index(str(task['status'])))
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
        
        if submitted:
            if title and assigned_to:
                db.update_task(task_id, title, description, client_name, assigned_to, priority, status, st.session_state.current_user)
                st.success("✅ Tâche modifiée avec succès !")
                st.session_state.edit_task_id = None
                st.rerun()
            else:
                st.error("⚠️ Le titre et l'assignation sont obligatoires")
        
        if cancelled:
            st.session_state.edit_task_id = None
            st.rerun()

@st.dialog("📊 Tableau des tâches", width="large")
def show_tasks_table_dialog(person_name, tasks_df):
    st.markdown(f"### 📋 Toutes les tâches de {person_name}")
    
    if not tasks_df.empty:
        st.markdown('<div style="margin-bottom: -15px;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_status = st.multiselect(
                "📋 Filtrer par statut",
                ["À faire", "En cours", "Terminée"],
                default=["À faire", "En cours", "Terminée"],
                key="filter_table_status",
                label_visibility="visible"
            )
        
        with col2:
            filter_priority = st.multiselect(
                "⚡ Filtrer par priorité",
                ["Normale", "Urgente"],
                default=["Normale", "Urgente"],
                key="filter_table_priority",
                label_visibility="visible"
            )
        
        with col3:
            all_columns = ['ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
            selected_columns = st.multiselect(
                "📋 Colonnes à afficher",
                all_columns,
                default=['ID', 'Titre', 'Client', 'Priorité', 'Statut', 'Assigné à'],
                key="filter_table_columns",
                label_visibility="visible"
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        filtered_df = tasks_df.copy()
        
        filtered_df = filtered_df[filtered_df['status'].isin(filter_status)]
        filtered_df = filtered_df[filtered_df['priority'].isin(filter_priority)]
        
        if filtered_df.empty:
            st.info("Aucune tâche ne correspond aux filtres sélectionnés")
        else:
            original_df = filtered_df.copy()
            
            display_df = filtered_df.copy()
            
            display_df = display_df.rename(columns={
                'id': 'ID',
                'title': 'Titre',
                'client_name': 'Client',
                'description': 'Description',
                'assigned_to': 'Assigné à',
                'priority': 'Priorité',
                'status': 'Statut',
                'created_at': 'Créée le',
                'updated_at': 'Modifiée le',
                'last_modified_by': 'Modifié par'
            })
            
            column_order = [col for col in selected_columns if col in display_df.columns]
            display_df = display_df[column_order]
            
            display_df = display_df.fillna('')
            
            column_config = {}
            if 'ID' in selected_columns:
                column_config["ID"] = st.column_config.NumberColumn("ID", width="small", disabled=True)
            if 'Titre' in selected_columns:
                column_config["Titre"] = st.column_config.TextColumn("Titre", width="medium", required=True)
            if 'Client' in selected_columns:
                column_config["Client"] = st.column_config.TextColumn("Client", width="medium")
            if 'Description' in selected_columns:
                column_config["Description"] = st.column_config.TextColumn("Description", width="large")
            if 'Priorité' in selected_columns:
                column_config["Priorité"] = st.column_config.SelectboxColumn("Priorité", width="small", options=["Normale", "Urgente"], required=True)
            if 'Statut' in selected_columns:
                column_config["Statut"] = st.column_config.SelectboxColumn("Statut", width="small", options=["À faire", "En cours", "Terminée"], required=True)
            if 'Créée le' in selected_columns:
                column_config["Créée le"] = st.column_config.TextColumn("Créée le", width="medium", disabled=True)
            if 'Modifiée le' in selected_columns:
                column_config["Modifiée le"] = st.column_config.TextColumn("Modifiée le", width="medium", disabled=True)
            if 'Modifié par' in selected_columns:
                column_config["Modifié par"] = st.column_config.TextColumn("Modifié par", width="small", disabled=True)
            if 'Assigné à' in selected_columns:
                column_config["Assigné à"] = st.column_config.SelectboxColumn("Assigné à", width="small", options=team_members, required=True)
            
            edited_df = st.data_editor(
                display_df,
                height=600,
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
                key="tasks_editor"
            )
            
            st.markdown("""
                <script>
                (function() {
                    function applyRowColorsInline() {
                        const dialog = document.querySelector('[data-testid="stDialog"]');
                        if (!dialog) return 0;
                        
                        const dataframe = dialog.querySelector('div[data-testid="stDataFrame"]');
                        if (!dataframe) return 0;
                        
                        const rows = dataframe.querySelectorAll('div[role="row"]');
                        let coloredCount = 0;
                        
                        rows.forEach((row, index) => {
                            if (index === 0) return; // Skip header row
                            
                            const cells = row.querySelectorAll('div[role="gridcell"]');
                            let hasUrgente = false;
                            let hasNormale = false;
                            
                            cells.forEach(cell => {
                                const text = cell.textContent || cell.innerText || '';
                                if (text.trim() === 'Urgente') {
                                    hasUrgente = true;
                                } else if (text.trim() === 'Normale') {
                                    hasNormale = true;
                                }
                            });
                            
                            if (hasUrgente) {
                                row.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                                row.style.setProperty('background-color', 'rgba(239, 68, 68, 0.15)', 'important');
                                cells.forEach(cell => {
                                    cell.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                                    cell.style.setProperty('background-color', 'rgba(239, 68, 68, 0.15)', 'important');
                                });
                                coloredCount++;
                            } else if (hasNormale) {
                                row.style.backgroundColor = 'rgba(34, 197, 94, 0.15)';
                                row.style.setProperty('background-color', 'rgba(34, 197, 94, 0.15)', 'important');
                                cells.forEach(cell => {
                                    cell.style.backgroundColor = 'rgba(34, 197, 94, 0.15)';
                                    cell.style.setProperty('background-color', 'rgba(34, 197, 94, 0.15)', 'important');
                                });
                                coloredCount++;
                            }
                        });
                        
                        return coloredCount;
                    }
                    
                    // Nettoyer l'interval précédent
                    if (window.colorRowsInterval) {
                        clearInterval(window.colorRowsInterval);
                    }
                    
                    // Appliquer immédiatement
                    setTimeout(applyRowColorsInline, 100);
                    setTimeout(applyRowColorsInline, 300);
                    setTimeout(applyRowColorsInline, 600);
                    setTimeout(applyRowColorsInline, 1000);
                    setTimeout(applyRowColorsInline, 2000);
                    
                    // Continuer à réappliquer toutes les 500ms pendant 10 secondes
                    let attempts = 0;
                    window.colorRowsInterval = setInterval(() => {
                        const colored = applyRowColorsInline();
                        attempts++;
                        
                        // Arrêter après 20 tentatives (10 secondes) ou si on a coloré au moins une ligne
                        if (attempts > 20 || (colored > 0 && attempts > 5)) {
                            clearInterval(window.colorRowsInterval);
                        }
                    }, 500);
                })();
                </script>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"**Total:** {len(display_df)} tâche(s)")
            st.markdown("**💡 Modifiez directement dans le tableau, puis cliquez sur 'Enregistrer'**")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Enregistrer les modifications", use_container_width=True, type="primary"):
                    changes_made = False
                    errors = []
                    
                    for idx in range(len(edited_df)):
                        if 'ID' in edited_df.columns:
                            task_id = int(edited_df.iloc[idx]['ID'])
                            original_row = display_df[display_df['ID'] == task_id].iloc[0] if 'ID' in display_df.columns else None
                            edited_row = edited_df.iloc[idx]
                            
                            if original_row is not None and not edited_row.equals(original_row):
                                title = edited_row.get('Titre', '')
                                client = edited_row.get('Client', '')
                                description = edited_row.get('Description', '')
                                priority = edited_row.get('Priorité', 'Normale')
                                status = edited_row.get('Statut', 'À faire')
                                assigned_to = edited_row.get('Assigné à', '')
                                
                                if not title or not assigned_to:
                                    errors.append(f"Ligne {idx + 1}: Titre et Assigné à sont obligatoires")
                                    continue
                                
                                db.update_task(task_id, title, description, client, assigned_to, priority, status, st.session_state.current_user)
                                changes_made = True
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    elif changes_made:
                        st.success("✅ Modifications enregistrées avec succès !")
                        st.rerun()
                    else:
                        st.info("Aucune modification détectée")
            
            with col2:
                if st.button("✅ Fermer", use_container_width=True):
                    st.session_state.show_table_person = None
                    st.rerun()
    else:
        st.info("Aucune tâche à afficher pour cette personne")
        if st.button("✅ Fermer", use_container_width=True, type="primary"):
            st.session_state.show_table_person = None
            st.rerun()

if st.session_state.app_mode is None:
    st.markdown("""
        <div style="text-align: center; margin-top: 80px; margin-bottom: 40px;">
            <h1 style="font-size: 48px; margin-bottom: 16px;">Bienvenue ! 👋</h1>
            <p class="subtitle" style="font-size: 20px;">Choisissez votre mode de gestion</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 60px 40px; cursor: pointer; transition: all 0.3s ease; background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));">
                    <div style="font-size: 80px; margin-bottom: 24px;">📋</div>
                    <h2 style="margin-bottom: 12px; color: #E8E9ED;">Gestion de Tâches</h2>
                    <p class="subtitle" style="font-size: 14px; margin-bottom: 24px;">Organisez et suivez les tâches de votre équipe</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📋 Accéder aux Tâches", use_container_width=True, type="primary"):
                st.session_state.app_mode = "tasks"
                st.rerun()
        
        with col_b:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 60px 40px; cursor: pointer; transition: all 0.3s ease; background: linear-gradient(135deg, rgba(245, 124, 0, 0.1), rgba(245, 124, 0, 0.05));">
                    <div style="font-size: 80px; margin-bottom: 24px;">🏢</div>
                    <h2 style="margin-bottom: 12px; color: #E8E9ED;">Gestion de Fiches</h2>
                    <p class="subtitle" style="font-size: 14px; margin-bottom: 24px;">Gérez vos fiches Google et services locaux</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🏢 Accéder aux Fiches", use_container_width=True, type="primary"):
                st.session_state.app_mode = "listings"
                st.rerun()

elif st.session_state.app_mode == "tasks":
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown("""
            <div style="margin-bottom: 16px;">
                <h1 style="margin-bottom: 4px;">Gestion de Tâches 📋</h1>
                <p class="subtitle">Gérez vos tâches et collaborez efficacement</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
        st.selectbox("👤 Vous êtes", team_members, key="current_user", label_visibility="visible")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.app_mode = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    current_user = st.session_state.current_user
    
    user_tasks = db.get_tasks_by_person(current_user)
    urgent_tasks = user_tasks[user_tasks['priority'] == 'Urgente'] if not user_tasks.empty else pd.DataFrame()
    all_tasks = db.get_all_tasks()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="icon-circle icon-all">📊</div>
                <div class="subtitle">Total des tâches</div>
                <h2 style="margin: 8px 0 0 0;">{len(user_tasks) if not user_tasks.empty else 0}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        urgent_count = len(urgent_tasks) if not urgent_tasks.empty else 0
        st.markdown(f"""
            <div class="metric-card metric-card-urgent">
                <div style="font-size: 32px; margin-bottom: 8px;">🚨</div>
                <div style="font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px;">Tâches urgentes</div>
                <h2 style="margin: 8px 0 0 0; color: white;">{urgent_count}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        in_progress = len(user_tasks[user_tasks['status'] == 'En cours']) if not user_tasks.empty else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="icon-circle icon-person">⏳</div>
                <div class="subtitle">En cours</div>
                <h2 style="margin: 8px 0 0 0;">{in_progress}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        done = len(user_tasks[user_tasks['status'] == 'Terminée']) if not user_tasks.empty else 0
        total = len(user_tasks) if not user_tasks.empty else 1
        completion_rate = round((done / total) * 100) if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="icon-circle icon-add">✅</div>
                <div class="subtitle">Taux de complétion</div>
                <h2 style="margin: 8px 0 0 0;">{completion_rate}%</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚨 Urgences", "➕ Nouvelle Tâche", "👥 Par Personne", "📊 Toutes les Tâches"])
    
    with tab1:
        st.markdown("### 🚨 Tâches Urgentes")
        
        if urgent_tasks.empty:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 48px;">
                    <div style="font-size: 64px; margin-bottom: 16px;">✨</div>
                    <h3>Aucune tâche urgente</h3>
                    <p class="subtitle">Tout est sous contrôle !</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Filtres
            col1, col2 = st.columns(2)
            
            with col1:
                filter_urgent_status = st.multiselect(
                    "📋 Filtrer par statut",
                    ["À faire", "En cours"],
                    default=["À faire", "En cours"],
                    key="filter_urgent_status"
                )
            
            with col2:
                search_urgent_client = st.text_input(
                    "🔍 Rechercher un client",
                    placeholder="Nom du client...",
                    key="search_urgent_client"
                )
            
            # Appliquer les filtres
            filtered_urgent_tasks = urgent_tasks.copy()
            
            # Filtre par statut
            filtered_urgent_tasks = filtered_urgent_tasks[filtered_urgent_tasks['status'].isin(filter_urgent_status)]
            
            # Filtre par client
            if search_urgent_client:
                filtered_urgent_tasks = filtered_urgent_tasks[
                    filtered_urgent_tasks['client_name'].str.contains(search_urgent_client, case=False, na=False)
                ]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_urgent_tasks.empty:
                st.info("Aucune tâche urgente ne correspond aux filtres sélectionnés")
            else:
                for _, task in filtered_urgent_tasks.iterrows():
                    col1, col2 = st.columns([20, 1])
                    
                    with col1:
                        # Construire le HTML de façon plus simple
                        html_parts = ['<div class="card">']
                        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                        html_parts.append('<div style="flex: 1;">')
                        html_parts.append(f'<h2 style="margin: 0 0 6px 0; color: #E8E9ED; font-size: 20px; font-weight: 700;">🔴 {escape_html(task["title"])}</h2>')
                        html_parts.append('<div style="display: flex; gap: 8px; align-items: center;">')
                        
                        # Client badge
                        if task.get('client_name'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(139, 92, 246, 0.15); color: #A78BFA;">👤 {escape_html(task["client_name"])}</span>')
                        
                        html_parts.append(f'<p class="subtitle" style="margin: 0;">Assigné à {escape_html(task["assigned_to"])}</p>')
                        html_parts.append('</div></div>')
                        
                        # Status section
                        html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: start; flex-direction: column; align-items: end;">')
                        html_parts.append('<div style="display: flex; gap: 6px;">')
                        html_parts.append(f'<span class="status-badge status-{str(task["status"]).lower().replace(" ", "-").replace("à", "a")}">{escape_html(task["status"])}</span>')
                        html_parts.append('</div>')
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créée le {escape_html(task["created_at"])}</span>')
                        
                        # Modified by badge
                        if task.get('last_modified_by') and pd.notna(task.get('last_modified_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">✏️ Modifié par {escape_html(task["last_modified_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        # Description
                        if task.get('description') and str(task.get('description')).strip():
                            html_parts.append(f'<p style="color: #9CA3AF; margin: 0; font-size: 13px;">{escape_html(task["description"])}</p>')
                        
                        html_parts.append('</div>')
                        
                        st.markdown(''.join(html_parts), unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("✏️", key=f"edit_urgent_{task['id']}", help="Modifier"):
                            st.session_state.edit_task_id = task['id']
                            st.rerun()
    
    with tab2:
        st.markdown("### ➕ Ajouter une Nouvelle Tâche")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        with st.form("new_task_form", clear_on_submit=True):
            title = st.text_input("Titre de la tâche *", placeholder="Ex: Finaliser le rapport mensuel")
            client_name = st.text_input("Nom du client", placeholder="Ex: Entreprise ABC")
            description = st.text_area("Description", placeholder="Décrivez la tâche en détail...")
            
            col1, col2 = st.columns(2)
            with col1:
                assigned_to = st.selectbox("Assigner à *", team_members)
            with col2:
                priority = st.selectbox("Priorité *", ["Normale", "Urgente"])
            
            submitted = st.form_submit_button("➕ Ajouter la tâche", use_container_width=True)
            
            if submitted:
                if title and assigned_to:
                    db.add_task(title, description, assigned_to, priority, client_name)
                    st.success(f"✅ Tâche ajoutée avec succès et assignée à {assigned_to} !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Le titre et l'assignation sont obligatoires")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 👥 Tâches par Personne")
        
        selected_person = st.selectbox("Sélectionner un membre de l'équipe", team_members, label_visibility="collapsed")
        
        person_tasks = db.get_tasks_by_person(selected_person)
        
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                    <div style="width: 64px; height: 64px; border-radius: 50%; background: {team_colors.get(selected_person, '#7A9A7E')}; display: flex; align-items: center; justify-content: center; font-size: 28px; color: white; font-weight: 700;">
                        {escape_html(selected_person[0])}
                    </div>
                    <div>
                        <h2 style="margin: 0;">{escape_html(selected_person)}</h2>
                        <p class="subtitle" style="margin: 0;">{len(person_tasks)} tâche(s) assignée(s)</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if person_tasks.empty:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 48px;">
                    <div style="font-size: 64px; margin-bottom: 16px;">📭</div>
                    <h3>Aucune tâche</h3>
                    <p class="subtitle">Rien d'assigné pour le moment</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Filtres
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_status = st.multiselect(
                    "📋 Filtrer par statut",
                    ["À faire", "En cours", "Terminée"],
                    default=["À faire", "En cours", "Terminée"],
                    key="filter_person_status"
                )
            
            with col2:
                filter_priority = st.multiselect(
                    "⚡ Filtrer par priorité",
                    ["Normale", "Urgente"],
                    default=["Normale", "Urgente"],
                    key="filter_person_priority"
                )
            
            with col3:
                all_columns = ['ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
                selected_columns = st.multiselect(
                    "📋 Colonnes à afficher",
                    all_columns,
                    default=['ID', 'Titre', 'Client', 'Priorité', 'Statut', 'Assigné à'],
                    key="filter_person_columns"
                )
            
            # Apply filters
            filtered_person_tasks = person_tasks.copy()
            filtered_person_tasks = filtered_person_tasks[filtered_person_tasks['status'].isin(filter_status)]
            filtered_person_tasks = filtered_person_tasks[filtered_person_tasks['priority'].isin(filter_priority)]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # CSS et JavaScript pour les couleurs
            st.markdown("""
                <style>
                .row-urgente {
                    background-color: rgba(239, 68, 68, 0.15) !important;
                }
                
                .row-normale {
                    background-color: rgba(34, 197, 94, 0.15) !important;
                }
                
                div[data-testid="stDataFrame"] input,
                div[data-testid="stDataFrame"] textarea,
                div[data-testid="stDataFrame"] select {
                    background-color: white !important;
                    color: #1f2937 !important;
                    border: 1px solid #d1d5db !important;
                }
                </style>
                <script>
                function applyRowColorsPerson() {
                    const rows = document.querySelectorAll('div[data-testid="stDataFrame"] tbody tr');
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        let hasUrgente = false;
                        let hasNormale = false;
                        cells.forEach(cell => {
                            const text = cell.textContent || cell.innerText || '';
                            if (text.includes('Urgente')) hasUrgente = true;
                            else if (text.includes('Normale')) hasNormale = true;
                        });
                        if (hasUrgente) {
                            row.classList.add('row-urgente');
                            row.classList.remove('row-normale');
                        } else if (hasNormale) {
                            row.classList.add('row-normale');
                            row.classList.remove('row-urgente');
                        }
                    });
                }
                setTimeout(applyRowColorsPerson, 100);
                setTimeout(applyRowColorsPerson, 300);
                setTimeout(applyRowColorsPerson, 500);
                setTimeout(applyRowColorsPerson, 1000);
                const observerPerson = new MutationObserver(() => applyRowColorsPerson());
                setTimeout(() => {
                    observerPerson.observe(document.body, { 
                        childList: true, 
                        subtree: true,
                        attributes: false,
                        characterData: false
                    });
                }, 100);
                </script>
            """, unsafe_allow_html=True)
            
            if filtered_person_tasks.empty:
                st.info("Aucune tâche ne correspond aux filtres sélectionnés")
            else:
                # Préparer le dataframe pour l'affichage
                original_df = filtered_person_tasks.copy()
                display_df = filtered_person_tasks.copy()
                
                display_df = display_df.rename(columns={
                    'id': 'ID',
                    'title': 'Titre',
                    'client_name': 'Client',
                    'description': 'Description',
                    'assigned_to': 'Assigné à',
                    'priority': 'Priorité',
                    'status': 'Statut',
                    'created_at': 'Créée le',
                    'updated_at': 'Modifiée le',
                    'last_modified_by': 'Modifié par'
                })
                
                column_order = [col for col in selected_columns if col in display_df.columns]
                display_df = display_df[column_order]
                display_df = display_df.fillna('')
                
                # Configuration des colonnes éditables
                column_config = {}
                if 'ID' in selected_columns:
                    column_config["ID"] = st.column_config.NumberColumn("ID", width="small", disabled=True)
                if 'Titre' in selected_columns:
                    column_config["Titre"] = st.column_config.TextColumn("Titre", width="medium", required=True)
                if 'Client' in selected_columns:
                    column_config["Client"] = st.column_config.TextColumn("Client", width="medium")
                if 'Description' in selected_columns:
                    column_config["Description"] = st.column_config.TextColumn("Description", width="large")
                if 'Priorité' in selected_columns:
                    column_config["Priorité"] = st.column_config.SelectboxColumn("Priorité", width="small", options=["Normale", "Urgente"], required=True)
                if 'Statut' in selected_columns:
                    column_config["Statut"] = st.column_config.SelectboxColumn("Statut", width="small", options=["À faire", "En cours", "Terminée"], required=True)
                if 'Créée le' in selected_columns:
                    column_config["Créée le"] = st.column_config.TextColumn("Créée le", width="medium", disabled=True)
                if 'Modifiée le' in selected_columns:
                    column_config["Modifiée le"] = st.column_config.TextColumn("Modifiée le", width="medium", disabled=True)
                if 'Modifié par' in selected_columns:
                    column_config["Modifié par"] = st.column_config.TextColumn("Modifié par", width="small", disabled=True)
                if 'Assigné à' in selected_columns:
                    column_config["Assigné à"] = st.column_config.SelectboxColumn("Assigné à", width="small", options=team_members, required=True)
                
                # Afficher le tableau éditable
                edited_df = st.data_editor(
                    display_df,
                    height=600,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config,
                    key="tasks_person_editor"
                )
                
                st.markdown("---")
                st.markdown(f"**Total:** {len(display_df)} tâche(s)")
                st.markdown("**💡 Double-cliquez sur une cellule pour la modifier**")
                
                # Bouton pour enregistrer les modifications
                if st.button("💾 Enregistrer les modifications", use_container_width=True, type="primary"):
                    changes_made = False
                    errors = []
                    
                    for idx in range(len(edited_df)):
                        if 'ID' in edited_df.columns:
                            task_id = int(edited_df.iloc[idx]['ID'])
                            original_row = display_df[display_df['ID'] == task_id].iloc[0] if 'ID' in display_df.columns else None
                            edited_row = edited_df.iloc[idx]
                            
                            if original_row is not None and not edited_row.equals(original_row):
                                title = edited_row.get('Titre', '')
                                client = edited_row.get('Client', '')
                                description = edited_row.get('Description', '')
                                priority = edited_row.get('Priorité', 'Normale')
                                status = edited_row.get('Statut', 'À faire')
                                assigned_to = edited_row.get('Assigné à', selected_person)
                                
                                if not title or not assigned_to:
                                    errors.append(f"Ligne {idx + 1}: Titre et Assigné à sont obligatoires")
                                    continue
                                
                                db.update_task(task_id, title, description, client, assigned_to, priority, status, st.session_state.current_user)
                                changes_made = True
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    elif changes_made:
                        st.success("✅ Modifications enregistrées avec succès !")
                        st.rerun()
                    else:
                        st.info("Aucune modification détectée")
    
    with tab4:
        st.markdown("### 📊 Vue d'Ensemble")
        
        if all_tasks.empty:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 48px;">
                    <div style="font-size: 64px; margin-bottom: 16px;">📋</div>
                    <h3>Aucune tâche</h3>
                    <p class="subtitle">Commencez par créer votre première tâche !</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                filter_person = st.multiselect(
                    "Filtrer par personne",
                    team_members,
                    default=team_members
                )
            
            with col2:
                filter_status = st.multiselect(
                    "Filtrer par statut",
                    ["À faire", "En cours", "Terminée"],
                    default=["À faire", "En cours"]
                )
            
            filtered_tasks = all_tasks[
                (all_tasks['assigned_to'].isin(filter_person)) &
                (all_tasks['status'].isin(filter_status))
            ]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_tasks.empty:
                st.info("Aucune tâche ne correspond aux filtres sélectionnés")
            else:
                for _, task in filtered_tasks.iterrows():
                    priority_icon = "🔴" if task['priority'] == "Urgente" else "🟢"
                    person_color = team_colors.get(str(task['assigned_to']), '#7A9A7E')
                    
                    col1, col2 = st.columns([20, 1])
                    
                    with col1:
                        html_parts = ['<div class="card">']
                        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                        html_parts.append('<div style="flex: 1;">')
                        html_parts.append(f'<h2 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 700; color: #E8E9ED;">{priority_icon} {escape_html(task["title"])}</h2>')
                        html_parts.append('<div style="display: flex; gap: 8px; align-items: center;">')
                        
                        # Client badge
                        if task.get('client_name'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(139, 92, 246, 0.15); color: #A78BFA;">👤 {escape_html(task["client_name"])}</span>')
                        
                        # Person info
                        html_parts.append('<div style="display: flex; align-items: center; gap: 6px;">')
                        html_parts.append(f'<div style="width: 24px; height: 24px; border-radius: 50%; background: {person_color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 11px;">')
                        html_parts.append(f'{escape_html(task["assigned_to"][0])}')
                        html_parts.append('</div>')
                        html_parts.append(f'<span style="font-weight: 500; color: #E8E9ED; font-size: 13px;">{escape_html(task["assigned_to"])}</span>')
                        html_parts.append('</div>')
                        
                        html_parts.append('</div></div>')
                        
                        # Status section
                        html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; flex-direction: column; align-items: end;">')
                        html_parts.append(f'<span class="status-badge status-{str(task["status"]).lower().replace(" ", "-").replace("à", "a")}">{escape_html(task["status"])}</span>')
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créée le {escape_html(task["created_at"])}</span>')
                        
                        # Modified by badge
                        if task.get('last_modified_by') and pd.notna(task.get('last_modified_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">✏️ Modifié par {escape_html(task["last_modified_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        # Description
                        if task.get('description') and str(task.get('description')).strip():
                            html_parts.append(f'<p style="color: #9CA3AF; margin: 0; font-size: 13px;">{escape_html(task["description"])}</p>')
                        
                        html_parts.append('</div>')
                        
                        st.markdown(''.join(html_parts), unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("✏️", key=f"edit_all_{task['id']}", help="Modifier"):
                            st.session_state.edit_task_id = task['id']
                            st.rerun()

elif st.session_state.app_mode == "listings":
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown("""
            <div style="margin-bottom: 16px;">
                <h1 style="margin-bottom: 4px;">Gestion de Fiches 🏢</h1>
                <p class="subtitle">Gérez vos fiches Google My Business et services locaux</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
        st.selectbox("👤 Vous êtes", team_members, key="current_user", label_visibility="visible")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.app_mode = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    current_user = st.session_state.current_user
    
    st.markdown("### 🏢 Gestion des Fiches Google & Services Locaux")
    
    subtab1, subtab2 = st.tabs(["📍 Fiches Google", "🛠️ Services Locaux"])
    
    with subtab1:
            st.markdown("#### 📍 Fiches Google My Business")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("##### ➕ Ajouter une nouvelle fiche")
                
                with st.form("new_google_listing_form", clear_on_submit=True):
                    business_name = st.text_input("Nom de l'entreprise *", placeholder="Ex: Restaurant Le Bon Goût")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        address = st.text_input("Adresse", placeholder="123 Rue Example, Paris")
                        phone = st.text_input("Téléphone", placeholder="+33 1 23 45 67 89")
                    with col_b:
                        website = st.text_input("Site web", placeholder="https://www.example.com")
                        category = st.selectbox("Catégorie", [
                            "Restaurant", "Commerce", "Service", "Santé", "Éducation", 
                            "Divertissement", "Hébergement", "Autre"
                        ])
                    
                    description = st.text_area("Description", placeholder="Décrivez votre entreprise...")
                    google_listing_url = st.text_input("URL de la fiche Google", placeholder="https://g.page/...")
                    
                    submitted_listing = st.form_submit_button("➕ Ajouter la fiche", use_container_width=True)
                    
                    if submitted_listing:
                        if business_name:
                            db.add_google_listing(
                                business_name, address, phone, website, category, 
                                description, google_listing_url, current_user
                            )
                            st.success(f"✅ Fiche Google ajoutée avec succès !")
                            st.rerun()
                        else:
                            st.error("⚠️ Le nom de l'entreprise est obligatoire")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                all_listings = db.get_all_google_listings()
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="icon-circle icon-all">📍</div>
                        <div class="subtitle">Total fiches</div>
                        <h2 style="margin: 8px 0 0 0;">{len(all_listings) if not all_listings.empty else 0}</h2>
                    </div>
                """, unsafe_allow_html=True)
                
                active_listings = len(all_listings[all_listings['status'] == 'Active']) if not all_listings.empty else 0
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="icon-circle icon-add">✅</div>
                        <div class="subtitle">Fiches actives</div>
                        <h2 style="margin: 8px 0 0 0;">{active_listings}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📋 Liste des Fiches Google")
            
            all_listings = db.get_all_google_listings()
            
            if all_listings.empty:
                st.markdown("""
                    <div class="card" style="text-align: center; padding: 48px;">
                        <div style="font-size: 64px; margin-bottom: 16px;">📍</div>
                        <h3>Aucune fiche Google</h3>
                        <p class="subtitle">Ajoutez votre première fiche ci-dessus !</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for _, listing in all_listings.iterrows():
                    col1, col2 = st.columns([20, 1])
                    
                    with col1:
                        html_parts = ['<div class="card">']
                        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                        html_parts.append('<div style="flex: 1;">')
                        html_parts.append(f'<h2 style="margin: 0 0 6px 0; color: #E8E9ED; font-size: 20px; font-weight: 700;">🏢 {escape_html(listing["business_name"])}</h2>')
                        html_parts.append('<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">')
                        
                        if listing.get('category'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(139, 92, 246, 0.15); color: #A78BFA;">📂 {escape_html(listing["category"])}</span>')
                        
                        if listing.get('address'):
                            html_parts.append(f'<span class="subtitle" style="margin: 0;">📍 {escape_html(listing["address"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; flex-direction: column; align-items: end;">')
                        status_class = 'status-en-cours' if listing['status'] == 'Active' else 'status-a-faire'
                        html_parts.append(f'<span class="status-badge {status_class}">{escape_html(listing["status"])}</span>')
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créée le {escape_html(listing["created_at"])}</span>')
                        
                        if listing.get('managed_by') and pd.notna(listing.get('managed_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">👤 Géré par {escape_html(listing["managed_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        if listing.get('phone') or listing.get('website') or listing.get('google_listing_url'):
                            html_parts.append('<div style="display: flex; gap: 12px; margin: 8px 0; flex-wrap: wrap;">')
                            if listing.get('phone'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">📞 {escape_html(listing["phone"])}</span>')
                            if listing.get('website'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">🌐 {escape_html(listing["website"])}</span>')
                            if listing.get('google_listing_url'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">🔗 Google</span>')
                            html_parts.append('</div>')
                        
                        if listing.get('description') and str(listing.get('description')).strip():
                            html_parts.append(f'<p style="color: #9CA3AF; margin: 0; font-size: 13px;">{escape_html(listing["description"])}</p>')
                        
                        html_parts.append('</div>')
                        
                        st.markdown(''.join(html_parts), unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_listing_{listing['id']}", help="Supprimer"):
                            db.delete_google_listing(listing['id'])
                            st.rerun()
    
    with subtab2:
            st.markdown("#### 🛠️ Services Locaux")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("##### ➕ Ajouter un nouveau service")
                
                with st.form("new_service_form", clear_on_submit=True):
                    service_name = st.text_input("Nom du service *", placeholder="Ex: Plomberie Express")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        service_type = st.selectbox("Type de service", [
                            "Plomberie", "Électricité", "Nettoyage", "Jardinage", 
                            "Déménagement", "Réparation", "Livraison", "Autre"
                        ])
                        provider = st.text_input("Fournisseur", placeholder="Nom de l'entreprise")
                    with col_b:
                        area_coverage = st.text_input("Zone de couverture", placeholder="Ex: Paris et Île-de-France")
                        phone = st.text_input("Téléphone", placeholder="+33 1 23 45 67 89")
                    
                    email = st.text_input("Email", placeholder="contact@example.com")
                    description = st.text_area("Description", placeholder="Décrivez le service...")
                    
                    submitted_service = st.form_submit_button("➕ Ajouter le service", use_container_width=True)
                    
                    if submitted_service:
                        if service_name:
                            db.add_local_service(
                                service_name, service_type, provider, area_coverage, 
                                phone, email, description, current_user
                            )
                            st.success(f"✅ Service local ajouté avec succès !")
                            st.rerun()
                        else:
                            st.error("⚠️ Le nom du service est obligatoire")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                all_services = db.get_all_local_services()
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="icon-circle icon-all">🛠️</div>
                        <div class="subtitle">Total services</div>
                        <h2 style="margin: 8px 0 0 0;">{len(all_services) if not all_services.empty else 0}</h2>
                    </div>
                """, unsafe_allow_html=True)
                
                active_services = len(all_services[all_services['status'] == 'Active']) if not all_services.empty else 0
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="icon-circle icon-add">✅</div>
                        <div class="subtitle">Services actifs</div>
                        <h2 style="margin: 8px 0 0 0;">{active_services}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📋 Liste des Services Locaux")
            
            all_services = db.get_all_local_services()
            
            if all_services.empty:
                st.markdown("""
                    <div class="card" style="text-align: center; padding: 48px;">
                        <div style="font-size: 64px; margin-bottom: 16px;">🛠️</div>
                        <h3>Aucun service local</h3>
                        <p class="subtitle">Ajoutez votre premier service ci-dessus !</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for _, service in all_services.iterrows():
                    col1, col2 = st.columns([20, 1])
                    
                    with col1:
                        html_parts = ['<div class="card">']
                        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                        html_parts.append('<div style="flex: 1;">')
                        html_parts.append(f'<h2 style="margin: 0 0 6px 0; color: #E8E9ED; font-size: 20px; font-weight: 700;">🛠️ {escape_html(service["service_name"])}</h2>')
                        html_parts.append('<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">')
                        
                        if service.get('service_type'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(139, 92, 246, 0.15); color: #A78BFA;">📂 {escape_html(service["service_type"])}</span>')
                        
                        if service.get('provider'):
                            html_parts.append(f'<span class="subtitle" style="margin: 0;">🏢 {escape_html(service["provider"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; flex-direction: column; align-items: end;">')
                        status_class = 'status-en-cours' if service['status'] == 'Active' else 'status-a-faire'
                        html_parts.append(f'<span class="status-badge {status_class}">{escape_html(service["status"])}</span>')
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créé le {escape_html(service["created_at"])}</span>')
                        
                        if service.get('managed_by') and pd.notna(service.get('managed_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">👤 Géré par {escape_html(service["managed_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        if service.get('area_coverage') or service.get('phone') or service.get('email'):
                            html_parts.append('<div style="display: flex; gap: 12px; margin: 8px 0; flex-wrap: wrap;">')
                            if service.get('area_coverage'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">📍 {escape_html(service["area_coverage"])}</span>')
                            if service.get('phone'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">📞 {escape_html(service["phone"])}</span>')
                            if service.get('email'):
                                html_parts.append(f'<span style="color: #9CA3AF; font-size: 13px;">📧 {escape_html(service["email"])}</span>')
                            html_parts.append('</div>')
                        
                        if service.get('description') and str(service.get('description')).strip():
                            html_parts.append(f'<p style="color: #9CA3AF; margin: 0; font-size: 13px;">{escape_html(service["description"])}</p>')
                        
                        html_parts.append('</div>')
                        
                        st.markdown(''.join(html_parts), unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_service_{service['id']}", help="Supprimer"):
                            db.delete_local_service(service['id'])
                            st.rerun()

if st.session_state.edit_task_id is not None:
    edit_task_dialog(st.session_state.edit_task_id)

if st.session_state.show_table_person is not None:
    person_tasks_for_table = db.get_tasks_by_person(st.session_state.show_table_person)
    show_tasks_table_dialog(st.session_state.show_table_person, person_tasks_for_table)

st.markdown('<p class="caption">💾 Toutes les données sont sauvegardées automatiquement</p>', unsafe_allow_html=True)
