"""Style commun de l'application (CSS, en-tête, légende)."""
import streamlit as st

_CSS = """
<style>
.block-container { padding-top: 1.6rem; max-width: 1200px; }

/* ---------- En-tête ---------- */
.hero {
    background: #f0fdfa;
    border: 1px solid #99f6e4;
    border-left: 5px solid #0f766e;
    border-radius: 14px;
    padding: 2rem 2.2rem 1.7rem 2.2rem;
}
.hero-label {
    color: #0f766e;
    font-size: .75rem; font-weight: 600;
    letter-spacing: .14em; text-transform: uppercase;
    margin: 0 0 .7rem 0;
}
.hero h1 {
    color: #0f172a !important;
    font-size: 2.1rem; font-weight: 700; line-height: 1.2;
    letter-spacing: -.01em;
    margin: 0 0 .6rem 0; padding: 0;
}
.hero p {
    color: #475569 !important;
    font-size: 1.02rem; max-width: 720px;
    margin: 0 0 1.1rem 0;
}
.chip {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #99f6e4;
    color: #115e59;
    font-size: .82rem; font-weight: 500;
    padding: .25rem .7rem;
    border-radius: 6px;
    margin: 0 .4rem .4rem 0;
}

/* ---------- Bande des 3 étapes ---------- */
.steps { display: flex; gap: .9rem; margin: 1rem 0 1.4rem 0; }
.step {
    flex: 1;
    display: flex; align-items: center; gap: .8rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: .8rem 1rem;
}
.step-num {
    flex: 0 0 auto;
    width: 2rem; height: 2rem; border-radius: 50%;
    border: 1.5px solid #0f766e; color: #0f766e;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: .95rem;
}
.step-title { font-weight: 600; color: #111827; font-size: .95rem; }
.step-text  { color: #6b7280; font-size: .82rem; }
@media (max-width: 800px) { .steps { flex-direction: column; } }

/* ---------- Images et légende ---------- */
div[data-testid="stImage"] img { border-radius: 8px; }
.legend { margin: .6rem 0 .2rem 0; }
.legend-bar {
    height: 12px; border-radius: 6px;
    background: linear-gradient(90deg, #00007f, #0000ff, #00ffff, #ffff00, #ff0000, #7f0000);
}
.legend-labels {
    display: flex; justify-content: space-between;
    font-size: .8rem; color: #6b7280; margin-top: .2rem;
}

/* ---------- Barre latérale ---------- */
section[data-testid="stSidebar"] { border-right: 1px solid #e5e7eb; }
.brand {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #0f766e;
    border-radius: 10px;
    padding: .9rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(17, 24, 39, .06);
}
.brand-title { color: #111827; font-weight: 700; font-size: .95rem; line-height: 1.2; margin: 0; }
.brand-sub   { color: #6b7280; font-size: .76rem; line-height: 1.3; margin: .15rem 0 0 0; }
.model-pill {
    display: block;
    background: #f3f4f6; color: #111827;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: .4rem .7rem; margin-bottom: .4rem;
    font-size: .85rem; font-weight: 500;
}
.side-footer {
    color: #6b7280; font-size: .75rem; line-height: 1.4;
    border-top: 1px solid #e5e7eb;
    padding-top: .8rem; margin-top: .6rem;
}

/* ---------- Éléments Streamlit par défaut masqués ---------- */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
"""


def inject_css():
    """À appeler une seule fois, au début de app.py."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero():
    """Bandeau d'en-tête et bande des 3 étapes."""
    st.markdown(
        '<div class="hero">'
        '<p class="hero-label">Image forensics</p>'
        "<h1>Détection et localisation de falsifications d'images</h1>"
        "<p>Visualisez où une image a pu être modifiée : cartes de chaleur et "
        "segmentation des régions suspectes, sans dépendre des métadonnées.</p>"
        "<div>"
        '<span class="chip">Heatmap de falsification</span>'
        '<span class="chip">Segmentation des régions</span>'
        '<span class="chip">Copier-coller · Collage · Retouche</span>'
        '<span class="chip">Sans métadonnées</span>'
        "</div></div>"
        '<div class="steps">'
        '<div class="step"><div class="step-num">1</div><div>'
        '<div class="step-title">Importer</div>'
        '<div class="step-text">Une image JPG, JPEG ou PNG</div></div></div>'
        '<div class="step"><div class="step-num">2</div><div>'
        '<div class="step-title">Choisir le modèle</div>'
        '<div class="step-text">Et régler le seuil à gauche</div></div></div>'
        '<div class="step"><div class="step-num">3</div><div>'
        '<div class="step-title">Analyser</div>'
        '<div class="step-text">Heatmap, masque et superposition</div></div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_heatmap_legend():
    """Barre de couleurs : bleu = peu suspect, rouge = très suspect."""
    st.markdown(
        '<div class="legend"><div class="legend-bar"></div>'
        '<div class="legend-labels"><span>Peu suspect</span><span>Très suspect</span></div></div>',
        unsafe_allow_html=True,
    )