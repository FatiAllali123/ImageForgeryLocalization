
"""Affichage des résultats de détection dans Streamlit."""

import streamlit as st

from services.visualization import (
    colorize_heatmap,
    overlay_heatmap,
    overlay_mask,
    mask_to_255,
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
    st.divider()
    st.header("Résultats de l'analyse")

    col1, col2, col3 = st.columns(3)

    col1.metric("Modèle utilisé", result.model_name)
    col2.metric("Temps d'inférence", f"{result.inference_time_s:.2f} s")
    col3.metric("Zone suspecte", f"{result.suspicious_area_percent:.2f} %")

    details = []

    if result.threshold is not None:
        details.append(f"Seuil : {result.threshold:.2f}")

    if result.device:
        details.append(f"Appareil : {result.device}")

    if details:
        st.caption(" | ".join(details))

    if result.is_precomputed:
        st.info("Résultat pré-calculé : l'analyse n'a pas été exécutée en direct.")

    if result.detection_score is not None:
        label = result.score_description or "Score de détection"
        st.metric(label, f"{result.detection_score:.4f}")

    # 3. Visualisations en grille 2 x 2
    st.subheader("Visualisation des résultats")

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            image_rgb,
            caption="1. Image originale",
            use_container_width=True,
        )
        st.image(
            heatmap_rgb,
            caption="2. Heatmap - zones suspectes",
            use_container_width=True,
        )

    with col2:
        st.image(
            mask,
            caption="3. Masque binaire",
            use_container_width=True,
        )
        st.image(
            heatmap_overlay,
            caption="4. Image avec heatmap",
            use_container_width=True,
        )

    st.image(
        mask_overlay,
        caption="Superposition du masque sur l'image originale",
        use_container_width=True,
    )

    # 4. Téléchargement des résultats
    st.subheader("Télécharger les résultats")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Télécharger la heatmap",
            data=to_png_bytes(heatmap_rgb),
            file_name="heatmap.png",
            mime="image/png",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Télécharger le masque",
            data=to_png_bytes(mask),
            file_name="mask.png",
            mime="image/png",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "Télécharger la superposition",
            data=to_png_bytes(mask_overlay),
            file_name="overlay.png",
            mime="image/png",
            use_container_width=True,
        )
