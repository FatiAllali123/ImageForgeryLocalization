
"""Point d'entrée Streamlit de l'application."""

import streamlit as st

from components.sidebar import render_sidebar
from components.uploader import render_uploader
from components.results_view import show_results
from models.registry import create_model, list_models


st.set_page_config(
    page_title="Détection de falsifications d'images",
    layout="wide",
)

st.title("Détection et localisation de falsifications d'images")

# 1. Paramètres et import de l'image
threshold = render_sidebar()
image, filename = render_uploader()

# 2. Sélection du modèle et analyse
if image is not None:
    model_name = st.selectbox("② Choisir le modèle", list_models())

    if st.button("③ Analyser", type="primary"):
        model = create_model(model_name)

        available, message = model.is_available()

        if not available:
            st.error(f"Modèle indisponible : {message}")

        else:
            try:
                with st.spinner("Analyse en cours..."):
                    model.load()
                    result = model.predict(image, threshold=threshold)

            except Exception as e:
                st.error(f"Erreur pendant l'analyse : {e}")

            else:
                # 3. Affichage complet des résultats
                show_results(image, result)
