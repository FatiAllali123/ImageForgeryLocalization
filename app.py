"""Point d'entrée Streamlit de l'application."""

import hashlib
from dataclasses import replace

import streamlit as st

from components.results_view import show_results
from components.sidebar import render_sidebar
from components.uploader import render_uploader
from models.base_model import binarize
from models.registry import list_models
from services.inference_service import ModelUnavailableError, get_manager

st.set_page_config(
    page_title="Détection de falsifications d'images",
    layout="wide",
)

st.title("Détection et localisation de falsifications d'images")

# 1. Paramètres et import de l'image
threshold = render_sidebar()
image, filename = render_uploader()

if image is None:
    # Plus d'image valide : on oublie l'ancien résultat
    st.session_state.pop("analysis", None)
else:
    # Empreinte de l'image : permet de savoir si le résultat stocké lui correspond
    image_id = hashlib.md5(image.tobytes()).hexdigest()

    # 2. Sélection du modèle et analyse
    model_name = st.selectbox("② Choisir le modèle", list_models())

    if st.button("③ Analyser", type="primary"):
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