import streamlit as st
import pandas as pd
import sqlite3
import datetime
import openpyxl

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestion ELGET SARL", layout="wide")

# --- CONNEXION BASE DE DONNÉES LOCALES (PERSISTANTE) ---
DB_FILE = "elget_sarl.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table Carburant
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carburant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            vehicule TEXT,
            chauffeur TEXT,
            litres REAL,
            cout_total REAL,
            station TEXT,
            kms_compteur REAL
        )
    """)
    
    # Table Inspections (Camions, Remorques, Pneus)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            immatriculation TEXT,
            type_element TEXT, -- Camion, Remorque, Pneu
            inspecteur TEXT,
            etat_general TEXT,
            pression_pneus_psi REAL,
            remarques TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- FONCTIONS DE CHARGEMENT & ET D'INSERTION ---
def charger_donnees(table_name):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def inserer_carburant(date, vehicule, chauffeur, litres, cout, station, kms):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO carburant (date, vehicule, chauffeur, litres, cout_total, station, kms_compteur)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (str(date), vehicule, chauffeur, litres, cout, station, kms))
    conn.commit()
    conn.close()

def inserer_inspection(date, immatriculation, type_element, inspecteur, etat, pression, remarques):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inspections (date, immatriculation, type_element, inspecteur, etat_general, pression_pneus_psi, remarques)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (str(date), immatriculation, type_element, inspecteur, etat, pression, remarques))
    conn.commit()
    conn.close()

def importer_excel_vers_db(uploaded_file, table_name):
    """Importation initiale de fichiers Excel vers SQLite"""
    try:
        df = pd.read_excel(uploaded_file)
        conn = get_connection()
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        st.success(f"Données importées avec succès dans la table '{table_name}' !")
    except Exception as e:
        st.error(f"Erreur lors de l'importation : {e}")

# --- INTERFACE UTILISATEUR (STREAMLIT) ---
st.title("🚛 Système de Gestion ELGET SARL")

menu = st.sidebar.selectbox(
    "Navigation", 
    ["Tableau de bord / Analyses", "Gestion Carburant", "Inspections Pneus & Véhicules", "Importation Excel"]
)

# 1. IMPORTATION DES FICHIERS EXCEL EXISTANTS
if menu == "Importation Excel":
    st.header("📥 Charger vos fichiers Excel existants")
    st.write("Les données chargées seront sauvegardées de manière permanente dans la base de données de l'application.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Carburant")
        file_carburant = st.file_uploader("Fichier Gestion_Carburant_ELGET_SARL.xlsx", type=["xlsx"], key="carb")
        if file_carburant and st.button("Importer Carburant"):
            importer_excel_vers_db(file_carburant, "carburant")
            
    with col2:
        st.subheader("Inspections & Pneus")
        file_inspection = st.file_uploader("Fichier Inspection_Camion_Remorque_Pneus_ELGET_SARL.xlsx", type=["xlsx"], key="insp")
        if file_inspection and st.button("Importer Inspections"):
            importer_excel_vers_db(file_inspection, "inspections")

# 2. GESTION DU CARBURANT (Saisie)
elif menu == "Gestion Carburant":
    st.header("⛽ Saisie & Historique Carburant")
    
    with st.expander("➕ Ajouter un plein de carburant"):
        with st.form("form_carburant"):
            col1, col2, col3 = st.columns(3)
            date_c = col1.date_input("Date", datetime.date.today())
            vehicule = col2.text_input("Véhicule / Immatriculation")
            chauffeur = col3.text_input("Chauffeur")
            
            col4, col5, col6 = st.columns(3)
            litres = col4.number_input("Litres", min_value=0.0)
            cout = col5.number_input("Coût total ($)", min_value=0.0)
            station = col6.text_input("Station / Fournisseur")
            kms = st.number_input("Kilométrage Compteur", min_value=0.0)
            
            submit = st.form_submit_button("Enregistrer")
            if submit:
                inserer_carburant(date_c, vehicule, chauffeur, litres, cout, station, kms)
                st.success("Enregistrement carburant sauvegardé avec succès !")
                st.rerun()

    st.subheader("📊 Données Carburant enregistrées")
    df_carb = charger_donnees("carburant")
    st.dataframe(df_carb, use_container_width=True)

# 3. INSPECTIONS (Saisie)
elif menu == "Inspections Pneus & Véhicules":
    st.header("🔍 Saisie & Historique des Inspections")
    
    with st.expander("➕ Ajouter une nouvelle inspection"):
        with st.form("form_inspection"):
            col1, col2, col3 = st.columns(3)
            date_i = col1.date_input("Date Inspection", datetime.date.today())
            immatriculation = col2.text_input("Immatriculation")
            type_element = col3.selectbox("Élément inspecté", ["Camion", "Remorque", "Pneu"])
            
            col4, col5 = st.columns(2)
            inspecteur = col4.text_input("Nom Inspecteur")
            etat = col5.selectbox("État général", ["Bon", "À réparer", "Critique", "Remplacé"])
            
            pression = st.number_input("Pression Pneus (PSI)", min_value=0.0)
            remarques = st.text_area("Remarques / Anomales détectées")
            
            submit = st.form_submit_button("Enregistrer Inspection")
            if submit:
                inserer_inspection(date_i, immatriculation, type_element, inspecteur, etat, pression, remarques)
                st.success("Inspection enregistrée avec succès !")
                st.rerun()

    st.subheader("📋 Données Inspections enregistrées")
    df_insp = charger_donnees("inspections")
    st.dataframe(df_insp, use_container_width=True)

# 4. TABLEAU DE BORD ET ANALYSES
elif menu == "Tableau de bord / Analyses":
    st.header("📈 Synthèse et Analyse des Données ELGET SARL")
    
    df_carb = charger_donnees("carburant")
    df_insp = charger_donnees("inspections")
    
    tab1, tab2 = st.tabs(["Analyse Carburant", "Analyse Maintenance & Pneus"])
    
    with tab1:
        if not df_carb.empty:
            st.metric("Total Litres Consommés", f"{df_carb['litres'].sum():,.2f} L")
            st.metric("Coût Total Carburant", f"${df_carb['cout_total'].sum():,.2f}")
            
            st.subheader("Consommation par Véhicule")
            chart_carb = df_carb.groupby("vehicule")["litres"].sum()
            st.bar_chart(chart_carb)
        else:
            st.info("Aucune donnée de carburant enregistrée.")

    with tab2:
        if not df_insp.empty:
            st.metric("Nombre total d'inspections", len(df_insp))
            
            st.subheader("Répartition des États Général")
            st.bar_chart(df_insp["etat_general"].value_counts())
        else:
            st.info("Aucune donnée d'inspection enregistrée.")
