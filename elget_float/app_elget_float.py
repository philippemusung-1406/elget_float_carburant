import streamlit as st
import pandas as pd
import sqlite3
import datetime

st.set_page_config(
    page_title="ELGET SARL - Gestion de Flotte & Analyses",
    page_icon="🚚",
    layout="wide"
)

# Esthétique personnalisée
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .brand-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 22px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .brand-header h1 { margin: 0; font-size: 26px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION D'IMPORTATION ADAPTATIVE ---
def charger_excel_ou_csv(uploaded_file):
    filename = uploaded_file.name.lower()
    
    # 1. Gestion des CSV
    if filename.endswith('.csv'):
        try:
            return pd.read_csv(uploaded_file)
        except Exception:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, sep=';')
            
    # 2. Gestion des Excel (.xlsx, .xls)
    engines = ['openpyxl', 'xlrd', 'pyxlsb', None]
    
    for engine in engines:
        try:
            uploaded_file.seek(0)
            xls = pd.ExcelFile(uploaded_file, engine=engine) if engine else pd.ExcelFile(uploaded_file)
            sheets = xls.sheet_names
            
            # Sélection intelligente de l'onglet (donner la priorité aux registres/historiques)
            target_sheet = sheets[0]
            for s in sheets:
                if any(k in s.lower() for k in ['historique', 'registre', 'données', 'data', 'suivi']):
                    target_sheet = s
                    break
                    
            # Lecture brute pour trouver l'en-tête réel
            df_raw = pd.read_excel(xls, sheet_name=target_sheet)
            
            # Scan des premières lignes pour repérer le vrai début du tableau
            skip_rows = None
            keywords = ['date', 'id plein', 'n° fiche', 'tracteur', 'véhicule / immat', 'immat', 'chauffeur']
            
            for idx, row in df_raw.iterrows():
                row_str = " ".join([str(v) for v in row.values if pd.notna(v)]).lower()
                if any(k in row_str for k in keywords):
                    skip_rows = idx + 1
                    break
            
            # Relecture avec le bon décalage de ligne
            uploaded_file.seek(0)
            if skip_rows is not None:
                df = pd.read_excel(xls, sheet_name=target_sheet, skiprows=skip_rows, engine=engine if engine else None)
            else:
                df = df_raw
                
            df = df.dropna(how='all')
            return df, target_sheet, sheets
            
        except Exception:
            continue
            
    raise ValueError("Format de fichier non reconnu ou corrompu.")

# --- INTERFACE UTISATEUR ---
st.markdown("""
    <div class="brand-header">
        <h1>🚚 ELGET SARL — ANALYSEUR UNIVERSEL DE FICHIERS FLOTTE</h1>
        <p>Importation intelligente des registres de carburant et d'inspections</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choisissez un fichier Excel (.xlsx, .xls) ou CSV (.csv) :", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        df, active_sheet, all_sheets = charger_excel_ou_csv(uploaded_file)
        
        st.success(f"✅ Fichier **{uploaded_file.name}** chargé avec succès !")
        
        # Sélection manuelle d'onglet si le fichier contient plusieurs feuilles
        if len(all_sheets) > 1:
            selected_sheet = st.selectbox("Sélectionner l'onglet à analyser :", all_sheets, index=all_sheets.index(active_sheet))
            if selected_sheet != active_sheet:
                uploaded_file.seek(0)
                # Rechargement direct de l'onglet sélectionné
                xls = pd.ExcelFile(uploaded_file)
                df_raw = pd.read_excel(xls, sheet_name=selected_sheet)
                
                skip_rows = None
                for idx, row in df_raw.iterrows():
                    row_str = " ".join([str(v) for v in row.values if pd.notna(v)]).lower()
                    if any(k in row_str for k in ['date', 'id', 'fiche', 'tracteur', 'immat', 'chauffeur']):
                        skip_rows = idx + 1
                        break
                        
                uploaded_file.seek(0)
                df = pd.read_excel(xls, sheet_name=selected_sheet, skiprows=skip_rows if skip_rows else 0).dropna(how='all')

        # Affichage du Tableau de données
        st.markdown(f"### 📋 Donnees extraites ({len(df)} enregistrements)")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 Statistiques & Visuels")

        col_num = df.select_dtypes(include=['number']).columns.tolist()
        col_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()

        c1, c2 = st.columns(2)

        with c1:
            st.write("**📈 Métriques Numériques**")
            if col_num:
                st.dataframe(df[col_num].describe().T)
            else:
                st.info("Aucune colonne numérique détectée dans cet onglet.")

        with c2:
            st.write("**📊 Représentation Graphique**")
            if col_cat and col_num:
                cat_col = st.selectbox("Axe des catégories (X) :", col_cat)
                num_col = st.selectbox("Valeur à mesurer (Y) :", col_num)
                
                df_grouped = df.groupby(cat_col)[num_col].mean().reset_index()
                st.bar_chart(df_grouped, x=cat_col, y=num_col)
            elif col_num:
                num_col = st.selectbox("Sélectionner la métrique :", col_num)
                st.line_chart(df[num_col])
            else:
                st.info("Sélectionnez un onglet contenant des colonnes analysables.")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier : {e}")
