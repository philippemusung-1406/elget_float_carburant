import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ELGET SARL - Flotte & Carburant",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLES CSS PERSONNALISÉS (DESIGN AVANCÉ) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .brand-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .brand-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .brand-header p {
        margin-top: 5px;
        opacity: 0.9;
        font-size: 14px;
    }
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 13px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if 'inspections_camion' not in st.session_state:
    st.session_state.inspections_camion = []
if 'ravitaillements' not in st.session_state:
    st.session_state.ravitaillements = []

# --- ENTÊTE APPLICATION ---
st.markdown("""
    <div class="brand-header">
        <h1>🚛 ELGET SARL — GESTION DE FLOTTE & CARBURANT</h1>
        <p>Plateforme de suivi technique des véhicules, état des pneumatiques et contrôle de consommation</p>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("ELGET SARL")
menu = st.sidebar.radio(
    "Navigation Principale",
    [
        "📊 Tableau de Bord",
        "📋 Inspection Camion & Pneus",
        "⛽ Suivi du Carburant",
        "📂 Historique & Importation"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Version 2.1 — Compatible Excel & CSV")

# ==============================================================================
# 1. TABLEAU DE BORD (DASHBOARD)
# ==============================================================================
if menu == "📊 Tableau de Bord":
    st.subheader("📊 Métriques & Indicateurs Clés")

    col1, col2, col3, col4 = st.columns(4)
    
    total_camions = len(set([i.get('Immat_Camion', i.get('immat', '')) for i in st.session_state.inspections_camion if i.get('Immat_Camion', i.get('immat', ''))]))
    immobilises = sum(1 for i in st.session_state.inspections_camion if i.get('Statut', i.get('statut', '')) == 'IMMOBILISÉ')
    
    # Calcul volume total
    volume_total = 0.0
    for r in st.session_state.ravitaillements:
        vol = r.get('Volume_L', r.get('volume', 0))
        try:
            volume_total += float(vol)
        except (ValueError, TypeError):
            pass

    # Calcul conso moyenne
    avg_cons = []
    for r in st.session_state.ravitaillements:
        c = r.get('Conso_L100km', r.get('conso_100km', 0))
        try:
            c_val = float(c)
            if c_val > 0:
                avg_cons.append(c_val)
        except (ValueError, TypeError):
            pass
            
    moyenne_flotte = sum(avg_cons) / len(avg_cons) if avg_cons else 0.0

    col1.markdown(f'<div class="kpi-card"><div class="kpi-title">Camions Inspectés</div><div class="kpi-value">{total_camions}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card" style="border-left-color: #ef4444;"><div class="kpi-title">Camions Immobilisés</div><div class="kpi-value" style="color:#ef4444;">{immobilises}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card" style="border-left-color: #10b981;"><div class="kpi-title">Volume Carburant</div><div class="kpi-value">{volume_total:.1f} L</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card" style="border-left-color: #f59e0b;"><div class="kpi-title">Conso. Moyenne Flotte</div><div class="kpi-value">{moyenne_flotte:.1f} L/100km</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    if st.session_state.ravitaillements:
        st.subheader("📈 Analyse de la Consommation")
        df_r = pd.DataFrame(st.session_state.ravitaillements)
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            col_immat = 'Immat' if 'Immat' in df_r.columns else ('immat' if 'immat' in df_r.columns else None)
            col_conso = 'Conso_L100km' if 'Conso_L100km' in df_r.columns else ('conso_100km' if 'conso_100km' in df_r.columns else None)
            
            if col_immat and col_conso:
                st.write("**Consommation (L/100km) par Véhicule**")
                st.bar_chart(df_r, x=col_immat, y=col_conso)
        
        with c_chart2:
            col_date = 'Date_Heure' if 'Date_Heure' in df_r.columns else ('date' if 'date' in df_r.columns else None)
            col_vol = 'Volume_L' if 'Volume_L' in df_r.columns else ('volume' if 'volume' in df_r.columns else None)
            
            if col_date and col_vol:
                st.write("**Volumes de Carburant Ajoutés (Litres)**")
                st.line_chart(df_r, x=col_date, y=col_vol)
    else:
        st.info("ℹ️ Renseignez des ravitaillements ou importez un fichier pour afficher les graphiques.")

# ==============================================================================
# 2. INSPECTION CAMION & PNEUS
# ==============================================================================
elif menu == "📋 Inspection Camion & Pneus":
    st.subheader("📋 Fiche d'Inspection : Camion, Remorque & Pneus")
    
    with st.form("form_camion"):
        st.markdown("##### 1. Identification du Véhicule")
        c1, c2, c3, c4 = st.columns(4)
        date_insp = c1.date_input("Date", datetime.date.today())
        immat_camion = c2.text_input("Camion / Immat", placeholder="Ex: C-101")
        chauffeur = c3.text_input("Chauffeur")
        immat_remorque = c4.text_input("Remorque / Immat")

        st.markdown("---")
        st.markdown("##### 2. Contrôles de Sécurité & Attelage")
        qc1, qc2, qc3, qc4 = st.columns(4)
        docs_ok = qc1.selectbox("Documents de bord", ["OK", "NOK"])
        eq_sec_ok = qc2.selectbox("Équipements sécurité", ["OK", "NOK"])
        ecl_ok = qc3.selectbox("Éclairage complet", ["OK", "NOK"])
        attelage_ok = qc4.selectbox("Attelage & Flexibles", ["OK", "NOK"])

        st.markdown("---")
        st.markdown("##### 3. Pneumatiques & Pression")
        qp1, qp2, qp3, qp4 = st.columns(4)
        e1_g = qp1.text_input("Essieu 1 - Gauche", "8.5 bar / 5 mm")
        e1_d = qp2.text_input("Essieu 1 - Droite", "8.5 bar / 5 mm")
        e2_g = qp3.text_input("Essieu 2 - Gauche", "8.5 bar / 4 mm")
        e2_d = qp4.text_input("Essieu 2 - Droite", "8.5 bar / 4 mm")

        st.markdown("---")
        st.markdown("##### 4. Décision Finale")
        statut = st.radio("Statut d'Inspection", ["CONFORME", "AVERTISSEMENT", "IMMOBILISÉ"], horizontal=True)
        inspecteur = st.text_input("Nom de l'Inspecteur")
        remarques = st.text_area("Remarques / Actions requises")

        submit = st.form_submit_button("💾 Enregistrer la Fiche d'Inspection")
        
        if submit:
            nouvelle_insp = {
                "Date": str(date_insp),
                "Immat_Camion": immat_camion,
                "Chauffeur": chauffeur,
                "Immat_Remorque": immat_remorque,
                "Docs_Bord": docs_ok,
                "Equipements_Securite": eq_sec_ok,
                "Eclairage_Voyants": ecl_ok,
                "Attelage_Flexibles": attelage_ok,
                "Essieu1_G_Bar_mm": e1_g,
                "Essieu1_D_Bar_mm": e1_d,
                "Essieu2_G_Bar_mm": e2_g,
                "Essieu2_D_Bar_mm": e2_d,
                "Statut": statut,
                "Inspecteur": inspecteur,
                "Remarques": remarques
            }
            st.session_state.inspections_camion.append(nouvelle_insp)
            st.success("✅ Fiche enregistrée avec succès !")

# ==============================================================================
# 3. SUIVI DU CARBURANT
# ==============================================================================
elif menu == "⛽ Suivi du Carburant":
    st.subheader("⛽ Fiche de Gestion et Suivi du Carburant")

    with st.form("form_carburant"):
        st.markdown("##### 1. Information du Ravitaillement")
        c1, c2, c3, c4 = st.columns(4)
        date_ravit = c1.date_input("Date", datetime.date.today())
        heure_ravit = c2.time_input("Heure", datetime.datetime.now().time())
        immat = c3.text_input("N° Immatriculation / Parc")
        chauffeur = c4.text_input("Nom du Chauffeur")
        station = st.text_input("Station / Mode de Plein")

        st.markdown("---")
        st.markdown("##### 2. Relevé Métrique & Calcul Consommation")
        r1, r2, r3, r4, r5 = st.columns(5)
        km_prec = r1.number_input("Km Précédent", min_value=0.0, step=1.0)
        km_act = r2.number_input("Km Actuel", min_value=0.0, step=1.0)
        volume = r3.number_input("Volume Ajouté (L)", min_value=0.0, step=0.1)
        jauge = r4.number_input("Niveau Jauge (%)", min_value=0, max_value=100, value=100)
        num_bon = r5.text_input("N° Bon / Carte")

        st.markdown("---")
        cible_conso = st.number_input("Consommation Cible (L/100km)", value=35.0, step=0.5)

        submit_carb = st.form_submit_button("🧮 Calculer et Enregistrer")

    if submit_carb:
        dist_parcourue = km_act - km_prec
        if dist_parcourue > 0:
            conso_calc = (volume / dist_parcourue) * 100
            ecart = "Normal" if conso_calc <= cible_conso else "Élevé"
            
            st.success(f"📊 Consommation calculée : **{conso_calc:.2f} L/100 km** (Statut: **{ecart}**)")

            nouveau_plein = {
                "Date_Heure": f"{date_ravit} {heure_ravit.strftime('%H:%M')}",
                "Immat": immat,
                "Chauffeur": chauffeur,
                "Station_Mode": station,
                "Km_Precedent": km_prec,
                "Km_Actuel": km_act,
                "Volume_L": volume,
                "Niveau_Jauge_Pct": jauge,
                "Num_Bon_Carte": num_bon,
                "Conso_L100km": round(conso_calc, 2),
                "Ecart": ecart
            }
            st.session_state.ravitaillements.append(nouveau_plein)
        else:
            st.error("❌ Le kilométrage actuel doit être supérieur au kilométrage précédent.")

# ==============================================================================
# 4. HISTORIQUE ET IMPORTATION DE FICHIERS EXCEL / CSV
# ==============================================================================
elif menu == "📂 Historique & Importation":
    st.subheader("📂 Historique Général & Importation de Données")

    st.markdown("### 📥 Importer un Fichier (Excel `.xlsx` ou `.csv`)")
    type_import = st.radio("Choisissez la destination des données à importer :", ["Ravitaillements Carburant", "Inspections Camions"], horizontal=True)

    uploaded_file = st.file_uploader("Sélectionnez votre fichier", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_imported = pd.read_csv(uploaded_file)
            else:
                df_imported = pd.read_excel(uploaded_file, engine='openpyxl')
            
            st.success("✅ Fichier chargé et lu avec succès !")
            st.write("**Aperçu des données importées :**")
            st.dataframe(df_imported, use_container_width=True)

            if st.button("➕ Injecter ces données dans le tableau de bord"):
                records = df_imported.to_dict(orient='records')
                if type_import == "Ravitaillements Carburant":
                    st.session_state.ravitaillements.extend(records)
                else:
                    st.session_state.inspections_camion.extend(records)
                st.success("Données ajoutées avec succès !")
                st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {e}")
            st.info("💡 Conseils : Assurez-vous d'avoir bien inclus 'openpyxl' dans votre fichier requirements.txt ou utilisez le format .csv")

    st.markdown("---")
    st.markdown("### 📋 Données Actuellement enregistrées")

    tab1, tab2 = st.tabs(["📋 Inspections Camions", "⛽ Ravitaillements Carburant"])

    with tab1:
        if st.session_state.inspections_camion:
            df_c = pd.DataFrame(st.session_state.inspections_camion)
            st.dataframe(df_c, use_container_width=True)
            csv_c = df_c.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV Inspections", csv_c, "Inspections_ELGET.csv", "text/csv")
        else:
            st.info("Aucune inspection enregistrée.")

    with tab2:
        if st.session_state.ravitaillements:
            df_r = pd.DataFrame(st.session_state.ravitaillements)
            st.dataframe(df_r, use_container_width=True)
            csv_r = df_r.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV Carburant", csv_r, "Carburant_ELGET.csv", "text/csv")
        else:
            st.info("Aucun ravitaillement enregistré.")
