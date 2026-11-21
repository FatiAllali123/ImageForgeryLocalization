"""Point d'entrée Streamlit de l'application."""

import hashlib
from dataclasses import replace

import streamlit as st

from components.model_choices import visible_models
from components.results_view import show_results
from components.sidebar import render_sidebar
from components.style import inject_css, render_hero, render_section
from components.uploader import render_uploader
from models.base_model import binarize
from services.inference_service import ModelUnavailableError, get_manager

st.set_page_config(
    page_title="Détection de falsifications d'images",
    layout="wide",
)

inject_css()
render_hero()

# 1. Paramètres et import de l'image
threshold = render_sidebar()

# Repère vers lequel le bouton « Commencer l'analyse » fait défiler la page
st.markdown('<div id="import"></div>', unsafe_allow_html=True)

with st.container(border=True, key="card_import"):
    render_section("Étape 1", "Importer", "l'image")
    image, filename = render_uploader()

if image is None:
    # Plus d'image valide : on oublie l'ancien résultat
    st.session_state.pop("analysis", None)
    st.info("Importez une image JPG, JPEG ou PNG pour commencer l'analyse.")
else:
    # Empreinte de l'image : permet de savoir si le résultat stocké lui correspond
    image_id = hashlib.md5(image.tobytes()).hexdigest()

    models = visible_models()
    if not models:
        st.warning("Aucun modèle n'est disponible pour le moment.")
        st.stop()

    # 2. Sélection du modèle et analyse
    with st.container(border=True, key="card_model"):
        render_section("Étapes 2 et 3", "Choisir le modèle", "et analyser")
        col_model, col_button = st.columns([3, 1], vertical_alignment="bottom")
        with col_model:
            model_name = st.selectbox("Modèle", models)
        with col_button:
            analyze = st.button("③ Analyser", type="primary", width="stretch")

    if analyze:
        try:
            with st.spinner(
                "Analyse en cours... (le premier chargement d'un modèle "
                "peut prendre une quinzaine de secondes)"
            ):
                # Le gestionnaire charge le modèle une seule fois et le garde en mémoire
                result = get_manager().analyze(model_name, image, threshold)
        except ModelUnavailableError as e:
            st.session_state.pop("analysis", None)
            st.error(f"Modèle indisponible : {e}")
        except Exception as e:
            st.session_state.pop("analysis", None)
            st.error(f"Erreur pendant l'analyse : {e}")
        else:
            # On garde le résultat (pas l'image) pour les prochaines relances
            st.session_state["analysis"] = {
                "image_id": image_id,
                "result": result,
            }

    # 3. Affichage : hors du bloc du bouton, donc visible à chaque relance
    analysis = st.session_state.get("analysis")
    if analysis is not None and analysis["image_id"] == image_id:
        result = analysis["result"]

        # Si le seuil a changé, on recalcule le masque sans relancer le modèle
        if result.threshold is not None and abs(result.threshold - threshold) > 1e-9:
            result = replace(
                result,
                mask=binarize(result.heatmap, threshold),
                threshold=threshold,
            )

        show_results(image, result)