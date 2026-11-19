"""Point d'entrée Streamlit. Flux : ① importer -> ② choisir le modèle -> ③ Analyser -> ④ résultats."""
import streamlit as st

from components.sidebar import render_sidebar
from components.uploader import render_uploader
from models.registry import create_model, list_models

st.set_page_config(page_title="Détection de falsifications d'images", layout="wide")
st.title("Détection et localisation de falsifications d'images")

threshold = render_sidebar()
image, filename = render_uploader()

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
                st.subheader("④ Résultats (provisoire)")
                c1, c2, c3 = st.columns(3)
                c1.metric("Surface suspecte", f"{result.suspicious_area_percent:.1f} %")
                c2.metric("Temps d'inférence", f"{result.inference_time_s:.3f} s")
                c3.metric("Seuil utilisé", f"{result.threshold:.2f}")
                if result.is_precomputed:
                    st.info("Résultat pré-calculé (non calculé en direct).")
                st.caption(f"Modèle : {result.model_name} | appareil : {result.device}")
                # Les images (heatmap, masque, superposition) viendront avec
                # services/visualization.py et components/results_view.py.