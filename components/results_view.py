"""Affichage des résultats de détection dans Streamlit."""

import streamlit as st

from components.style import render_heatmap_legend, render_section
from services.visualization import (
    colorize_heatmap,
    mask_to_255,
    overlay_heatmap,
    overlay_mask,
    to_png_bytes,
)


def show_results(image_rgb, result):
    """Affiche les résultats de la prédiction."""

    # 1. Préparer les visualisations
    heatmap_rgb = colorize_heatmap(result.heatmap)
    heatmap_overlay = overlay_heatmap(image_rgb, result.heatmap)
    mask = mask_to_255(result.mask)
    mask_overlay = overlay_mask(image_rgb, result.mask)

    # 2. Résumé des résultats
    st.markdown("<br>", unsafe_allow_html=True)
    render_section("Résultats", "Résultats de", "l'analyse")

    has_score = result.detection_score is not None
    columns = st.columns(4 if has_score else 3)

    columns[0].metric("Modèle utilisé", result.model_name, border=True)
    columns[1].metric("Temps d'inférence", f"{result.inference_time_s:.2f} s", border=True)
    columns[2].metric("Zone suspecte", f"{result.suspicious_area_percent:.2f} %", border=True)
    if has_score:
        columns[3].metric(
            result.score_description or "Score de détection",
            f"{result.detection_score:.4f}",
            help="Indice fourni par le modèle : ce n'est pas une probabilité calibrée.",
            border=True,
        )

    badges = []
    if result.threshold is not None:
        badges.append(f":blue-badge[Seuil : {result.threshold:.2f}]")
    if result.device:
        badges.append(f":gray-badge[Appareil : {result.device}]")
    if badges:
        st.markdown(" ".join(badges))

    if result.is_precomputed:
        st.info("Résultat pré-calculé : l'analyse n'a pas été exécutée en direct.")

    # 3. Visualisations (onglets)
    with st.container(border=True, key="card_viz"):
        render_section("Visualisation", "Visualisation des", "résultats")
        tab_overview, tab_details = st.tabs(["Vue d'ensemble", "Détails"])

        with tab_overview:
            col1, col2, col3 = st.columns(3)
            col1.image(image_rgb, caption="Image originale", width="stretch")
            col2.image(heatmap_overlay, caption="Image avec heatmap", width="stretch")
            col3.image(mask_overlay, caption="Masque superposé sur l'image", width="stretch")
            render_heatmap_legend()

        with tab_details:
            col1, col2 = st.columns(2)
            col1.image(heatmap_rgb, caption="Heatmap : zones suspectes", width="stretch")
            col2.image(mask, caption="Masque binaire", width="stretch")
            render_heatmap_legend()

    # 4. Téléchargement des résultats
    with st.container(border=True, key="card_download"):
        render_section("Export", "Télécharger les", "résultats")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "Télécharger la heatmap",
                data=to_png_bytes(heatmap_rgb),
                file_name="heatmap.png",
                mime="image/png",
                width="stretch",
            )

        with col2:
            st.download_button(
                "Télécharger le masque",
                data=to_png_bytes(mask),
                file_name="mask.png",
                mime="image/png",
                width="stretch",
            )

        with col3:
            st.download_button(
                "Télécharger la superposition",
                data=to_png_bytes(mask_overlay),
                file_name="overlay.png",
                mime="image/png",
                width="stretch",
            )

    st.caption(
        "Les zones rouges indiquent des régions suspectes selon le modèle : "
        "ce n'est pas une preuve de falsification."
    )