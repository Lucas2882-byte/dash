import streamlit as st
import streamlit.components.v1 as components
import database as db
import pandas as pd
from datetime import datetime
import html
import base64
import os

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
db.mark_overdue_tasks_urgent()

# Charger les icônes en base64
def get_base64_image(image_path):
    """Convertit une image en base64 pour l'utiliser dans le HTML"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Charger les icônes
icon_tasks_base64 = get_base64_image(os.path.join(os.path.dirname(__file__), 'attached_assets', 'icon-tasks.png'))
icon_fiches_base64 = get_base64_image(os.path.join(os.path.dirname(__file__), 'attached_assets', 'icon-fiches.png'))

if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Franck"
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
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

def create_clickable_card(title, subtitle, icon_base64, card_id):
    """Crée une carte iOS premium entièrement cliquable"""
    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
                padding: 0;
            }}
            .ios-premium-card {{
                position: relative;
                background: linear-gradient(145deg, 
                    rgba(255, 255, 255, 0.08) 0%, 
                    rgba(255, 255, 255, 0.02) 100%);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 32px;
                padding: 48px 32px;
                min-height: 380px;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            .ios-premium-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(
                    circle at 50% 0%,
                    rgba(167, 139, 250, 0.15) 0%,
                    transparent 60%
                );
                opacity: 0;
                transition: opacity 0.4s ease;
            }}
            .ios-premium-card:hover {{
                transform: translateY(-12px) scale(1.02) perspective(1000px) {('rotateY(-2deg)' if card_id == 'tasks' else 'rotateY(2deg)')};
                border-color: rgba(167, 139, 250, 0.4);
                box-shadow: 
                    0 20px 60px rgba(167, 139, 250, 0.3),
                    0 0 0 1px rgba(167, 139, 250, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
            }}
            .ios-premium-card:hover::before {{
                opacity: 1;
            }}
            .card-glow {{
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(
                    circle,
                    rgba(167, 139, 250, 0.4) 0%,
                    transparent 70%
                );
                opacity: 0;
                transition: opacity 0.6s ease;
                pointer-events: none;
            }}
            .ios-premium-card:hover .card-glow {{
                opacity: 0.6;
                animation: glow-pulse 2s ease-in-out infinite;
            }}
            @keyframes glow-pulse {{
                0%, 100% {{ opacity: 0.4; }}
                50% {{ opacity: 0.7; }}
            }}
            .card-content {{
                position: relative;
                z-index: 1;
            }}
            .icon-container {{
                width: 160px;
                height: 160px;
                margin: 0 auto 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            .ios-premium-card:hover .icon-container {{
                transform: scale(1.1) rotateY(10deg);
            }}
            .card-icon {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.3));
                transition: filter 0.4s ease;
            }}
            .ios-premium-card:hover .card-icon {{
                filter: drop-shadow(0 12px 32px rgba(167, 139, 250, 0.6));
            }}
            .card-title {{
                font-size: 28px;
                font-weight: 700;
                color: #F5F5F7;
                margin-bottom: 12px;
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, #F5F5F7 0%, #E8E9ED 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .card-subtitle {{
                font-size: 16px;
                color: rgba(245, 245, 247, 0.7);
                line-height: 1.6;
                max-width: 280px;
                margin: 0 auto;
            }}
        </style>
    </head>
    <body>
        <div class="ios-premium-card" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '{card_id}'}}, '*')">
            <div class="card-glow"></div>
            <div class="card-content">
                <div class="icon-container">
                    <img src="data:image/png;base64,{icon_base64}" alt="{title}" class="card-icon" />
                </div>
                <h2 class="card-title">{title}</h2>
                <p class="card-subtitle">{subtitle}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return components.html(card_html, height=450)

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
            all_columns = ['Ordre', 'ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Date d\'échéance', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
            selected_columns = st.multiselect(
                "📋 Colonnes à afficher",
                all_columns,
                default=['Ordre', 'Titre', 'Client', 'Priorité', 'Statut', 'Date d\'échéance', 'Assigné à'],
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
                'deadline': 'Date d\'échéance',
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
            if 'Date d\'échéance' in selected_columns:
                column_config["Date d'échéance"] = st.column_config.TextColumn("Date d'échéance", width="medium")
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
                                original_order = int(original_df.iloc[idx]['Ordre']) if 'Ordre' in original_df.columns else idx + 1
                                order_value = int(edited_df.iloc[idx]['Ordre'])
                                reorder_data.append({
                                    'task_id': task_id, 
                                    'new_order': order_value,
                                    'original_order': original_order,
                                    'original_idx': idx
                                })
                        
                        if reorder_data:
                            # Trier par new_order, puis par original_idx pour gérer les doublons
                            reorder_df = pd.DataFrame(reorder_data)
                            reorder_df = reorder_df.sort_values(['new_order', 'original_idx'])
                            
                            # Réassigner des valeurs contiguës (1, 2, 3, etc.)
                            new_order_map = {}
                            for idx, row in enumerate(reorder_df.itertuples()):
                                new_order_map[row.task_id] = idx + 1
                            
                            # Vérifier s'il y a vraiment eu un changement d'ordre
                            order_changed = False
                            for idx in range(len(original_df)):
                                task_id = int(original_df.iloc[idx]['_original_id'])
                                original_order = int(original_df.iloc[idx]['Ordre']) if 'Ordre' in original_df.columns else idx + 1
                                if task_id in new_order_map and new_order_map[task_id] != original_order:
                                    order_changed = True
                                    break
                            
                            # Appliquer le réordonnancement seulement si l'ordre a changé
                            if order_changed:
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
    
    # Header premium iOS style
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h2 style="margin: 0 0 8px 0; color: #F5F5F7; font-size: 28px; font-weight: 700; letter-spacing: -0.02em;">🏢 {listing['business_name']}</h2>
        <p style="margin: 0; color: #86868B; font-size: 15px; font-weight: 400;">Client: {listing.get('client_name', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = db.get_workflow_progress(listing_id)
    st.markdown(f"""
    <div style="margin-bottom: 32px;">
        <p style="margin: 0 0 8px 0; color: #86868B; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Progression: {progress['completed']}/{progress['total']} étapes complétées ({progress['percentage']}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    workflow_steps = db.get_workflow_steps(listing_id)
    
    if not workflow_steps.empty:
        main_steps = ['Fiche prise en compte', 'Local Shark', 'SEO Fiche GMB']
        step_colors = {
            'Fiche prise en compte': '#10B981',
            'Local Shark': '#3B82F6',
            'SEO Fiche GMB': '#8B5CF6'
        }
        
        for main_step in main_steps:
            step_data = workflow_steps[workflow_steps['main_step'] == main_step]
            
            if not step_data.empty:
                total_sub = len(step_data)
                completed_sub = len(step_data[step_data['completed'] == 1])
                percentage = round((completed_sub / total_sub) * 100) if total_sub > 0 else 0
                
                step_color = step_colors.get(main_step, '#7A9A7E')
                
                # Premium iOS Card avec bordure colorée
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(30, 33, 42, 0.7) 0%, rgba(26, 29, 41, 0.7) 100%);
                    border: 2px solid {step_color};
                    border-radius: 20px;
                    padding: 20px;
                    margin-bottom: 16px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.03);
                    backdrop-filter: blur(20px);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="
                                width: 8px;
                                height: 8px;
                                border-radius: 50%;
                                background: {step_color};
                                box-shadow: 0 0 12px {step_color};
                            "></div>
                            <h3 style="margin: 0; color: #F5F5F7; font-size: 19px; font-weight: 600; letter-spacing: -0.02em;">{main_step}</h3>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 32px; font-weight: 700; color: {step_color}; line-height: 1; margin-bottom: 2px;">{percentage}%</div>
                            <div style="font-size: 11px; color: #86868B; font-weight: 500;">{completed_sub}/{total_sub} complétées</div>
                        </div>
                    </div>
                    <div style="
                        width: 100%; 
                        height: 6px; 
                        background: rgba(255,255,255,0.08); 
                        border-radius: 10px; 
                        overflow: hidden;
                        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
                    ">
                        <div style="
                            width: {percentage}%; 
                            height: 100%; 
                            background: linear-gradient(90deg, {step_color} 0%, {step_color}dd 100%);
                            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                            box-shadow: 0 0 8px {step_color}80;
                        "></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Sous-étapes avec design premium
                for _, sub_step in step_data.iterrows():
                    is_completed = sub_step['completed'] == 1
                    
                    # Container pour chaque sous-étape
                    col_check, col_note = st.columns([20, 1])
                    
                    with col_check:
                        checkbox_label = sub_step['sub_step']
                        if sub_step.get('completed_at'):
                            checkbox_label += f" - Complété le {sub_step['completed_at']}"
                        
                        new_state = st.checkbox(
                            checkbox_label,
                            value=is_completed,
                            key=f"step_{sub_step['id']}"
                        )
                        
                        if new_state != is_completed:
                            db.update_workflow_step(sub_step['id'], new_state)
                            st.rerun()
                        
                        if sub_step.get('notes') and str(sub_step.get('notes')).strip():
                            st.caption(f"💬 {sub_step['notes']}")
                    
                    with col_note:
                        if st.button("📄", key=f"note_{sub_step['id']}", help="Ajouter une note"):
                            st.session_state[f'edit_note_{sub_step["id"]}'] = True
                    
                    # Éditeur de note
                    if st.session_state.get(f'edit_note_{sub_step["id"]}'):
                        note = st.text_area(
                            "Note",
                            value=sub_step.get('notes', ''),
                            key=f"note_input_{sub_step['id']}",
                            placeholder="Ajouter une note..."
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
                            if st.button("💾 Enregistrer", key=f"save_note_{sub_step['id']}", use_container_width=True):
                                if deadline:
                                    db.update_workflow_step(sub_step['id'], sub_step['completed'] == 1, note, str(deadline))
                                else:
                                    db.update_workflow_step(sub_step['id'], sub_step['completed'] == 1, note)
                                st.session_state[f'edit_note_{sub_step["id"]}'] = False
                                st.rerun()
                        with col_b:
                            if st.button("✕ Annuler", key=f"cancel_note_{sub_step['id']}", use_container_width=True):
                                st.session_state[f'edit_note_{sub_step["id"]}'] = False
                                st.rerun()
                
                # Bouton marquer comme étape actuelle
                if st.button(f"✅ Marquer comme étape actuelle", key=f"set_current_{main_step}", use_container_width=True):
                    db.update_listing_current_step(listing_id, main_step)
                    st.success(f"Étape actuelle mise à jour : {main_step}")
                    st.rerun()
                
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("Fermer", use_container_width=True, type="primary"):
        st.session_state.show_workflow_listing_id = None
        st.rerun()

@st.dialog("📊 Suivi du Service Local", width="large")
def show_service_workflow_dialog(service_id):
    service = db.get_local_service_by_id(service_id)
    if service is None:
        st.error("Service introuvable")
        return
    
    # Bouton de fermeture aligné à droite
    col_spacer, col_close = st.columns([10, 1])
    with col_close:
        if st.button("✕", key="close_service_dialog", help="Fermer"):
            st.session_state.show_workflow_service_id = None
            st.rerun()
    
    progress = db.get_service_workflow_progress(service_id)
    
    st.markdown(f"""
    <div class="ios-progress-header">
        <div class="ios-progress-text">
            PROGRESSION · {progress['completed']}/{progress['total']} ÉTAPES COMPLÉTÉES ({progress['percentage']}%)
        </div>
        <div class="ios-progress-bar-container">
            <div class="ios-progress-bar" style="width: {progress['percentage']}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    workflow_steps = db.get_service_workflow_steps(service_id)
    
    if not workflow_steps.empty:
        step_icons = {
            'INFOS FACTURATION': '💳',
            'ASSURANCE': '🛡️',
            'SIRET/SIREN': '🏢',
            'KBIS': '📋',
            'FICHE GMB LINK': '📍',
            'AVIS LINK': '⭐',
            'BUDGET/SEMAINE': '💰',
            'DATE DOCUMENT': '📄',
            'DATE LANCEMENT': '🚀'
        }
        
        main_steps = ['INFOS FACTURATION', 'ASSURANCE', 'SIRET/SIREN', 'KBIS', 
                     'FICHE GMB LINK', 'AVIS LINK', 'BUDGET/SEMAINE', 'DATE DOCUMENT', 'DATE LANCEMENT']
        
        st.markdown("<div class='ios-workflow-section'>", unsafe_allow_html=True)
        
        for main_step in main_steps:
            step_data = workflow_steps[workflow_steps['main_step'] == main_step]
            
            if not step_data.empty:
                for _, sub_step in step_data.iterrows():
                    is_completed = sub_step['completed'] == 1
                    card_class = "completed" if is_completed else ""
                    has_details = sub_step.get('notes') or sub_step.get('completed_at')
                    details_class = "has-details" if has_details else ""
                    
                    icon = step_icons.get(main_step, '📌')
                    
                    # Utiliser un conteneur Streamlit natif
                    with st.container():
                        # Marqueur pour le CSS
                        st.markdown(f'<div class="ios-workflow-card-marker {card_class} {details_class}"></div>', unsafe_allow_html=True)
                        
                        # Ligne de header : icône/texte à gauche, toggle/bouton à droite
                        header_left, header_right = st.columns([3, 1])
                        
                        with header_left:
                            st.markdown(f"""
                            <div class="ios-workflow-header">
                                <div class="ios-workflow-label-container">
                                    <div class="ios-step-icon">{icon}</div>
                                    <div class="ios-workflow-label">{main_step}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with header_right:
                            # Toggle et bouton dans des sous-colonnes
                            col_toggle, col_btn = st.columns([3, 1])
                            with col_toggle:
                                new_state = st.toggle(
                                    "Toggle",
                                    value=is_completed,
                                    key=f"service_step_{sub_step['id']}",
                                    label_visibility="collapsed"
                                )
                                
                                if new_state != is_completed:
                                    db.update_service_workflow_step(sub_step['id'], new_state)
                                    st.rerun()
                            
                            with col_btn:
                                if not st.session_state.get(f'edit_service_note_{sub_step["id"]}'):
                                    if st.button(f"📝", key=f"note_service_{sub_step['id']}", use_container_width=False):
                                        st.session_state[f'edit_service_note_{sub_step["id"]}'] = True
                                        st.rerun()
                        
                        # Afficher les détails (notes et date de complétion)
                        if has_details:
                            st.markdown('<div class="ios-workflow-details"><div class="ios-workflow-meta">', unsafe_allow_html=True)
                            
                            if sub_step.get('notes') and str(sub_step.get('notes')).strip():
                                st.markdown(f'<div class="ios-workflow-note">💬 {sub_step["notes"]}</div>', unsafe_allow_html=True)
                            
                            if sub_step.get('completed_at'):
                                st.markdown(f'<div class="ios-workflow-completed-date">✓ Complété le {sub_step["completed_at"]}</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div></div>', unsafe_allow_html=True)
                        
                        # Éditeur de note
                        if st.session_state.get(f'edit_service_note_{sub_step["id"]}'):
                            st.markdown("<div class='ios-note-editor'>", unsafe_allow_html=True)
                            note = st.text_area(
                                "Note",
                                value=sub_step.get('notes', ''),
                                key=f"note_service_input_{sub_step['id']}",
                                placeholder="Ajouter une note...",
                                height=80
                            )
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("💾 Enregistrer", key=f"save_service_note_{sub_step['id']}", use_container_width=True):
                                    db.update_service_workflow_step(sub_step['id'], sub_step['completed'] == 1, note)
                                    st.session_state[f'edit_service_note_{sub_step["id"]}'] = False
                                    st.rerun()
                            with col_b:
                                if st.button("✕ Annuler", key=f"cancel_service_note_{sub_step['id']}", use_container_width=True):
                                    st.session_state[f'edit_service_note_{sub_step["id"]}'] = False
                                    st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    if st.button("Fermer", use_container_width=True, type="primary"):
        st.session_state.show_workflow_service_id = None
        st.rerun()

if not st.session_state.user_logged_in:
    st.markdown("""
        <div style="text-align: center; margin-top: 120px; margin-bottom: 60px;">
            <h1 style="
                font-size: 56px; 
                margin-bottom: 20px; 
                background: linear-gradient(135deg, #A78BFA 0%, #EC4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 800;
            ">Connexion 👤</h1>
            <p class="subtitle" style="font-size: 22px; opacity: 0.8;">Qui êtes-vous ?</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='margin-bottom: 30px;'>", unsafe_allow_html=True)
        selected_user = st.selectbox(
            "Sélectionnez votre nom", 
            team_members, 
            key="temp_user",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("✨ Continuer", use_container_width=True, type="primary"):
            st.session_state.current_user = selected_user
            st.session_state.user_logged_in = True
            st.rerun()

elif st.session_state.app_mode is None:
    st.markdown("""
        <div style="text-align: center; margin-top: 60px; margin-bottom: 40px;">
            <h1 style="
                font-size: 52px; 
                margin-bottom: 16px; 
                background: linear-gradient(135deg, #A78BFA 0%, #EC4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 800;
            ">Bienvenue ! 👋</h1>
            <p class="subtitle" style="font-size: 20px; opacity: 0.8;">Choisissez votre mode de gestion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # CSS pour les cartes premium iOS style
    st.markdown(f"""
    <style>
    [data-testid="column"] {{
        overflow: visible !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        overflow: visible !important;
    }}
    
    /* Cartes Premium iOS Style */
    .ios-premium-card {{
        position: relative;
        background: linear-gradient(145deg, 
            rgba(255, 255, 255, 0.08) 0%, 
            rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 32px;
        padding: 48px 32px 32px 32px;
        min-height: 420px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        overflow: hidden;
        margin-bottom: 16px;
    }}
    
    .ios-premium-card:hover {{
        transform: translateY(-12px) scale(1.02);
        border-color: rgba(167, 139, 250, 0.4);
        box-shadow: 
            0 20px 60px rgba(167, 139, 250, 0.3),
            0 0 0 1px rgba(167, 139, 250, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }}
    
    .ios-premium-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(
            circle at 50% 0%,
            rgba(167, 139, 250, 0.15) 0%,
            transparent 60%
        );
        opacity: 0;
        transition: opacity 0.4s ease;
    }}
    
    .ios-premium-card:hover::before {{
        opacity: 1;
    }}
    
    .card-glow {{
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle,
            rgba(167, 139, 250, 0.4) 0%,
            transparent 70%
        );
        opacity: 0;
        transition: opacity 0.6s ease;
        pointer-events: none;
    }}
    
    .ios-premium-card:hover .card-glow {{
        opacity: 0.6;
        animation: glow-pulse 2s ease-in-out infinite;
    }}
    
    @keyframes glow-pulse {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .card-content {{
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }}
    
    .icon-container {{
        width: 160px;
        height: 160px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .ios-premium-card:hover .icon-container {{
        transform: scale(1.1) rotateY(10deg);
    }}
    
    .card-icon {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.3));
        transition: filter 0.4s ease;
    }}
    
    .ios-premium-card:hover .card-icon {{
        filter: drop-shadow(0 12px 32px rgba(167, 139, 250, 0.6));
    }}
    
    .card-title {{
        font-size: 28px;
        font-weight: 700;
        color: #F5F5F7;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #F5F5F7 0%, #E8E9ED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .card-subtitle {{
        font-size: 16px;
        color: rgba(245, 245, 247, 0.7);
        line-height: 1.6;
        max-width: 280px;
        margin: 0 auto 24px auto;
    }}
    
    /* Effet 3D différent pour chaque carte */
    #tasks-card:hover {{
        transform: translateY(-12px) scale(1.02) perspective(1000px) rotateY(-2deg);
    }}
    
    #fiches-card:hover {{
        transform: translateY(-12px) scale(1.02) perspective(1000px) rotateY(2deg);
    }}
    
    /* Boutons Accéder Premium Style */
    [data-testid="column"] > div > div > .stButton > button {{
        background: linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 32px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 4px 16px rgba(167, 139, 250, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        opacity: 1 !important;
        position: relative !important;
        pointer-events: all !important;
        margin-top: -16px !important;
    }}
    
    [data-testid="column"] > div > div > .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 
            0 6px 24px rgba(167, 139, 250, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    }}
    
    [data-testid="column"] > div > div > .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* Style pour la checkbox */
    .stCheckbox {{
        opacity: 0.6;
    }}
    
    .stCheckbox label {{
        color: rgba(245, 245, 247, 0.7) !important;
        font-size: 14px !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    
    with col2:
        col_a, col_b = st.columns(2, gap="large")
        
        with col_a:
            st.markdown(f"""
                <div class="ios-premium-card" id="tasks-card">
                    <div class="card-glow"></div>
                    <div class="card-content">
                        <div class="icon-container">
                            <img src="data:image/png;base64,{icon_tasks_base64}" alt="Tasks" class="card-icon" />
                        </div>
                        <h2 class="card-title">Gestion de<br>Tâches</h2>
                        <p class="card-subtitle">Organisez et suivez les tâches de votre équipe</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✦ Accéder", key="btn_tasks_access", use_container_width=True, type="primary"):
                st.session_state.app_mode = "tasks"
                st.rerun()
        
        with col_b:
            st.markdown(f"""
                <div class="ios-premium-card" id="fiches-card">
                    <div class="card-glow"></div>
                    <div class="card-content">
                        <div class="icon-container">
                            <img src="data:image/png;base64,{icon_fiches_base64}" alt="Fiches" class="card-icon" />
                        </div>
                        <h2 class="card-title">Gestion de<br>Fiches</h2>
                        <p class="card-subtitle">Gérez vos fiches Google et services locaux</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✦ Accéder", key="btn_fiches_access", use_container_width=True, type="primary"):
                st.session_state.app_mode = "listings"
                st.rerun()
        
        st.markdown("<div style='margin-top: 24px; text-align: center;'>", unsafe_allow_html=True)
        st.checkbox("💾 Toutes les données sont sauvegardées automatiquement", value=True, disabled=True, key="auto_save_info")
        st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown(f"""
            <div style='margin-top: 8px; text-align: center; padding: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; border: 1px solid rgba(167, 139, 250, 0.3);'>
                <p style='margin: 0; font-size: 14px; opacity: 0.7;'>Connecté en tant que</p>
                <p style='margin: 0; font-size: 16px; font-weight: 600; color: {team_colors[st.session_state.current_user]};'>👤 {st.session_state.current_user}</p>
            </div>
        """, unsafe_allow_html=True)
    
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
                <div class="icon-circle icon-urgent">🚨</div>
                <div class="subtitle">Tâches urgentes</div>
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚨 Urgences", "➕ Nouvelle Tâche", "👥 Par Personne", "📊 Toutes les Tâches", "📜 Historique"])
    
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
        st.markdown("""
            <div style="margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 48px; height: 48px; border-radius: 14px; background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35);">➕</div>
                    <h2 style="margin: 0; font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #E8E9ED 0%, #A78BFA 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Ajouter une Nouvelle Tâche</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            div[data-testid="stForm"] {
                background: linear-gradient(145deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
                border-radius: 24px !important;
                padding: 36px !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        has_deadline = st.checkbox("📅 Ajouter une date d'échéance", key="add_deadline_checkbox")
        
        with st.form("new_task_form", clear_on_submit=True):
            title = st.text_input("Titre de la tâche *", placeholder="Ex: Finaliser le rapport mensuel")
            client_name = st.text_input("Nom du client", placeholder="Ex: Entreprise ABC")
            description = st.text_area("Description", placeholder="Décrivez la tâche en détail...")
            
            col1, col2 = st.columns(2)
            with col1:
                assigned_to = st.selectbox("Assigner à *", team_members, index=0)
            
            with col2:
                priority = st.selectbox("Priorité *", ["Normale", "Urgente"], index=0)
            
            deadline = None
            if has_deadline:
                deadline = st.date_input("Date d'échéance")
            
            submitted = st.form_submit_button("➕ Ajouter la tâche", use_container_width=True)
            
            if submitted:
                if title and assigned_to:
                    deadline_str = deadline.strftime('%Y-%m-%d') if has_deadline and deadline else None
                    db.add_task(title, description, assigned_to, priority, client_name, deadline_str)
                    st.success(f"✅ Tâche ajoutée avec succès et assignée à {assigned_to} !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Le titre et l'assignation sont obligatoires")
    
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
                    default=["À faire", "En cours"],
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
                all_columns = ['Ordre', 'ID', 'Titre', 'Client', 'Description', 'Priorité', 'Statut', 'Date d\'échéance', 'Créée le', 'Modifiée le', 'Modifié par', 'Assigné à']
                selected_columns = st.multiselect(
                    "📋 Colonnes à afficher",
                    all_columns,
                    default=['Ordre', 'Titre', 'Client', 'Priorité', 'Statut', 'Date d\'échéance', 'Assigné à'],
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
            
            # Choix de vue
            view_mode = st.radio(
                "Mode d'affichage",
                ["📋 Tableau", "🔀 Réorganiser"],
                horizontal=True,
                key="view_mode_person"
            )
            
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
                if has_active_filters and view_mode == "🔀 Réorganiser":
                    st.warning("⚠️ La réorganisation des tâches n'est pas disponible lorsque des filtres sont actifs. Affichez toutes les tâches pour pouvoir réorganiser.")
                
                # Ajouter les numéros de tâche par personne
                filtered_person_tasks = add_person_task_numbers(filtered_person_tasks)
                
                if view_mode == "🔀 Réorganiser" and not has_active_filters:
                    st.info("💡 Modifiez le numéro directement ou utilisez les boutons ↑ et ↓ pour réorganiser les tâches")
                    
                    # Initialiser l'état de session pour les tâches si nécessaire
                    if 'reorder_tasks' not in st.session_state or st.session_state.get('reorder_person') != selected_person:
                        sorted_tasks = filtered_person_tasks.sort_values('person_task_number')
                        st.session_state.reorder_tasks = sorted_tasks.to_dict('records')
                        st.session_state.reorder_person = selected_person
                        st.session_state.task_moving_id = None
                        st.session_state.task_animation_trigger = 0
                    
                    tasks_list = st.session_state.reorder_tasks
                    
                    # Utiliser un trigger pour savoir si on doit animer
                    animation_trigger = st.session_state.get('task_animation_trigger', 0)
                    moving_task_id = st.session_state.get('task_moving_id') if animation_trigger > 0 else None
                    moving_direction = st.session_state.get('task_moving_direction') if animation_trigger > 0 else None
                    
                    # Décrémenter le trigger pour désactiver l'animation au prochain rendu
                    if animation_trigger > 0:
                        st.session_state.task_animation_trigger = 0
                    
                    # Container avec scroll pour les tâches
                    st.markdown("""
                        <style>
                        .task-list-wrapper {
                            max-height: 60vh;
                            overflow-y: auto;
                            padding: 4px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Conteneur scrollable pour la liste
                    st.markdown('<div class="task-list-wrapper">', unsafe_allow_html=True)
                    
                    # Afficher les tâches avec boutons de réorganisation
                    for idx, task in enumerate(tasks_list):
                        priority_icon = "🔴" if task['priority'] == "Urgente" else "🟢"
                        status_icon = "✅" if task['status'] == "Terminée" else "⏳" if task['status'] == "En cours" else "📋"
                        client_text = f" - {task['client_name']}" if task.get('client_name') else ""
                        task_id = int(task['_original_id'])
                        
                        # Déterminer si cette tâche est en train de bouger
                        animation_class = ""
                        if moving_task_id == task_id and moving_direction:
                            animation_class = f" task-moving-{moving_direction}"
                        
                        # Utiliser des colonnes pour l'affichage
                        col_num, col_content, col_up, col_down = st.columns([0.08, 0.77, 0.075, 0.075])
                        
                        with col_num:
                            # Sélecteur pour modifier l'ordre directement
                            new_position = st.selectbox(
                                "Ordre",
                                options=list(range(1, len(tasks_list) + 1)),
                                index=idx,
                                key=f"pos_{idx}_{task_id}",
                                label_visibility="collapsed"
                            )
                            
                            # Si la position a changé, réorganiser la liste
                            if new_position != idx + 1:
                                # Retirer la tâche de sa position actuelle
                                task_to_move = tasks_list.pop(idx)
                                # Insérer à la nouvelle position (ajuster pour l'index 0)
                                tasks_list.insert(new_position - 1, task_to_move)
                                st.session_state.reorder_tasks = tasks_list
                                st.rerun()
                        
                        with col_content:
                            # Créer une carte compacte avec HTML/CSS personnalisé
                            task_html = f"""
                            <div class="task-reorder-item{animation_class}">
                                <div class="task-reorder-content">
                                    <span>{priority_icon}</span>
                                    <span>{status_icon}</span>
                                    <span>{escape_html(task['title'])}{escape_html(client_text)}</span>
                                </div>
                            </div>
                            """
                            st.markdown(task_html, unsafe_allow_html=True)
                        
                        with col_up:
                            if idx > 0:
                                if st.button("↑", key=f"up_{idx}_{task_id}", help="Monter"):
                                    # Marquer l'animation avec l'ID de la tâche
                                    st.session_state.task_moving_id = task_id
                                    st.session_state.task_moving_direction = 'up'
                                    st.session_state.task_animation_trigger = 1
                                    # Échanger avec l'élément précédent
                                    tasks_list[idx], tasks_list[idx-1] = tasks_list[idx-1], tasks_list[idx]
                                    st.session_state.reorder_tasks = tasks_list
                                    st.rerun()
                        
                        with col_down:
                            if idx < len(tasks_list) - 1:
                                if st.button("↓", key=f"down_{idx}_{task_id}", help="Descendre"):
                                    # Marquer l'animation avec l'ID de la tâche
                                    st.session_state.task_moving_id = task_id
                                    st.session_state.task_moving_direction = 'down'
                                    st.session_state.task_animation_trigger = 1
                                    # Échanger avec l'élément suivant
                                    tasks_list[idx], tasks_list[idx+1] = tasks_list[idx+1], tasks_list[idx]
                                    st.session_state.reorder_tasks = tasks_list
                                    st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Bouton pour enregistrer l'ordre
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("💾 Enregistrer l'ordre", use_container_width=True, type="primary"):
                            new_order_map = {}
                            for new_idx, task in enumerate(tasks_list):
                                task_id = int(task['_original_id'])
                                new_order_map[task_id] = new_idx + 1
                            
                            db.reorder_tasks(selected_person, new_order_map)
                            st.success("✅ Ordre des tâches enregistré avec succès !")
                            # Réinitialiser l'état
                            if 'reorder_tasks' in st.session_state:
                                del st.session_state.reorder_tasks
                            if 'reorder_person' in st.session_state:
                                del st.session_state.reorder_person
                            st.rerun()
                    
                    with col2:
                        if st.button("🔄 Réinitialiser", use_container_width=True):
                            # Réinitialiser l'état
                            if 'reorder_tasks' in st.session_state:
                                del st.session_state.reorder_tasks
                            if 'reorder_person' in st.session_state:
                                del st.session_state.reorder_person
                            st.rerun()
                
                else:
                    # Mode Tableau
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
                        'deadline': 'Date d\'échéance',
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
                    if 'Date d\'échéance' in selected_columns:
                        column_config["Date d'échéance"] = st.column_config.TextColumn("Date d'échéance", width="medium")
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
                        
                        # Première passe: réorganiser complètement l'ordre des tâches basé sur les valeurs "Ordre" saisies
                        if 'Ordre' in edited_df.columns and not original_df.empty:
                            # Créer un DataFrame temporaire avec l'ordre saisi et les IDs originaux
                            reorder_data = []
                            for idx in range(len(edited_df)):
                                original_task = original_df.iloc[idx] if idx < len(original_df) else None
                                if original_task is not None and '_original_id' in original_task:
                                    task_id = int(original_task['_original_id'])
                                    original_order = int(original_df.iloc[idx]['Ordre']) if 'Ordre' in original_df.columns else idx + 1
                                    order_value = int(edited_df.iloc[idx]['Ordre'])
                                    reorder_data.append({
                                        'task_id': task_id, 
                                        'new_order': order_value,
                                        'original_order': original_order,
                                        'original_idx': idx
                                    })
                            
                            if reorder_data:
                                # Trier par new_order, puis par original_idx pour gérer les doublons
                                reorder_df = pd.DataFrame(reorder_data)
                                reorder_df = reorder_df.sort_values(['new_order', 'original_idx'])
                                
                                # Réassigner des valeurs contiguës (1, 2, 3, etc.)
                                new_order_map = {}
                                for idx, row in enumerate(reorder_df.itertuples()):
                                    new_order_map[row.task_id] = idx + 1
                                
                                # Vérifier s'il y a vraiment eu un changement d'ordre
                                order_changed = False
                                for idx in range(len(original_df)):
                                    task_id = int(original_df.iloc[idx]['_original_id'])
                                    original_order = int(original_df.iloc[idx]['Ordre']) if 'Ordre' in original_df.columns else idx + 1
                                    if task_id in new_order_map and new_order_map[task_id] != original_order:
                                        order_changed = True
                                        break
                                
                                # Appliquer le réordonnancement seulement si l'ordre a changé
                                if order_changed:
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
    
    with tab5:
        st.markdown("### 📜 Historique des Tâches Terminées")
        
        # Récupérer toutes les tâches terminées
        completed_tasks = all_tasks[all_tasks['status'] == 'Terminée']
        
        if completed_tasks.empty:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 48px;">
                    <div style="font-size: 64px; margin-bottom: 16px;">✨</div>
                    <h3>Aucune tâche terminée</h3>
                    <p class="subtitle">Les tâches complétées apparaîtront ici</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Filtres pour l'historique
            col1, col2 = st.columns(2)
            
            with col1:
                filter_history_person = st.multiselect(
                    "Filtrer par personne",
                    team_members,
                    default=team_members,
                    key="filter_history_person"
                )
            
            with col2:
                search_history_client = st.text_input(
                    "🔍 Rechercher un client",
                    placeholder="Nom du client...",
                    key="search_history_client"
                )
            
            # Appliquer les filtres
            filtered_completed = completed_tasks[completed_tasks['assigned_to'].isin(filter_history_person)]
            
            if search_history_client:
                filtered_completed = filtered_completed[
                    filtered_completed['client_name'].str.contains(search_history_client, case=False, na=False)
                ]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_completed.empty:
                st.info("Aucune tâche terminée ne correspond aux filtres")
            else:
                st.markdown(f"**{len(filtered_completed)} tâche(s) terminée(s)**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Trier par date de modification (les plus récentes en premier)
                filtered_completed = filtered_completed.sort_values('updated_at', ascending=False)
                
                for _, task in filtered_completed.iterrows():
                    priority_icon = "🔴" if task['priority'] == "Urgente" else "🟢"
                    person_color = team_colors.get(str(task['assigned_to']), '#7A9A7E')
                    
                    html_parts = ['<div class="card" style="opacity: 0.8;">']
                    html_parts.append('<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">')
                    html_parts.append('<div style="flex: 1;">')
                    html_parts.append(f'<h2 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 700; color: #E8E9ED;">✅ {escape_html(task["title"])}</h2>')
                    html_parts.append('<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">')
                    
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
                    
                    # Priority badge
                    html_parts.append(f'<span class="status-badge" style="background: rgba(34, 197, 94, 0.15); color: #4ADE80;">{priority_icon} {escape_html(task["priority"])}</span>')
                    
                    html_parts.append('</div></div>')
                    
                    # Dates section
                    html_parts.append('<div style="display: flex; gap: 6px; flex-wrap: wrap; flex-direction: column; align-items: end;">')
                    html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px;">Créée le {escape_html(task["created_at"])}</span>')
                    html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #4ADE80;">✅ Terminée le {escape_html(task["updated_at"])}</span>')
                    
                    # Modified by badge
                    if task.get('last_modified_by') and pd.notna(task.get('last_modified_by')):
                        html_parts.append(f'<span class="subtitle" style="white-space: nowrap; font-size: 11px; color: #A78BFA;">✏️ Par {escape_html(task["last_modified_by"])}</span>')
                    
                    html_parts.append('</div></div>')
                    
                    # Description
                    if task.get('description') and str(task.get('description')).strip():
                        html_parts.append(f'<p style="color: #9CA3AF; margin: 8px 0 0 0; font-size: 13px;">{escape_html(task["description"])}</p>')
                    
                    html_parts.append('</div>')
                    
                    st.markdown(''.join(html_parts), unsafe_allow_html=True)

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
        st.markdown(f"""
            <div style='margin-top: 8px; text-align: center; padding: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; border: 1px solid rgba(167, 139, 250, 0.3);'>
                <p style='margin: 0; font-size: 14px; opacity: 0.7;'>Connecté en tant que</p>
                <p style='margin: 0; font-size: 16px; font-weight: 600; color: {team_colors[st.session_state.current_user]};'>👤 {st.session_state.current_user}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.app_mode = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    current_user = st.session_state.current_user
    
    st.markdown("### 🏢 Gestion des Fiches Google & Services Locaux")
    
    subtab1, subtab2, subtab3 = st.tabs(["📍 Fiches Google", "🛠️ Services Locaux", "📊 Tableau de bord"])
    
    with subtab1:
            st.markdown("#### 📍 Fiches Google My Business")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("##### ➕ Ajouter une nouvelle fiche")
                
                with st.form("new_google_listing_form", clear_on_submit=True):
                    business_name = st.text_input("Nom de l'entreprise *", placeholder="Ex: Entreprise Dubois")
                    client_name = st.text_input("Nom du client *", placeholder="Ex: M. Dupont")
                    
                    category_choice = st.selectbox("Catégorie *", [
                        "Couvreur", "Élagueur", "Paysagiste", "Nettoyeur toiture", "Tapissier", "Autre"
                    ])
                    
                    custom_category = st.text_input("Si Autre, précisez la catégorie", placeholder="Ex: Plombier, Électricien, Maçon...")
                    
                    description = st.text_area("Description", placeholder="Décrivez votre entreprise...")
                    google_listing_url = st.text_input("URL de la fiche Google", placeholder="https://g.page/...")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    create_local_service = st.checkbox("✅ Gestion Local Services à faire", value=False, help="Créer automatiquement une entrée dans Services Locaux")
                    
                    submitted_listing = st.form_submit_button("➕ Ajouter la fiche", use_container_width=True)
                    
                    if submitted_listing:
                        if business_name and client_name:
                            # Déterminer la catégorie finale
                            if category_choice == "Autre" and custom_category:
                                final_category = custom_category
                            elif category_choice == "Autre":
                                final_category = "Autre"
                            else:
                                final_category = category_choice
                            
                            db.add_google_listing(
                                business_name, "", "", "", final_category, 
                                description, google_listing_url, current_user, client_name
                            )
                            
                            if create_local_service:
                                db.add_local_service(
                                    service_name=business_name,
                                    service_type=final_category,
                                    provider=client_name,
                                    area_coverage="",
                                    phone="",
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
                            st.session_state.show_workflow_service_id = None
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
                            st.session_state.show_workflow_listing_id = None
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_service_{service['id']}", help="Supprimer"):
                            db.delete_local_service(service['id'])
                            st.rerun()
    
    with subtab3:
            st.markdown("#### 📊 Tableau de bord récapitulatif")
            
            # Filtres iOS Premium
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(30, 33, 42, 0.6) 0%, rgba(26, 29, 41, 0.6) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 16px;
                    padding: 20px;
                    margin-bottom: 24px;
                    backdrop-filter: blur(20px);
                ">
                    <h3 style="margin: 0 0 16px 0; color: #F5F5F7; font-size: 17px; font-weight: 600;">🔍 Filtres</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filter_type = st.multiselect(
                    "Type",
                    ["Fiches Google", "Services Locaux"],
                    default=["Fiches Google", "Services Locaux"],
                    key="dashboard_filter_type"
                )
            
            with col_f2:
                filter_status = st.multiselect(
                    "Statut progression",
                    ["À faire", "En cours", "Terminé"],
                    default=["À faire", "En cours", "Terminé"],
                    key="dashboard_filter_status"
                )
            
            with col_f3:
                all_listings = db.get_all_google_listings()
                all_services = db.get_all_local_services()
                all_categories = set()
                
                if not all_listings.empty:
                    all_categories.update(all_listings['category'].dropna().unique())
                if not all_services.empty:
                    all_categories.update(all_services['service_type'].dropna().unique())
                
                filter_category = st.multiselect(
                    "Catégorie",
                    sorted(list(all_categories)) if all_categories else ["Aucune"],
                    default=sorted(list(all_categories)) if all_categories else [],
                    key="dashboard_filter_category"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Collecter toutes les données
            dashboard_data = []
            
            if "Fiches Google" in filter_type:
                all_listings = db.get_all_google_listings()
                if not all_listings.empty:
                    for _, listing in all_listings.iterrows():
                        progress = db.get_workflow_progress(listing['id'])
                        status = get_status_from_progress(progress['percentage'])
                        
                        if status in filter_status and (not filter_category or listing.get('category') in filter_category):
                            dashboard_data.append({
                                'type': 'Fiche Google',
                                'nom': listing['business_name'],
                                'client': listing.get('client_name', 'N/A'),
                                'categorie': listing.get('category', 'N/A'),
                                'progression': progress['percentage'],
                                'etapes': f"{progress['completed']}/{progress['total']}",
                                'statut': status,
                                'id': listing['id'],
                                'data_type': 'listing'
                            })
            
            if "Services Locaux" in filter_type:
                all_services = db.get_all_local_services()
                if not all_services.empty:
                    for _, service in all_services.iterrows():
                        progress = db.get_service_workflow_progress(service['id'])
                        status = get_status_from_progress(progress['percentage'])
                        
                        if status in filter_status and (not filter_category or service.get('service_type') in filter_category):
                            dashboard_data.append({
                                'type': 'Service Local',
                                'nom': service['service_name'],
                                'client': service.get('provider', 'N/A'),
                                'categorie': service.get('service_type', 'N/A'),
                                'progression': progress['percentage'],
                                'etapes': f"{progress['completed']}/{progress['total']}",
                                'statut': status,
                                'id': service['id'],
                                'data_type': 'service'
                            })
            
            # Afficher les résultats
            if not dashboard_data:
                st.markdown("""
                    <div class="card" style="text-align: center; padding: 48px;">
                        <div style="font-size: 64px; margin-bottom: 16px;">📊</div>
                        <h3>Aucune donnée à afficher</h3>
                        <p class="subtitle">Ajustez vos filtres ou ajoutez des fiches/services</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Statistiques globales
                total_items = len(dashboard_data)
                total_completed = len([d for d in dashboard_data if d['statut'] == 'Terminé'])
                total_in_progress = len([d for d in dashboard_data if d['statut'] == 'En cours'])
                total_todo = len([d for d in dashboard_data if d['statut'] == 'À faire'])
                avg_progress = sum(d['progression'] for d in dashboard_data) / total_items if total_items > 0 else 0
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.1) 100%);
                            border: 1px solid rgba(139, 92, 246, 0.3);
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="color: #A78BFA; font-size: 14px; font-weight: 500; margin-bottom: 8px;">Total</div>
                            <div style="color: #F5F5F7; font-size: 36px; font-weight: 700;">{total_items}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_s2:
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
                            border: 1px solid rgba(16, 185, 129, 0.3);
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="color: #10B981; font-size: 14px; font-weight: 500; margin-bottom: 8px;">Terminé</div>
                            <div style="color: #F5F5F7; font-size: 36px; font-weight: 700;">{total_completed}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_s3:
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
                            border: 1px solid rgba(59, 130, 246, 0.3);
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="color: #3B82F6; font-size: 14px; font-weight: 500; margin-bottom: 8px;">En cours</div>
                            <div style="color: #F5F5F7; font-size: 36px; font-weight: 700;">{total_in_progress}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_s4:
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(251, 146, 60, 0.15) 0%, rgba(249, 115, 22, 0.1) 100%);
                            border: 1px solid rgba(251, 146, 60, 0.3);
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="color: #FB923C; font-size: 14px; font-weight: 500; margin-bottom: 8px;">À faire</div>
                            <div style="color: #F5F5F7; font-size: 36px; font-weight: 700;">{total_todo}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Tableau avec st.dataframe
                import pandas as pd
                
                # Style CSS pour agrandir les cellules du tableau
                st.markdown("""
                <style>
                [data-testid="stDataFrame"] {
                    font-size: 15px !important;
                }
                [data-testid="stDataFrame"] th {
                    padding: 20px 16px !important;
                    font-size: 14px !important;
                    background: rgba(139, 92, 246, 0.15) !important;
                    color: #A78BFA !important;
                }
                [data-testid="stDataFrame"] td {
                    padding: 18px 16px !important;
                    font-size: 15px !important;
                }
                [data-testid="stDataFrame"] tbody tr:hover {
                    background: rgba(139, 92, 246, 0.1) !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Préparer les données pour le tableau
                table_data = []
                for item in sorted(dashboard_data, key=lambda x: x['progression'], reverse=False):
                    icon = '📍' if item['type'] == 'Fiche Google' else '🛠️'
                    table_data.append({
                        'ICÔNE': icon,
                        'TYPE': item['type'],
                        'NOM': item['nom'],
                        'CLIENT': item['client'],
                        'CATÉGORIE': item['categorie'],
                        'PROGRESSION': f"{item['progression']}%",
                        'ÉTAPES': item['etapes'],
                        'STATUT': item['statut'],
                    })
                
                df_dashboard = pd.DataFrame(table_data)
                
                # Afficher le dataframe
                st.dataframe(
                    df_dashboard,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ICÔNE": st.column_config.TextColumn("ICÔNE", width="small"),
                        "TYPE": st.column_config.TextColumn("TYPE", width="small"),
                        "NOM": st.column_config.TextColumn("NOM", width="medium"),
                        "CLIENT": st.column_config.TextColumn("CLIENT", width="small"),
                        "CATÉGORIE": st.column_config.TextColumn("CATÉGORIE", width="small"),
                        "PROGRESSION": st.column_config.TextColumn("PROGRESSION", width="small"),
                        "ÉTAPES": st.column_config.TextColumn("ÉTAPES", width="small"),
                        "STATUT": st.column_config.TextColumn("STATUT", width="small"),
                    }
                )
                
                # Boutons d'action en dessous du tableau
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**💡 Cliquez sur un bouton ci-dessous pour voir le workflow :**")
                
                cols = st.columns(min(len(dashboard_data), 4))
                for idx, item in enumerate(sorted(dashboard_data, key=lambda x: x['progression'], reverse=False)):
                    with cols[idx % 4]:
                        if st.button(f"📊 {item['nom'][:20]}...", key=f"dash_btn_{item['data_type']}_{item['id']}", use_container_width=True):
                            if item['data_type'] == 'listing':
                                st.session_state.show_workflow_listing_id = item['id']
                                st.session_state.show_workflow_service_id = None
                            else:
                                st.session_state.show_workflow_service_id = item['id']
                                st.session_state.show_workflow_listing_id = None
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
