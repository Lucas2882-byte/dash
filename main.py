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

js_path = os.path.join(os.path.dirname(__file__), 'row_colors.js')
with open(js_path) as f:
    row_colors_js = f.read()

db.init_database()

if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Franck"
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None
if 'show_table_person' not in st.session_state:
    st.session_state.show_table_person = None
if 'show_workflow_listing_id' not in st.session_state:
    st.session_state.show_workflow_listing_id = None
if 'show_workflow_service_id' not in st.session_state:
    st.session_state.show_workflow_service_id = None

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

def get_status_from_progress(percentage):
    """Détermine le statut en fonction du pourcentage de progression"""
    if percentage == 0:
        return "À faire"
    elif percentage == 100:
        return "Terminé"
    else:
        return "En cours"

def add_person_task_numbers(df):
    """Ajoute un numéro de tâche séquentiel par personne basé sur task_order"""
    if df.empty:
        return df
    
    df = df.copy()
    # Garder l'ID original pour les modifications
    df['_original_id'] = df['id']
    
    # Utiliser task_order si disponible, sinon utiliser l'ordre de création
    if 'task_order' in df.columns:
        # Trier par assigned_to et task_order
        df = df.sort_values(['assigned_to', 'task_order'], na_position='last')
        # Créer un numéro séquentiel par personne basé sur task_order
        df['person_task_number'] = df.groupby('assigned_to').cumcount() + 1
    else:
        # Fallback: créer un numéro séquentiel par personne basé sur created_at
        df = df.sort_values(['assigned_to', 'created_at'])
        df['person_task_number'] = df.groupby('assigned_to').cumcount() + 1
    
    # Remplacer id par person_task_number pour l'affichage
    df['id'] = df['person_task_number']
    
    return df

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
        # Ajouter les numéros de tâche par personne
        tasks_df = add_person_task_numbers(tasks_df)
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
            all_columns = ['Ordre', 'ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
            selected_columns = st.multiselect(
                "📋 Colonnes à afficher",
                all_columns,
                default=['Ordre', 'Titre', 'Client', 'Priorité', 'Statut', 'Assigné à'],
                key="filter_table_columns",
                label_visibility="visible"
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        filtered_df = tasks_df.copy()
        
        filtered_df = filtered_df[filtered_df['status'].isin(filter_status)]
        filtered_df = filtered_df[filtered_df['priority'].isin(filter_priority)]
        
        # Détecter si des filtres sont actifs
        all_statuses = ["À faire", "En cours", "Terminée"]
        all_priorities = ["Normale", "Urgente"]
        has_active_filters = (set(filter_status) != set(all_statuses) or set(filter_priority) != set(all_priorities))
        
        if filtered_df.empty:
            st.info("Aucune tâche ne correspond aux filtres sélectionnés")
        else:
            if has_active_filters:
                st.warning("⚠️ La réorganisation des tâches n'est pas disponible lorsque des filtres sont actifs. Affichez toutes les tâches pour pouvoir réorganiser.")
            
            original_df = filtered_df.copy()
            
            display_df = filtered_df.copy()
            
            # Ajouter la colonne Ordre seulement si aucun filtre n'est actif
            if not has_active_filters:
                display_df['Ordre'] = display_df['person_task_number']
            
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
            
            # Ajouter les badges de couleur dans la colonne Priorité
            if 'Priorité' in display_df.columns:
                display_df['Priorité'] = display_df['Priorité'].apply(
                    lambda x: f"🔴 {x}" if x == "Urgente" else f"🟢 {x}" if x == "Normale" else x
                )
            
            column_order = [col for col in selected_columns if col in display_df.columns]
            display_df = display_df[column_order]
            
            display_df = display_df.fillna('')
            
            column_config = {}
            if 'Ordre' in selected_columns:
                column_config["Ordre"] = st.column_config.NumberColumn("Ordre", width="small", help="Modifiez pour réorganiser les tâches", required=True, min_value=1)
            if 'ID' in selected_columns:
                column_config["ID"] = st.column_config.NumberColumn("ID", width="small", disabled=True)
            if 'Titre' in selected_columns:
                column_config["Titre"] = st.column_config.TextColumn("Titre", width="medium", required=True)
            if 'Client' in selected_columns:
                column_config["Client"] = st.column_config.TextColumn("Client", width="medium")
            if 'Description' in selected_columns:
                column_config["Description"] = st.column_config.TextColumn("Description", width="large")
            if 'Priorité' in selected_columns:
                column_config["Priorité"] = st.column_config.SelectboxColumn("Priorité", width="small", options=["🟢 Normale", "🔴 Urgente"], required=True)
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
            
            st.markdown(f"""
                <script>
                {row_colors_js}
                initDialogRowColors();
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
                    
                    # Première passe: réorganiser complètement l'ordre des tâches basé sur les valeurs "Ordre" saisies
                    if 'Ordre' in edited_df.columns and not original_df.empty:
                        # Créer un DataFrame temporaire avec l'ordre saisi et les IDs originaux
                        reorder_data = []
                        for idx in range(len(edited_df)):
                            original_task = original_df.iloc[idx] if idx < len(original_df) else None
                            if original_task is not None and '_original_id' in original_task:
                                task_id = int(original_task['_original_id'])
                                order_value = int(edited_df.iloc[idx]['Ordre'])
                                reorder_data.append({'task_id': task_id, 'new_order': order_value})
                        
                        if reorder_data:
                            # Trier par new_order pour obtenir l'ordre final
                            reorder_df = pd.DataFrame(reorder_data)
                            reorder_df = reorder_df.sort_values('new_order')
                            
                            # Réassigner des valeurs contiguës (1, 2, 3, etc.)
                            new_order_map = {}
                            for idx, row in enumerate(reorder_df.itertuples()):
                                new_order_map[row.task_id] = idx + 1
                            
                            # Appliquer le réordonnancement
                            db.reorder_tasks(person_name, new_order_map)
                            changes_made = True
                    
                    # Deuxième passe: traiter les autres modifications
                    for idx in range(len(edited_df)):
                        original_task = original_df.iloc[idx] if idx < len(original_df) else None
                        task_id = int(original_task['_original_id']) if original_task is not None and '_original_id' in original_task else None
                        
                        if task_id is None:
                            continue
                        
                        original_row = display_df.iloc[idx] if idx < len(display_df) else None
                        edited_row = edited_df.iloc[idx]
                        
                        if original_row is not None:
                            # Vérifier les changements (sauf Ordre qui est déjà géré)
                            needs_update = False
                            title = edited_row.get('Titre', '')
                            client = edited_row.get('Client', '')
                            description = edited_row.get('Description', '')
                            priority_raw = edited_row.get('Priorité', 'Normale')
                            priority = priority_raw.replace('🔴 ', '').replace('🟢 ', '')
                            status = edited_row.get('Statut', 'À faire')
                            assigned_to = edited_row.get('Assigné à', '')
                            
                            # Comparer avec les valeurs originales (en ignorant Ordre)
                            if (title != original_row.get('Titre', '') or
                                client != original_row.get('Client', '') or
                                description != original_row.get('Description', '') or
                                priority != original_row.get('Priorité', '').replace('🔴 ', '').replace('🟢 ', '') or
                                status != original_row.get('Statut', '') or
                                assigned_to != original_row.get('Assigné à', '')):
                                needs_update = True
                            
                            if needs_update:
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

@st.dialog("📊 Suivi de la Fiche GMB", width="large")
def show_workflow_dialog(listing_id):
    listing = db.get_google_listing_by_id(listing_id)
    if listing is None:
        st.error("Fiche introuvable")
        return
    
    if f'expanded_steps_{listing_id}' not in st.session_state:
        st.session_state[f'expanded_steps_{listing_id}'] = {listing.get('current_step'): True}
    
    st.markdown(f"### 🏢 {listing['business_name']}")
    st.markdown(f"**Client:** {listing.get('client_name', 'N/A')}")
    
    progress = db.get_workflow_progress(listing_id)
    st.markdown(f"**Progression:** {progress['completed']}/{progress['total']} étapes complétées ({progress['percentage']}%)")
    st.progress(progress['percentage'] / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    workflow_steps = db.get_workflow_steps(listing_id)
    
    if not workflow_steps.empty:
        main_steps = ['Fiche prise en compte', 'Local Shark', 'SEO Fiche GMB']
        
        for main_step in main_steps:
            step_data = workflow_steps[workflow_steps['main_step'] == main_step]
            
            if not step_data.empty:
                total_sub = len(step_data)
                completed_sub = len(step_data[step_data['completed'] == 1])
                
                step_icon = "✅" if completed_sub == total_sub else "⏳" if completed_sub > 0 else "⭕"
                
                is_expanded = st.session_state[f'expanded_steps_{listing_id}'].get(main_step, False)
                
                with st.expander(f"{step_icon} {main_step} ({completed_sub}/{total_sub})", expanded=is_expanded):
                    for _, sub_step in step_data.iterrows():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            is_completed = sub_step['completed'] == 1
                            checkbox_label = f"{'✅' if is_completed else '⭕'} {sub_step['sub_step']}"
                            
                            if sub_step.get('completed_at'):
                                checkbox_label += f" - Complété le {sub_step['completed_at']}"
                            
                            new_state = st.checkbox(
                                checkbox_label,
                                value=is_completed,
                                key=f"step_{sub_step['id']}"
                            )
                            
                            if new_state != is_completed:
                                st.session_state[f'expanded_steps_{listing_id}'][main_step] = True
                                db.update_workflow_step(sub_step['id'], new_state)
                                st.rerun()
                            
                            if sub_step.get('deadline') and not is_completed:
                                from datetime import datetime, date
                                deadline_date = datetime.strptime(sub_step['deadline'], '%Y-%m-%d').date()
                                today = date.today()
                                if deadline_date < today:
                                    st.caption(f"⚠️ Date limite dépassée: {sub_step['deadline']}")
                                else:
                                    st.caption(f"📅 Date limite: {sub_step['deadline']}")
                            
                            if sub_step.get('notes') and str(sub_step.get('notes')).strip():
                                st.caption(f"📝 {sub_step['notes']}")
                        
                        with col2:
                            if st.button("📝", key=f"note_{sub_step['id']}", help="Ajouter une note"):
                                st.session_state[f'expanded_steps_{listing_id}'][main_step] = True
                                st.session_state[f'edit_note_{sub_step["id"]}'] = True
                        
                        if st.session_state.get(f'edit_note_{sub_step["id"]}'):
                            note = st.text_area(
                                "Note",
                                value=sub_step.get('notes', ''),
                                key=f"note_input_{sub_step['id']}"
                            )
                            
                            deadline = None
                            if sub_step['sub_step'] in ['Photo ajouté', 'Publications ajouté']:
                                st.markdown("**📅 Date limite**")
                                existing_deadline = sub_step.get('deadline')
                                if existing_deadline:
                                    from datetime import datetime
                                    deadline_value = datetime.strptime(existing_deadline, '%Y-%m-%d').date()
                                else:
                                    deadline_value = None
                                
                                deadline = st.date_input(
                                    "Sélectionner la date limite",
                                    value=deadline_value,
                                    key=f"deadline_input_{sub_step['id']}",
                                    help="Date à laquelle une tâche sera créée pour Lise si l'étape n'est pas complétée"
                                )
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("💾 Enregistrer", key=f"save_note_{sub_step['id']}"):
                                    st.session_state[f'expanded_steps_{listing_id}'][main_step] = True
                                    if deadline:
                                        db.update_workflow_step(sub_step['id'], sub_step['completed'] == 1, note, str(deadline))
                                    else:
                                        db.update_workflow_step(sub_step['id'], sub_step['completed'] == 1, note)
                                    st.session_state[f'edit_note_{sub_step["id"]}'] = False
                                    st.rerun()
                            with col_b:
                                if st.button("❌ Annuler", key=f"cancel_note_{sub_step['id']}"):
                                    st.session_state[f'expanded_steps_{listing_id}'][main_step] = True
                                    st.session_state[f'edit_note_{sub_step["id"]}'] = False
                                    st.rerun()
                    
                    st.markdown("---")
                    if st.button(f"✅ Marquer '{main_step}' comme étape actuelle", key=f"set_current_{main_step}", use_container_width=True):
                        st.session_state[f'expanded_steps_{listing_id}'][main_step] = True
                        db.update_listing_current_step(listing_id, main_step)
                        st.success(f"Étape actuelle mise à jour : {main_step}")
                        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Fermer", use_container_width=True, type="primary"):
        st.session_state.show_workflow_listing_id = None
        st.rerun()

@st.dialog("📊 Suivi du Service Local", width="large")
def show_service_workflow_dialog(service_id):
    service = db.get_local_service_by_id(service_id)
    if service is None:
        st.error("Service introuvable")
        return
    
    if f'expanded_service_steps_{service_id}' not in st.session_state:
        st.session_state[f'expanded_service_steps_{service_id}'] = {}
    
    st.markdown(f"### 🛠️ {service['service_name']}")
    st.markdown(f"**Fournisseur:** {service.get('provider', 'N/A')}")
    
    progress = db.get_service_workflow_progress(service_id)
    st.markdown(f"**Progression:** {progress['completed']}/{progress['total']} étapes complétées ({progress['percentage']}%)")
    st.progress(progress['percentage'] / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    workflow_steps = db.get_service_workflow_steps(service_id)
    
    if not workflow_steps.empty:
        main_steps = ['INFOS FACTURATION', 'ASSURANCE', 'SIRET/SIREN', 'KBIS', 
                     'FICHE GMB LINK', 'AVIS LINK', 'BUDGET/SEMAINE', 'DATE DOCUMENT', 'DATE LANCEMENT']
        
        for main_step in main_steps:
            step_data = workflow_steps[workflow_steps['main_step'] == main_step]
            
            if not step_data.empty:
                for _, sub_step in step_data.iterrows():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        is_completed = sub_step['completed'] == 1
                        checkbox_label = f"{'✅' if is_completed else '⭕'} {sub_step['sub_step']}"
                        
                        if sub_step.get('completed_at'):
                            checkbox_label += f" - Complété le {sub_step['completed_at']}"
                        
                        new_state = st.checkbox(
                            checkbox_label,
                            value=is_completed,
                            key=f"service_step_{sub_step['id']}"
                        )
                        
                        if new_state != is_completed:
                            db.update_service_workflow_step(sub_step['id'], new_state)
                            st.rerun()
                        
                        if sub_step.get('notes') and str(sub_step.get('notes')).strip():
                            st.caption(f"📝 {sub_step['notes']}")
                    
                    with col2:
                        if st.button("📝", key=f"note_service_{sub_step['id']}", help="Ajouter une note"):
                            st.session_state[f'edit_service_note_{sub_step["id"]}'] = True
                    
                    if st.session_state.get(f'edit_service_note_{sub_step["id"]}'):
                        note = st.text_area(
                            "Note",
                            value=sub_step.get('notes', ''),
                            key=f"note_service_input_{sub_step['id']}"
                        )
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("💾 Enregistrer", key=f"save_service_note_{sub_step['id']}"):
                                db.update_service_workflow_step(sub_step['id'], sub_step['completed'] == 1, note)
                                st.session_state[f'edit_service_note_{sub_step["id"]}'] = False
                                st.rerun()
                        with col_b:
                            if st.button("❌ Annuler", key=f"cancel_service_note_{sub_step['id']}"):
                                st.session_state[f'edit_service_note_{sub_step["id"]}'] = False
                                st.rerun()
                
                st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Fermer", use_container_width=True, type="primary"):
        st.session_state.show_workflow_service_id = None
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
    db.check_deadlines_and_create_tasks()
    
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
                all_columns = ['Ordre', 'ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
                selected_columns = st.multiselect(
                    "📋 Colonnes à afficher",
                    all_columns,
                    default=['Ordre', 'Titre', 'Client', 'Priorité', 'Statut', 'Assigné à'],
                    key="filter_person_columns"
                )
            
            # Apply filters
            filtered_person_tasks = person_tasks.copy()
            filtered_person_tasks = filtered_person_tasks[filtered_person_tasks['status'].isin(filter_status)]
            filtered_person_tasks = filtered_person_tasks[filtered_person_tasks['priority'].isin(filter_priority)]
            
            # Détecter si des filtres sont actifs
            all_statuses = ["À faire", "En cours", "Terminée"]
            all_priorities = ["Normale", "Urgente"]
            has_active_filters = (set(filter_status) != set(all_statuses) or set(filter_priority) != set(all_priorities))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # JavaScript pour les couleurs
            st.markdown(f"""
                <script>
                {row_colors_js}
                initPersonRowColors();
                </script>
            """, unsafe_allow_html=True)
            
            if filtered_person_tasks.empty:
                st.info("Aucune tâche ne correspond aux filtres sélectionnés")
            else:
                if has_active_filters:
                    st.warning("⚠️ La réorganisation des tâches n'est pas disponible lorsque des filtres sont actifs. Affichez toutes les tâches pour pouvoir réorganiser.")
                
                # Ajouter les numéros de tâche par personne
                filtered_person_tasks = add_person_task_numbers(filtered_person_tasks)
                
                # Préparer le dataframe pour l'affichage
                original_df = filtered_person_tasks.copy()
                display_df = filtered_person_tasks.copy()
                
                # Ajouter la colonne Ordre seulement si aucun filtre n'est actif
                if not has_active_filters:
                    display_df['Ordre'] = display_df['person_task_number']
                
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
                
                # Ajouter les badges de couleur dans la colonne Priorité
                if 'Priorité' in display_df.columns:
                    display_df['Priorité'] = display_df['Priorité'].apply(
                        lambda x: f"🔴 {x}" if x == "Urgente" else f"🟢 {x}" if x == "Normale" else x
                    )
                
                column_order = [col for col in selected_columns if col in display_df.columns]
                display_df = display_df[column_order]
                display_df = display_df.fillna('')
                
                # Configuration des colonnes éditables
                column_config = {}
                if 'Ordre' in selected_columns:
                    column_config["Ordre"] = st.column_config.NumberColumn("Ordre", width="small", help="Modifiez le numéro pour changer la position de la tâche", required=True, min_value=1)
                if 'ID' in selected_columns:
                    column_config["ID"] = st.column_config.NumberColumn("ID", width="small", disabled=True)
                if 'Titre' in selected_columns:
                    column_config["Titre"] = st.column_config.TextColumn("Titre", width="medium", required=True)
                if 'Client' in selected_columns:
                    column_config["Client"] = st.column_config.TextColumn("Client", width="medium")
                if 'Description' in selected_columns:
                    column_config["Description"] = st.column_config.TextColumn("Description", width="large")
                if 'Priorité' in selected_columns:
                    column_config["Priorité"] = st.column_config.SelectboxColumn("Priorité", width="small", options=["🟢 Normale", "🔴 Urgente"], required=True)
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
                if not has_active_filters:
                    st.markdown("**💡 Modifiez le numéro dans la colonne 'Ordre' pour réorganiser les tâches**")
                else:
                    st.markdown("**💡 Double-cliquez sur une cellule pour la modifier**")
                
                # Bouton pour enregistrer les modifications
                if st.button("💾 Enregistrer les modifications", use_container_width=True, type="primary"):
                    changes_made = False
                    errors = []
                    
                    # Première passe: réorganiser complètement l'ordre des tâches basé sur les valeurs "Ordre" saisies
                    if 'Ordre' in edited_df.columns and not original_df.empty:
                        # Créer un DataFrame temporaire avec l'ordre saisi et les IDs originaux
                        reorder_data = []
                        for idx in range(len(edited_df)):
                            original_task = original_df.iloc[idx] if idx < len(original_df) else None
                            if original_task is not None and '_original_id' in original_task:
                                task_id = int(original_task['_original_id'])
                                order_value = int(edited_df.iloc[idx]['Ordre'])
                                reorder_data.append({'task_id': task_id, 'new_order': order_value})
                        
                        if reorder_data:
                            # Trier par new_order pour obtenir l'ordre final
                            reorder_df = pd.DataFrame(reorder_data)
                            reorder_df = reorder_df.sort_values('new_order')
                            
                            # Réassigner des valeurs contiguës (1, 2, 3, etc.)
                            new_order_map = {}
                            for idx, row in enumerate(reorder_df.itertuples()):
                                new_order_map[row.task_id] = idx + 1
                            
                            # Appliquer le réordonnancement
                            db.reorder_tasks(selected_person, new_order_map)
                            changes_made = True
                    
                    # Deuxième passe: traiter les autres modifications
                    for idx in range(len(edited_df)):
                        original_task = original_df.iloc[idx] if idx < len(original_df) else None
                        task_id = int(original_task['_original_id']) if original_task is not None and '_original_id' in original_task else None
                        
                        if task_id is None:
                            continue
                        
                        original_row = display_df.iloc[idx] if idx < len(display_df) else None
                        edited_row = edited_df.iloc[idx]
                        
                        if original_row is not None:
                            # Vérifier les changements (sauf Ordre qui est déjà géré)
                            needs_update = False
                            title = edited_row.get('Titre', '')
                            client = edited_row.get('Client', '')
                            description = edited_row.get('Description', '')
                            priority_raw = edited_row.get('Priorité', 'Normale')
                            priority = priority_raw.replace('🔴 ', '').replace('🟢 ', '')
                            status = edited_row.get('Statut', 'À faire')
                            assigned_to = edited_row.get('Assigné à', selected_person)
                            
                            # Comparer avec les valeurs originales (en ignorant Ordre)
                            if (title != original_row.get('Titre', '') or
                                client != original_row.get('Client', '') or
                                description != original_row.get('Description', '') or
                                priority != original_row.get('Priorité', '').replace('🔴 ', '').replace('🟢 ', '') or
                                status != original_row.get('Statut', '') or
                                assigned_to != original_row.get('Assigné à', '')):
                                needs_update = True
                            
                            if needs_update:
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
    db.check_deadlines_and_create_tasks()
    
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
                    client_name = st.text_input("Nom du client *", placeholder="Ex: M. Dupont")
                    
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
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    create_local_service = st.checkbox("✅ Gestion Local Services à faire", value=False, help="Créer automatiquement une entrée dans Services Locaux")
                    
                    submitted_listing = st.form_submit_button("➕ Ajouter la fiche", use_container_width=True)
                    
                    if submitted_listing:
                        if business_name and client_name:
                            db.add_google_listing(
                                business_name, address, phone, website, category, 
                                description, google_listing_url, current_user, client_name
                            )
                            
                            if create_local_service:
                                service_type_mapping = {
                                    "Restaurant": "Autre",
                                    "Commerce": "Autre",
                                    "Service": "Autre",
                                    "Santé": "Autre",
                                    "Éducation": "Autre",
                                    "Divertissement": "Autre",
                                    "Hébergement": "Autre",
                                    "Autre": "Autre"
                                }
                                service_type = service_type_mapping.get(category, "Autre")
                                area_coverage = address if address else ""
                                
                                db.add_local_service(
                                    service_name=business_name,
                                    service_type=service_type,
                                    provider=client_name,
                                    area_coverage=area_coverage,
                                    phone=phone if phone else "",
                                    email="",
                                    description=description if description else "",
                                    managed_by=current_user
                                )
                                st.success(f"✅ Fiche Google et Service Local ajoutés avec succès !")
                            else:
                                st.success(f"✅ Fiche Google ajoutée avec succès !")
                            
                            st.rerun()
                        else:
                            st.error("⚠️ Le nom de l'entreprise et le nom du client sont obligatoires")
                
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
            
            col_title, col_filters = st.columns([1, 2])
            with col_title:
                st.markdown("##### 📋 Liste des Fiches Google")
            
            with col_filters:
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    status_filter = st.selectbox(
                        "🔍 Filtrer par statut",
                        ["Tous", "À faire", "En cours", "Terminé"],
                        key="listing_status_filter"
                    )
                with filter_col2:
                    all_listings_for_filter = db.get_all_google_listings()
                    client_names = ["Tous"] + sorted(all_listings_for_filter['client_name'].dropna().unique().tolist()) if not all_listings_for_filter.empty else ["Tous"]
                    client_filter = st.selectbox(
                        "👤 Filtrer par client",
                        client_names,
                        key="listing_client_filter"
                    )
            
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
                    progress = db.get_workflow_progress(listing['id'])
                    
                    computed_status = get_status_from_progress(progress['percentage'])
                    
                    if status_filter != "Tous" and computed_status != status_filter:
                        continue
                    
                    if client_filter != "Tous" and listing.get('client_name') != client_filter:
                        continue
                    
                    col1, col2, col3 = st.columns([16, 2, 1])
                    
                    with col1:
                        html_parts = ['<div class="card">']
                        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                        html_parts.append('<div style="flex: 1;">')
                        html_parts.append(f'<h2 style="margin: 0 0 6px 0; color: #E8E9ED; font-size: 20px; font-weight: 700;">🏢 {escape_html(listing["business_name"])}</h2>')
                        html_parts.append('<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">')
                        
                        if listing.get('client_name'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(34, 211, 238, 0.15); color: #22D3EE;">👤 {escape_html(listing["client_name"])}</span>')
                        
                        if listing.get('category'):
                            html_parts.append(f'<span class="status-badge" style="background: rgba(139, 92, 246, 0.15); color: #A78BFA;">📂 {escape_html(listing["category"])}</span>')
                        
                        if listing.get('address'):
                            html_parts.append(f'<span class="subtitle" style="margin: 0;">📍 {escape_html(listing["address"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; flex-direction: column; align-items: end;">')
                        status_class = 'status-en-cours' if computed_status == 'En cours' else 'status-terminee' if computed_status == 'Terminé' else 'status-a-faire'
                        html_parts.append(f'<span class="status-badge {status_class}">{escape_html(computed_status)}</span>')
                        
                        if listing.get('current_step'):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">📍 Étape: {escape_html(listing["current_step"])}</span>')
                        
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créée le {escape_html(listing["created_at"])}</span>')
                        
                        if listing.get('managed_by') and pd.notna(listing.get('managed_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">👤 Géré par {escape_html(listing["managed_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        html_parts.append(f'<div style="margin: 8px 0;">')
                        html_parts.append(f'<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">')
                        html_parts.append(f'<span style="color: #9CA3AF; font-size: 12px;">Progression du workflow</span>')
                        html_parts.append(f'<span style="color: #9CA3AF; font-size: 12px;">{progress["completed"]}/{progress["total"]} ({progress["percentage"]}%)</span>')
                        html_parts.append('</div>')
                        html_parts.append(f'<div style="background: #1F2937; border-radius: 8px; height: 8px; overflow: hidden;">')
                        progress_color = "#10B981" if progress["percentage"] == 100 else "#3B82F6" if progress["percentage"] > 0 else "#6B7280"
                        html_parts.append(f'<div style="background: {progress_color}; height: 100%; width: {progress["percentage"]}%; transition: width 0.3s ease;"></div>')
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
                        if st.button("📊 Workflow", key=f"workflow_{listing['id']}", help="Voir le workflow", use_container_width=True):
                            st.session_state.show_workflow_listing_id = listing['id']
                            st.rerun()
                    
                    with col3:
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
                    progress = db.get_service_workflow_progress(service['id'])
                    
                    col1, col2, col3 = st.columns([16, 2, 1])
                    
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
                        
                        computed_status = get_status_from_progress(progress['percentage'])
                        status_class = 'status-en-cours' if computed_status == 'En cours' else 'status-terminee' if computed_status == 'Terminé' else 'status-a-faire'
                        html_parts.append(f'<span class="status-badge {status_class}">{escape_html(computed_status)}</span>')
                        
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créé le {escape_html(service["created_at"])}</span>')
                        
                        if service.get('managed_by') and pd.notna(service.get('managed_by')):
                            html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">👤 Géré par {escape_html(service["managed_by"])}</span>')
                        
                        html_parts.append('</div></div>')
                        
                        html_parts.append(f'<div style="margin: 8px 0;">')
                        html_parts.append(f'<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">')
                        html_parts.append(f'<span style="color: #9CA3AF; font-size: 12px;">Progression du workflow</span>')
                        html_parts.append(f'<span style="color: #9CA3AF; font-size: 12px;">{progress["completed"]}/{progress["total"]} ({progress["percentage"]}%)</span>')
                        html_parts.append('</div>')
                        html_parts.append(f'<div style="background: #1F2937; border-radius: 8px; height: 8px; overflow: hidden;">')
                        progress_color = "#10B981" if progress["percentage"] == 100 else "#3B82F6" if progress["percentage"] > 0 else "#6B7280"
                        html_parts.append(f'<div style="background: {progress_color}; height: 100%; width: {progress["percentage"]}%; transition: width 0.3s ease;"></div>')
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
                        if st.button("📊 Workflow", key=f"workflow_service_{service['id']}", help="Voir le workflow", use_container_width=True):
                            st.session_state.show_workflow_service_id = service['id']
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_service_{service['id']}", help="Supprimer"):
                            db.delete_local_service(service['id'])
                            st.rerun()

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔄 Synchronisation GitHub")
    st.markdown("Sauvegardez votre base de données sur GitHub")
    
    try:
        import github_sync
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Upload BDD", use_container_width=True, help="Sauvegarder la BDD sur GitHub"):
                with st.spinner("Synchronisation en cours..."):
                    success, message = github_sync.upload_database_to_github(db.DATABASE_FILE)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        with col2:
            if st.button("📥 Download BDD", use_container_width=True, help="Restaurer la BDD depuis GitHub"):
                with st.spinner("Téléchargement en cours..."):
                    success, message = github_sync.download_database_from_github(db.DATABASE_FILE)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        st.caption("⚙️ Configurez vos secrets GitHub dans `.streamlit/secrets.toml`")
    except Exception as e:
        st.caption("⚠️ Synchronisation GitHub non configurée")

if st.session_state.edit_task_id is not None:
    edit_task_dialog(st.session_state.edit_task_id)
elif st.session_state.show_table_person is not None:
    person_tasks_for_table = db.get_tasks_by_person(st.session_state.show_table_person)
    show_tasks_table_dialog(st.session_state.show_table_person, person_tasks_for_table)
elif st.session_state.show_workflow_listing_id is not None:
    show_workflow_dialog(st.session_state.show_workflow_listing_id)
elif st.session_state.show_workflow_service_id is not None:
    show_service_workflow_dialog(st.session_state.show_workflow_service_id)

st.markdown('<p class="caption">💾 Toutes les données sont sauvegardées automatiquement</p>', unsafe_allow_html=True)
