import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Bons de Travail",
    page_icon="📋",
    layout="wide"
)

# Constantes
DATA_FILE = "work_orders.xlsx"
IMAGE_DIR = "work_images"

# Créer le dossier pour les images s'il n'existe pas
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Liste prédéfinie des installations impactées
INSTALLATIONS = [
    "éclairage",
    "climatisation",
    "toilettes lavabo vestiaires",
    "groupe électrogène",
    "Autre"
]

# Statuts possibles
STATUS_OPTIONS = ["En cours", "Terminé", "En attente", "Annulé"]

# ==================== Fonctions de gestion des données ====================
@st.cache_data
def load_data():
    """Charge les données depuis le fichier Excel."""
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE, dtype={"Numéro de Bon de Travail": str})
        date_cols = ["Date d'Émission", "Date de Réception du Bon de Travail", "Date de Livraison des Travaux"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        required_cols = [
            "Numéro de Bon de Travail", "Date d'Émission", "Émetteur", "Destinataire",
            "Direction / Département / Division", "Service / Site / Gare",
            "Installation Impactée", "Description du Travail Demandé",
            "Nom du Responsable", "Date de Réception du Bon de Travail",
            "Date de Livraison des Travaux", "Statut"
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        return df
    else:
        columns = [
            "Numéro de Bon de Travail", "Date d'Émission", "Émetteur", "Destinataire",
            "Direction / Département / Division", "Service / Site / Gare",
            "Installation Impactée", "Description du Travail Demandé",
            "Nom du Responsable", "Date de Réception du Bon de Travail",
            "Date de Livraison des Travaux", "Statut"
        ]
        return pd.DataFrame(columns=columns)

def save_data(df):
    """Sauvegarde le DataFrame dans le fichier Excel."""
    df.to_excel(DATA_FILE, index=False)
    st.cache_data.clear()

def add_work_order(df, new_data):
    """Ajoute un nouveau bon de travail."""
    if new_data["Numéro de Bon de Travail"] in df["Numéro de Bon de Travail"].values:
        st.error("Ce numéro de bon de travail existe déjà.")
        return df
    new_row = pd.DataFrame([new_data])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return df

def update_work_order(df, num_bon, updated_data):
    """Met à jour un bon de travail existant."""
    idx = df[df["Numéro de Bon de Travail"] == num_bon].index
    if len(idx) > 0:
        for key, value in updated_data.items():
            df.loc[idx[0], key] = value
        save_data(df)
    return df

def save_image(work_order_number, uploaded_file):
    """Sauvegarde l'image téléversée pour un bon de travail."""
    if uploaded_file is not None:
        ext = uploaded_file.name.split('.')[-1]
        filename = f"{work_order_number}.{ext}"
        filepath = os.path.join(IMAGE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filepath
    return None

def get_image_path(work_order_number):
    """Récupère le chemin de l'image associée à un bon de travail."""
    for ext in ['png', 'jpg', 'jpeg', 'gif']:
        filepath = os.path.join(IMAGE_DIR, f"{work_order_number}.{ext}")
        if os.path.exists(filepath):
            return filepath
    return None

# ==================== Interface Streamlit ====================
st.title("📋 Gestion des Bons de Travail")
st.markdown("---")

# Chargement initial des données
df = load_data()

# Création des onglets
tab1, tab2, tab3 = st.tabs(["📋 Gestion des Bons", "📊 Statistiques & Commentaire", "📑 Tableau complet"])

# ==================== Onglet 1 : Gestion des Bons ====================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Sélectionner un Bon")
        if not df.empty:
            bon_list = df["Numéro de Bon de Travail"].tolist()
            selected_bon = st.selectbox("Choisissez un numéro", bon_list, key="select_bon")
        else:
            st.info("Aucun bon de travail enregistré.")
            selected_bon = None
        
        st.markdown("---")
        st.subheader("➕ Ajouter un nouveau bon")
        with st.form("add_form"):
            new_num = st.text_input("Numéro de Bon de Travail")
            new_date_emission = st.date_input("Date d'Émission", value=datetime.today())
            new_emetteur = st.text_input("Émetteur")
            new_destinataire = st.text_input("Destinataire")
            new_direction = st.text_input("Direction / Département / Division")
            new_service = st.text_input("Service / Site / Gare")
            new_install = st.selectbox("Installation Impactée", INSTALLATIONS)
            new_desc = st.text_area("Description du Travail Demandé")
            new_resp = st.text_input("Nom du Responsable")
            new_date_recep = st.date_input("Date de Réception du Bon de Travail", value=datetime.today())
            new_date_livr = st.date_input("Date de Livraison des Travaux", value=None)
            new_status = st.selectbox("Statut", STATUS_OPTIONS)
            submitted = st.form_submit_button("Ajouter", width='stretch')
            
            if submitted:
                if new_num and new_num not in df["Numéro de Bon de Travail"].values:
                    new_data = {
                        "Numéro de Bon de Travail": new_num,
                        "Date d'Émission": new_date_emission,
                        "Émetteur": new_emetteur,
                        "Destinataire": new_destinataire,
                        "Direction / Département / Division": new_direction,
                        "Service / Site / Gare": new_service,
                        "Installation Impactée": new_install,
                        "Description du Travail Demandé": new_desc,
                        "Nom du Responsable": new_resp,
                        "Date de Réception du Bon de Travail": new_date_recep,
                        "Date de Livraison des Travaux": new_date_livr if new_date_livr else None,
                        "Statut": new_status
                    }
                    df = add_work_order(df, new_data)
                    st.success(f"Bon {new_num} ajouté avec succès !")
                    st.rerun()
                else:
                    st.error("Numéro invalide ou déjà existant.")
    
    with col2:
        st.subheader("Détails et modification")
        if selected_bon is not None:
            bon_data = df[df["Numéro de Bon de Travail"] == selected_bon].iloc[0]
            
            with st.form("edit_form"):
                edit_num = st.text_input("Numéro", value=bon_data["Numéro de Bon de Travail"], disabled=True)
                edit_date_emission = st.date_input("Date d'Émission", value=bon_data["Date d'Émission"])
                edit_emetteur = st.text_input("Émetteur", value=bon_data["Émetteur"] if pd.notna(bon_data["Émetteur"]) else "")
                edit_destinataire = st.text_input("Destinataire", value=bon_data["Destinataire"] if pd.notna(bon_data["Destinataire"]) else "")
                edit_direction = st.text_input("Direction", value=bon_data["Direction / Département / Division"] if pd.notna(bon_data["Direction / Département / Division"]) else "")
                edit_service = st.text_input("Service / Site / Gare", value=bon_data["Service / Site / Gare"] if pd.notna(bon_data["Service / Site / Gare"]) else "")
                edit_install = st.selectbox("Installation Impactée", INSTALLATIONS, index=INSTALLATIONS.index(bon_data["Installation Impactée"]) if bon_data["Installation Impactée"] in INSTALLATIONS else 0)
                edit_desc = st.text_area("Description", value=bon_data["Description du Travail Demandé"] if pd.notna(bon_data["Description du Travail Demandé"]) else "")
                edit_resp = st.text_input("Responsable", value=bon_data["Nom du Responsable"] if pd.notna(bon_data["Nom du Responsable"]) else "")
                edit_date_recep = st.date_input("Date de Réception", value=bon_data["Date de Réception du Bon de Travail"] if pd.notna(bon_data["Date de Réception du Bon de Travail"]) else datetime.today())
                edit_date_livr = st.date_input("Date de Livraison", value=bon_data["Date de Livraison des Travaux"] if pd.notna(bon_data["Date de Livraison des Travaux"]) else None)
                edit_status = st.selectbox("Statut", STATUS_OPTIONS, index=STATUS_OPTIONS.index(bon_data["Statut"]) if bon_data["Statut"] in STATUS_OPTIONS else 0)
                
                update_clicked = st.form_submit_button("✅ Mettre à jour", width='stretch')
                
                if update_clicked:
                    updated = {
                        "Date d'Émission": edit_date_emission,
                        "Émetteur": edit_emetteur,
                        "Destinataire": edit_destinataire,
                        "Direction / Département / Division": edit_direction,
                        "Service / Site / Gare": edit_service,
                        "Installation Impactée": edit_install,
                        "Description du Travail Demandé": edit_desc,
                        "Nom du Responsable": edit_resp,
                        "Date de Réception du Bon de Travail": edit_date_recep,
                        "Date de Livraison des Travaux": edit_date_livr if edit_date_livr else None,
                        "Statut": edit_status
                    }
                    df = update_work_order(df, selected_bon, updated)
                    st.success("Bon mis à jour !")
                    st.rerun()
            
            st.markdown("---")
            st.subheader("📸 Image du Bon de Travail")
            uploaded_image = st.file_uploader("Téléversez une image (PNG, JPG, JPEG)", type=['png', 'jpg', 'jpeg'], key=f"upload_{selected_bon}")
            if uploaded_image is not None:
                if save_image(selected_bon, uploaded_image):
                    st.success("Image enregistrée avec succès !")
                else:
                    st.error("Erreur lors de l'enregistrement.")
            
            image_path = get_image_path(selected_bon)
            if image_path:
                st.image(image_path, caption=f"Bon {selected_bon}", width='stretch')
            else:
                st.info("Aucune image associée à ce bon.")

# ==================== Onglet 2 : Statistiques & Commentaire ====================
with tab2:
    if not df.empty:
        st.subheader("📊 Fréquence des interventions par type d'installation")
        install_counts = df["Installation Impactée"].value_counts().reset_index()
        install_counts.columns = ["Installation", "Nombre d'interventions"]
        fig = px.bar(install_counts, x="Installation", y="Nombre d'interventions",
                     title="Nombre de fois où chaque installation a été réparée",
                     color="Installation", text_auto=True)
        fig.update_layout(xaxis_title="Type d'installation", yaxis_title="Nombre d'interventions")
        st.plotly_chart(fig, use_container_width=True)  # use_container_width est accepté pour plotly_chart
        
        st.markdown("---")
        st.subheader("📈 Courbe d'évolution des interventions")
        df_copy = df.copy()
        df_copy["Date d'Émission"] = pd.to_datetime(df_copy["Date d'Émission"])
        df_copy["Mois"] = df_copy["Date d'Émission"].dt.to_period("M").astype(str)
        monthly_counts = df_copy.groupby("Mois").size().reset_index(name="Nombre")
        fig_line = px.line(monthly_counts, x="Mois", y="Nombre", 
                           title="Nombre de bons de travail par mois",
                           markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        st.subheader("💬 Commentaire sur l'optimisation des livraisons")
        completed = df[df["Statut"] == "Terminé"].copy()
        if not completed.empty:
            completed["Date de Réception"] = pd.to_datetime(completed["Date de Réception du Bon de Travail"])
            completed["Date de Livraison"] = pd.to_datetime(completed["Date de Livraison des Travaux"])
            completed["Délai (jours)"] = (completed["Date de Livraison"] - completed["Date de Réception"]).dt.days
            valid_delays = completed["Délai (jours)"].dropna()
            valid_delays = valid_delays[valid_delays >= 0]
            
            if len(valid_delays) > 0:
                avg_delay = valid_delays.mean()
                max_delay = valid_delays.max()
                min_delay = valid_delays.min()
                
                st.metric("Délai moyen de livraison (jours)", f"{avg_delay:.1f}")
                col1, col2 = st.columns(2)
                col1.metric("Délai minimum", f"{min_delay} jours")
                col2.metric("Délai maximum", f"{max_delay} jours")
                
                if avg_delay <= 2:
                    st.success("✅ **La livraison des travaux est optimale** : les délais sont très courts (moyenne ≤ 2 jours).")
                elif avg_delay <= 5:
                    st.info("📊 **Livraison acceptable** : les délais sont modérés. Une légère amélioration pourrait être envisagée.")
                else:
                    st.warning("⚠️ **Livraison non optimale** : les délais sont trop longs. Il est recommandé d'accélérer le processus d'exécution.")
            else:
                st.info("Aucune donnée de délai valide pour les travaux terminés.")
        else:
            st.info("Aucun bon de travail terminé pour analyser les délais.")
        
        st.markdown("---")
        st.subheader("📋 Détail des interventions par installation")
        install_details = df.groupby("Installation Impactée")["Numéro de Bon de Travail"].count().reset_index()
        install_details.columns = ["Installation", "Nombre d'interventions"]
        st.dataframe(install_details, width='stretch')
    else:
        st.info("Aucune donnée disponible. Veuillez ajouter des bons de travail dans l'onglet 'Gestion des Bons'.")

# ==================== Onglet 3 : Tableau complet ====================
with tab3:
    if not df.empty:
        st.subheader("📄 Tous les bons de travail")
        st.dataframe(df, width='stretch')
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données (CSV)",
            data=csv,
            file_name="work_orders_export.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucun bon de travail enregistré pour le moment.")

st.markdown("---")
st.caption("Application de gestion des bons de travail - Version 1.1 (sans suppression)")