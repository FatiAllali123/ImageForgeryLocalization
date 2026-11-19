"""Barre latérale : paramètres secondaires uniquement."""
import streamlit as st


def render_sidebar() -> float:
    """Retourne le seuil choisi (utilisé pour fabriquer le masque binaire)."""
    st.sidebar.header("Paramètres")
    return st.sidebar.slider(
        "Seuil de détection",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
        help="Plus le seuil est haut, plus le masque est restreint aux zones très suspectes.",
    )