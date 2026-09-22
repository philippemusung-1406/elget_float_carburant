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

# --- STYLES CSS SUR MESURE (DESIGN AVANCÉ) ---
st.markdown("""
    <style>
    /* Style général */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* En-tête principal */
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

    /* Cards KPI */
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

    /* Cadres de formulaires */
    .form-section {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
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
st.sidebar.image("https://img.icons8.com/color/96/semi-truck.png", width=70)
st.sidebar.title("ELGET SARL")
menu = st.sidebar.radio(
    "Navigation Principale",
    [
        "📊 Tableau de Bord",
        "📋 Inspection Camion & Pneus",
        "⛽ Suivi du Carburant",
        "📂 Historique & Import Excel"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Version 2.0 avec analyse de données & Import Excel")

# ==============================================================================
# 1. TABLEAU DE BORD (DASHBOARD)
# ==============================================================================
if menu == "📊 Tableau de Bord":
    st.subheader("📊 Métriques & Indicateurs Clés")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    total_camions = len(set([i.get('immat') for i in st.session_state.inspections_camion if i.get('immat')]))
    immobilises = sum(1 for i in st.session_state.inspections_camion if i.get('statut') == 'IMMOBILISÉ')
    volume_total = sum(r.get('volume', 0) for r in st.session_state.ravitaillements)
    avg_cons = [r.get('conso_100km', 0) for r in st.session_state.ravitaillements if r.get('conso_100km', 0) > 0]
    moyenne_flotte = sum(avg_cons) / len(avg_cons) if avg_cons else 0

    col1.markdown(f'<div class="kpi-card"><div class="kpi-title">Camions Inspectés</div><div class="kpi-value">{total_camions}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card" style="border-left-color: #ef4444;"><div class="kpi-title">Camions Immobilisés</div><div class="kpi-value" style="color:#ef4444;">{immobilises}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card" style="border-left-color: #10b981;"><div class="kpi-title">Volume Carburant</div><div class="kpi-value">{volume_total:.1f} L</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card" style="border-left-color: #f59e0b;"><div class="kpi-title">Conso. Moyenne Flotte</div><div class="kpi-value">{moyenne_flotte:.1f} L/100km</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Graphiques si des données sont disponibles
    if st.session_state.ravitaillements:
        st.subheader("📈 Analyse de la Consommation")
        df_r = pd.DataFrame(st.session_state.ravitaillements)
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.write("**Consommation (L/100km) par Immatriculation**")
            st.bar_chart(df_r, x="immat", y="conso_100km")
        
        with c_chart2:
            st.write("**Volumes de Carburant Ajoutés (Litres)**")
            st.line_chart(df_r, x="date", y="volume")
    else:
        st.info("ℹ️ Renseignez des ravitaillements ou importez un fichier Excel pour afficher les graphiques de suivi.")

# ==============================================================================
# 2. INSPECTION CAMION & PNEUS
# ==============================================================================
elif menu == "📋 Inspection Camion & Pneus":
    st.subheader("📋 Fiche d'Inspection : Camion, Remorque & Pneus")
    
    with st.form("form_camion"):
        st.markdown("##### 1. Identification du Véhicule")
        c1, c2, c3, c4 = st.columns(4)
        date_insp = c1.date_input("Date", datetime.date.today())
        immat_camion = c2.text_input("Camion / Immat", placeholder="Ex: 1234AB01")
        chauffeur = c3.text_input("Chauffeur")
        immat_remorque = c4.text_input("Remorque / Immat")

        st.markdown("---")
        st.markdown("##### 2. Cabine & Sécurité Générale")
        qc1, qc2, qc3 = st.columns(3)
        docs_ok = qc1.selectbox("Documents de bord", ["OK", "NOK"])
        eq_sec_ok = qc2.selectbox("Équipements de sécurité", ["OK", "NOK"])
        ecl_ok = qc3.selectbox("Éclairage complet", ["OK", "NOK"])

        st.markdown("---")
        st.markdown("##### 3. Attelage & Remorque")
        qa1, qa2, qa3, qa4 = st.columns(4)
        sellette_ok = qa1.selectbox("Verrouillage sellette", ["OK", "NOK"])
        flex_ok = qa2.selectbox("Flexibles d'air / Câbles", ["OK", "NOK"])
        bequilles_ok = qa3.selectbox("Béquilles remorque", ["OK", "NOK"])
        arrimage_ok = qa4.selectbox("Arrimage chargement", ["OK", "NOK"])

        st.markdown("---")
        st.markdown("##### 4. Contrôle des Pneumatiques")
        qp1, qp2, qp3, qp4 = st.columns(4)
        press_ok = qp1.selectbox("Pression à froid", ["OK", "NOK"])
        sculpt_ok = qp2.selectbox("Profondeur sculpture (>=1.6mm)", ["OK", "NOK"])
        ecrous_ok = qp3.selectbox("Serrage écrous de roues", ["OK", "NOK"])
        corps_ok = qp4.selectbox("Absence corps étrangers", ["OK", "NOK"])

        st.markdown("---")
        st.markdown("##### 5. Décision Finale & Validation")
        statut = st.radio("Statut d'Inspection", ["CONFORME", "AVERTISSEMENT", "IMMOBILISÉ"], horizontal=True)
        inspecteur = st.text_input("Nom de l'Inspecteur")
        remarques_finales = st.text_area("Remarques / Actions requises")

        submit = st.form_submit_button("💾 Enregistrer la Fiche d'Inspection")
        
        if submit:
            nouvelle_inspection = {
                "date": str(date_insp),
                "immat": immat_camion,
                "chauffeur": chauffeur,
                "remorque": immat_remorque,
                "statut": statut,
                "inspecteur": inspecteur,
                "remarques": remarques_finales
            }
            st.session_state.inspections_camion.append(nouvelle_inspection)
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
                "date": f"{date_ravit} {heure_ravit.strftime('%H:%M')}",
                "immat": immat,
                "chauffeur": chauffeur,
                "station": station,
                "km_prec": km_prec,
                "km_act": km_act,
                "distance": dist_parcourue,
                "volume": volume,
                "conso_100km": round(conso_calc, 2),
                "ecart": ecart,
                "num_bon": num_bon
            }
            st.session_state.ravitaillements.append(nouveau_plein)
        else:
            st.error("❌ Le kilométrage actuel doit être supérieur au kilométrage précédent.")

# ==============================================================================
# 4. HISTORIQUE ET IMPORT EXCEL
# ==============================================================================
elif menu == "📂 Historique & Import Excel":
    st.subheader("📂 Historique & Chargement de Fichiers Excel")

    st.markdown("### 📥 Charger vos données Excel ou CSV")
    st.write("Vous pouvez importer votre fichier Excel directement ci-dessous. Il mettra automatiquement à jour l'application et les graphiques.")

    uploaded_file = st.file_uploader("Choisissez un fichier Excel (.xlsx) ou CSV (.csv)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_imported = pd.read_csv(uploaded_file)
            else:
                df_imported = pd.read_excel(uploaded_file)
            
            st.success("✅ Fichier chargé avec succès !")
            st.write("**Aperçu des données importées :**")
            st.dataframe(df_imported, use_container_width=True)

            # Option d'injection dans la session
            if st.button("➕ Injecter ces données dans l'application"):
                records = df_imported.to_dict(orient='records')
                st.session_state.ravitaillements.extend(records)
                st.success("Données ajoutées au tableau de bord !")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

    st.markdown("---")
    st.markdown("### 📋 Données Actuelles en Mémoire")

    tab1, tab2 = st.tabs(["📋 Inspections Camions", "⛽ Ravitaillements Carburant"])

    with tab1:
        if st.session_state.inspections_camion:
            df_c = pd.DataFrame(st.session_state.inspections_camion)
            st.dataframe(df_c, use_container_width=True)
        else:
            st.info("Aucune inspection enregistrée.")

    with tab2:
        if st.session_state.ravitaillements:
            df_r = pd.DataFrame(st.session_state.ravitaillements)
            st.dataframe(df_r, use_container_width=True)
        else:
            st.info("Aucun ravitaillement enregistré.")
