import streamlit as st
import pandas as pd
import sqlite3
import datetime

st.set_page_config(
    page_title="ELGET SARL - Flotte, Carburant & Analyses",
    page_icon="🚚",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .brand-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .brand-header h1 { margin: 0; font-size: 28px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION DE LECTURE EXCEL UNIVERSELLE & ANTIFRAGILE ---
def lire_fichier_universel(uploaded_file):
    filename = uploaded_file.name.lower()
    
    # 1. Traitement des fichiers CSV
    if filename.endswith('.csv'):
        try:
            return pd.read_csv(uploaded_file)
        except Exception:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, sep=';')
            
    # 2. Traitement des fichiers Excel (.xlsx, .xls) avec moteurs multiples
    engines = ['openpyxl', 'xlrd', 'pyxlsb', None]
    
    for engine in engines:
        try:
            uploaded_file.seek(0)
            if engine:
                xls = pd.ExcelFile(uploaded_file, engine=engine)
            else:
                xls = pd.ExcelFile(uploaded_file)
                
            sheets = xls.sheet_names
            sheet_target = sheets[0]
            
            # Recherche automatique du bon onglet
            for s in sheets:
                if any(k in s.lower() for k in ['plein', 'carburant', 'inspection', 'suivi', 'flotte', 'donnees']):
                    sheet_target = s
                    break
                    
            df_raw = pd.read_excel(xls, sheet_name=sheet_target)
            
            # Détection et saut des lignes de titre décoratives
            skip = 0
            for idx, row in df_raw.iterrows():
                row_str = " ".join([str(v) for v in row.values if pd.notna(v)]).lower()
                if any(k in row_str for k in ['date', 'plein', 'fiche', 'immat', 'camion', 'chauffeur', 'km']):
                    skip = idx + 1
                    break
            
            uploaded_file.seek(0)
            if skip > 0:
                df = pd.read_excel(xls, sheet_name=sheet_target, skiprows=skip, engine=engine).dropna(how='all')
            else:
                df = df_raw.dropna(how='all')
                
            return df
        except Exception:
            continue

    # 3. Mode secours : Fichier HTML / CSV renommé en .xlsx par erreur
    try:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, on_bad_lines='skip', sep=None, engine='python')
    except Exception as e:
        raise ValueError("Impossible de lire ce fichier Excel. Enregistrez-le sous le format .CSV depuis Excel puis réessayez.")

# --- ENTÊTE APPLICATION ---
st.markdown("""
    <div class="brand-header">
        <h1>🚛 ELGET SARL — GESTION DE FLOTTE & ANALYSE DE FICHIERS EXCEL</h1>
        <p>Analyse automatique et chargement universel sans erreur d'importation</p>
    </div>
""", unsafe_allow_html=True)

# --- APPLICATION PRINCIPALE ---
st.subheader("📂 Chargement & Analyse des Fichiers Excel / CSV")

file = st.file_uploader("Déposez votre fichier Excel (.xlsx, .xls) ou CSV (.csv) :", type=["xlsx", "xls", "csv"])

if file is not None:
    try:
        df = lire_fichier_universel(file)
        st.success(f"✅ Fichier **{file.name}** chargé avec succès ! ({len(df)} lignes, {len(df.columns)} colonnes)")
        
        # Aperçu interactif
        st.markdown("### 📋 Aperçu des Données")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📊 Analyses Automatiques")
        
        col_num = df.select_dtypes(include=['float64', 'int64', 'float', 'int']).columns.tolist()
        col_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("**📈 Statistiques Récapitulatives**")
            if col_num:
                st.dataframe(df[col_num].describe().T)
            else:
                st.info("Aucune colonne numérique détectée.")
                
        with c2:
            st.write("**📊 Graphique Interactif**")
            if col_cat and col_num:
                col_x = st.selectbox("Axe X (Catégorie / Élément) :", col_cat)
                col_y = st.selectbox("Axe Y (Valeur numérique) :", col_num)
                
                df_grouped = df.groupby(col_x)[col_y].sum().reset_index()
                st.bar_chart(df_grouped, x=col_x, y=col_y)
            elif col_num:
                col_y = st.selectbox("Sélectionnez la colonne à afficher :", col_num)
                st.line_chart(df[col_y])
            else:
                st.info("Données insuffisantes pour générer un graphique.")

    except Exception as err:
        st.error(f"❌ Erreur lors de la lecture du fichier : {err}")
        st.info("💡 Astuce : Si le problème persiste, ouvrez le fichier dans Excel et faites **Fichier > Enregistrer sous > CSV (séparé par des virgules) (.csv)**.")
