"""Composant d'import d'image : ① importer l'image -> aperçu."""
import os

import streamlit as st

from services.image_processing import ImageLoadError, load_image_from_bytes


def _format_size(n_bytes):
    """Poids lisible : 850 Ko, 2.4 Mo."""
    if n_bytes < 1024 * 1024:
        return f"{n_bytes / 1024:.0f} Ko"
    return f"{n_bytes / (1024 * 1024):.1f} Mo"


def render_uploader():
    """Affiche le bouton d'import et l'aperçu sur toute la largeur.
    Retourne (image_rgb, nom_du_fichier), ou (None, None) si rien de valide."""
    file = st.file_uploader(
        "Importer une image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )
    if file is None:
        return None, None

    try:
        image = load_image_from_bytes(file.getvalue(), file.name)
    except ImageLoadError as e:
        st.error(str(e))        # message en français, écrit à l'étape 3
        return None, None

    h, w = image.shape[:2]
    extension = os.path.splitext(file.name)[1].lstrip(".").upper()

    st.markdown(
        f"**{file.name}** &nbsp;·&nbsp; {w} × {h} pixels "
        f"&nbsp;·&nbsp; {_format_size(file.size)} &nbsp;·&nbsp; {extension}"
    )
    st.image(image, width="stretch")
    return image, file.name