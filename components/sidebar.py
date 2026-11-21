"""Barre latérale : paramètres et informations d'aide."""
import streamlit as st

from components.model_choices import visible_models


def render_sidebar() -> float:
    """Retourne le seuil choisi (utilisé pour fabriquer le masque binaire)."""
    # Carte de marque
    st.sidebar.markdown(
        '<div class="brand">'
        '<p class="brand-title">Image Forgery Localization</p>'
        '<p class="brand-sub">Localiser les zones modifiées d\'une image</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    # Paramètre
    st.sidebar.subheader("Paramètres")
    threshold = st.sidebar.slider(
        "Seuil de détection",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
        help="Plus le seuil est haut, plus le masque est restreint aux zones très suspectes.",
    )
    st.sidebar.caption(
        "Le seuil transforme la heatmap en masque. "
        "Le modifier ne relance pas le modèle."
    )

    st.sidebar.divider()

    # Informations utiles
    with st.sidebar.expander("À quoi sert cette application ?"):
        st.markdown(
            "Les images modifiées circulent partout (réseaux sociaux, presse, dossiers). "
            "Les métadonnées d'une image peuvent être effacées ou falsifiées : "
            "elles ne suffisent donc pas à vérifier son authenticité.\n\n"
            "Cette application analyse **les pixels** de l'image avec des modèles "
            "de Deep Learning, et montre **où** elle semble avoir été modifiée."
        )

    with st.sidebar.expander("Comment l'utiliser ?"):
        st.markdown(
            "1. Importez une image JPG, JPEG ou PNG.\n"
            "2. Choisissez un modèle.\n"
            "3. Cliquez sur **Analyser**.\n"
            "4. Ajustez le seuil pour affiner le masque.\n"
            "5. Téléchargez la heatmap, le masque ou la superposition."
        )

    with st.sidebar.expander("Comment lire les résultats ?"):
        st.markdown(
            "- **Heatmap** : bleu = peu suspect, rouge = très suspect.\n"
            "- **Masque** : pixels dont la valeur dépasse le seuil.\n"
            "- **Zone suspecte** : part de l'image couverte par le masque.\n"
            "- **Score** : indice donné par le modèle, pas une probabilité."
        )

    with st.sidebar.expander("Limites à connaître"):
        st.markdown(
            "- Un résultat est un **indice**, pas une preuve de falsification.\n"
            "- Les modèles localisent une zone suspecte : ils ne disent pas "
            "quel type de manipulation a été utilisé.\n"
            "- Les très petites retouches sont difficiles à détecter.\n"
            "- Une image authentique peut aussi déclencher de fausses alertes.\n"
            "- Une forte compression ou un redimensionnement peut dégrader l'analyse."
        )

    # Modèles disponibles
    st.sidebar.markdown("**Modèles disponibles**")
    models = visible_models()
    if models:
        pills = "".join(f'<span class="model-pill">{name}</span>' for name in models)
        st.sidebar.markdown(pills, unsafe_allow_html=True)
    else:
        st.sidebar.caption("Aucun modèle disponible pour le moment.")

    # Pied de page
    st.sidebar.markdown(
        '<div class="side-footer">'
        "Les images importées ne sont pas conservées après l'analyse."
        "</div>",
        unsafe_allow_html=True,
    )
    return threshold