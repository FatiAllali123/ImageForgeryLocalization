"""Composant d'import d'image : ① importer l'image -> aperçu."""
import streamlit as st

from services.image_processing import ImageLoadError, load_image_from_bytes


def render_uploader():
    """Affiche le bouton d'import et l'aperçu.
    Retourne (image_rgb, nom_du_fichier), ou (None, None) si rien de valide."""
    file = st.file_uploader("① Importer une image", type=["jpg", "jpeg", "png"])
    if file is None:
        return None, None

    try:
        image = load_image_from_bytes(file.getvalue(), file.name)
    except ImageLoadError as e:
        st.error(str(e))        # message en français, écrit à l'étape 3
        return None, None

    h, w = image.shape[:2]
    st.image(image, caption=f"{file.name} ({w} x {h} pixels)")
    return image, file.name