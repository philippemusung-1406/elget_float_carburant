import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ELGET SARL - Gestion Camions & Carburant",
    page_icon="🚛",
    layout="wide"
)

# --- CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main-header { font-size:26px; font-weight:bold; color:#1E3A8A; text-align:center; margin-bottom:20px; }
    .sub-header { font-size:18px; font-weight:bold; color:#1E40AF; margin-top:15px; }
    .card { background-color:#F3F4F6; padding:15px; border-radius:10px; margin-bottom:10px; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if 'inspections_camion' not in st.session_state:
    st.session_state.inspections_camion = []
if 'ravitaillements' not in st.session_state:
    st.session_state.ravitaillements = []

# --- TITRE DE L'APPLICATION ---
st.markdown("<div class='main-header'>🚚 ELGET SARL — SYSTÈME DE SUIVI FLOTTE & CARBURANT</div>", unsafe_allow_html=True)

# --- NAVIGATION VIA BARRE LATÉRALE ---
menu = st.sidebar.radio(
    "📍 Navigation",
    [
        "📊 Tableau de Bord",
        "📋 Inspection Camion & Pneus",
        "⛽ Suivi du Carburant",
        "📂 Historique & Exports"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Aide Rapide** : Complétez les formulaires sur le terrain. Les données sont enregistrées automatiquement.")

# ==============================================================================
# 1. TABLEAU DE BORD (DASHBOARD)
# ==============================================================================
if menu == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord & Indicateurs Clefs")

    col1, col2, col3, col4 = st.columns(4)
    
    total_camions = len(set([i.get('immat') for i in st.session_state.inspections_camion if i.get('immat')]))
    immobilises = sum(1 for i in st.session_state.inspections_camion if i.get('statut') == 'IMMOBILISÉ')
    volume_total = sum(r.get('volume', 0) for r in st.session_state.ravitaillements)
    
    col1.metric("Camions Inspectés", total_camions)
    col2.metric("Camions Immobilisés", immobilises, delta_color="inverse")
    col3.metric("Volume Carburant Total", f"{volume_total:.1f} L")
    
    avg_cons = [r.get('conso_100km', 0) for r in st.session_state.ravitaillements if r.get('conso_100km', 0) > 0]
    moyenne_flotte = sum(avg_cons) / len(avg_cons) if avg_cons else 0
    col4.metric("Conso. Moyenne Flotte", f"{moyenne_flotte:.1f} L/100km")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Dernières Inspections Véhicules")
        if st.session_state.inspections_camion:
            df_c = pd.DataFrame(st.session_state.inspections_camion)[['date', 'immat', 'chauffeur', 'statut']]
            st.dataframe(df_c.tail(5), use_container_width=True)
        else:
            st.write("Aucune inspection enregistrée.")

    with col_b:
        st.subheader("Derniers Ravitaillements Carburant")
        if st.session_state.ravitaillements:
            df_r = pd.DataFrame(st.session_state.ravitaillements)[['date', 'immat', 'volume', 'conso_100km', 'ecart']]
            st.dataframe(df_r.tail(5), use_container_width=True)
        else:
            st.write("Aucun ravitaillement enregistré.")

# ==============================================================================
# 2. FICHE D'INSPECTION: CAMION, REMORQUE & PNEUS
# ==============================================================================
elif menu == "📋 Inspection Camion & Pneus":
    st.title("📋 Fiche d'Inspection : Camion, Remorque & Pneus")
    
    with st.form("form_camion"):
        st.subheader("1. Informations Générales")
        c1, c2, c3, c4 = st.columns(4)
        date_insp = c1.date_input("Date", datetime.date.today())
        immat_camion = c2.text_input("Camion / Immat")
        chauffeur = c3.text_input("Chauffeur")
        immat_remorque = c4.text_input("Remorque / Immat")

        st.markdown("---")
        st.subheader("2. Cabine & Sécurité Générale")
        
        qc1, qc2, qc3 = st.columns([3, 2, 3])
        docs_ok = qc1.selectbox("Documents de bord (Carte rose, Assurance, Contrôle technique)", ["OK", "NOK"])
        eq_sec_ok = qc2.selectbox("Équipements de sécurité (Gilet, triangle, extincteurs à jour)", ["OK", "NOK"])
        ecl_ok = qc3.selectbox("Éclairage complet (Feux croisement/route, clignotants, feux stop)", ["OK", "NOK"])
        
        rem_cabine = st.text_input("Remarques Cabine & Sécurité")

        st.markdown("---")
        st.subheader("3. Attelage & Remorque")
        
        qa1, qa2, qa3, qa4 = st.columns(4)
        sellette_ok = qa1.selectbox("Verrouillage sellette / cheville", ["OK", "NOK"])
        flex_ok = qa2.selectbox("Flexibles d'air & câbles élec.", ["OK", "NOK"])
        bequilles_ok = qa3.selectbox("Béquilles remorque relevées", ["OK", "NOK"])
        arrimage_ok = qa4.selectbox("Arrimage chargement / Bâches", ["OK", "NOK"])

        st.markdown("---")
        st.subheader("4. Pneumatiques (État visuel & Contrôles)")
        
        qp1, qp2, qp3, qp4 = st.columns(4)
        press_ok = qp1.selectbox("Pression à froid (Tracteur+Remorque)", ["OK", "NOK"])
        sculpt_ok = qp2.selectbox("Profondeur sculpture (>=1.6 mm)", ["OK", "NOK"])
        ecrous_ok = qp3.selectbox("Serrage écrous / Indicateurs visuels", ["OK", "NOK"])
        corps_ok = qp4.selectbox("Absence corps étrangers (Jumelées)", ["OK", "NOK"])

        st.markdown("---")
        st.subheader("5. Relevé Métrique des Pneus")
        
        e1_g = st.text_input("Essieu 1 (Directeur) - Gauche (Pression / mm)", "8.5 bar / 5 mm")
        e1_d = st.text_input("Essieu 1 (Directeur) - Droite (Pression / mm)", "8.5 bar / 5 mm")
        
        e2_g = st.text_input("Essieu 2 (Moteur Int/Ext) - Gauche (Pression / mm)", "8.5 bar / 4 mm")
        e2_d = st.text_input("Essieu 2 (Moteur Int/Ext) - Droite (Pression / mm)", "8.5 bar / 4 mm")

        st.markdown("---")
        st.subheader("6. Décision Finale")
        
        statut = st.radio("Statut d'Inspection", ["CONFORME", "AVERTISSEMENT", "IMMOBILISÉ"], horizontal=True)
        inspecteur = st.text_input("Nom de l'Inspecteur")
        remarques_finales = st.text_area("Remarques / Actions à entreprendre")

        submit = st.form_submit_button("💾 Enregistrer l'inspection")
        
        if submit:
            nouvelle_inspection = {
                "date": str(date_insp),
                "immat": immat_camion,
                "chauffeur": chauffeur,
                "remorque": immat_remorque,
                "statut": statut,
                "inspecteur": inspecteur,
                "remarques": remarques_finales,
                "details": {
                    "docs": docs_ok,
                    "securite": eq_sec_ok,
                    "eclairage": ecl_ok,
                    "attelage": sellette_ok,
                    "pneus_press": press_ok
                }
            }
            st.session_state.inspections_camion.append(nouvelle_inspection)
            st.success("✅ Fiche d'inspection du camion enregistrée avec succès !")

# ==============================================================================
# 3. FICHE DE GESTION ET SUIVI DU CARBURANT
# ==============================================================================
elif menu == "⛽ Suivi du Carburant":
    st.title("⛽ Fiche de Gestion et Suivi du Carburant")

    with st.form("form_carburant"):
        st.subheader("1. Informations de Ravitaillement")
        c1, c2, c3, c4 = st.columns(4)
        date_ravit = c1.date_input("Date", datetime.date.today())
        heure_ravit = c2.time_input("Heure", datetime.datetime.now().time())
        immat = c3.text_input("N° Immatriculation / Parc")
        chauffeur = c4.text_input("Nom du Chauffeur")
        
        station = st.text_input("Station / Mode de Plein")

        st.markdown("---")
        st.subheader("2. Relevé du Ravitaillement et Consommation")
        
        r1, r2, r3, r4, r5 = st.columns(5)
        km_prec = r1.number_input("Index / Km Précédent", min_value=0.0, step=1.0)
        km_act = r2.number_input("Index / Km Actuel", min_value=0.0, step=1.0)
        volume = r3.number_input("Volume Ajouté (Litres)", min_value=0.0, step=0.1)
        jauge = r4.number_input("Niveau Jauge (%)", min_value=0, max_value=100, value=100)
        num_bon = r5.text_input("N° Bon / Carte")

        st.markdown("---")
        st.subheader("3. Contrôle Réservoir & Procédures Sécurité")
        
        col_sec1, col_sec2 = st.columns(2)
        reservoir_ok = col_sec1.selectbox("Étanchéité / Bouchon / Absence de fuites", ["OK", "NOK"])
        procedure_ok = col_sec2.selectbox("Procédures de sécurité respectées (Arrêt moteur, ticket pris)", ["OK", "NOK"])
        
        st.markdown("---")
        st.subheader("4. Seuil Cible & Éco-Conduite")
        cible_conso = st.number_input("Consommation Cible (L/100km)", value=35.0, step=0.5)

        submit_carb = st.form_submit_button("🧮 Calculer Consommation et Enregistrer")

    if submit_carb:
        dist_parcourue = km_act - km_prec
        if dist_parcourue > 0:
            conso_calc = (volume / dist_parcourue) * 100
            ecart = "Normal" if conso_calc <= cible_conso else "Élevé"
            
            st.markdown(f"""
                <div class="card">
                    <h3>📊 Bilan Consommation Calculé</h3>
                    <p><b>Distance Parcourue :</b> {dist_parcourue:.1f} km</p>
                    <p><b>Consommation Moyenne :</b> <span style="font-size:20px; font-weight:bold; color:{'green' if ecart=='Normal' else 'red'};">{conso_calc:.2f} L/100 km</span></p>
                    <p><b>Écart par rapport à la cible ({cible_conso} L/100km) :</b> <b>{ecart}</b></p>
                </div>
            """, unsafe_allow_html=True)

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
            st.success("✅ Ravitaillement enregistré dans le système !")
        else:
            st.error("❌ Le kilométrage actuel doit être supérieur au kilométrage précédent.")

# ==============================================================================
# 4. HISTORIQUE ET EXPORTS
# ==============================================================================
elif menu == "📂 Historique & Exports":
    st.title("📂 Historique Général des Fiches")

    tab1, tab2 = st.tabs(["📋 Inspections Camions", "⛽ Ravitaillements Carburant"])

    with tab1:
        if st.session_state.inspections_camion:
            df = pd.DataFrame(st.session_state.inspections_camion)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV (Inspections)", csv, "inspections_elget.csv", "text/csv")
        else:
            st.info("Aucune donnée d'inspection enregistrée pour le moment.")

    with tab2:
        if st.session_state.ravitaillements:
            df_r = pd.DataFrame(st.session_state.ravitaillements)
            st.dataframe(df_r, use_container_width=True)
            csv_r = df_r.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV (Carburant)", csv_r, "carburant_elget.csv", "text/csv")
        else:
            st.info("Aucun ravitaillement enregistré pour le moment.")
