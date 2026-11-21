"""Style commun de l'application (CSS, en-tête, titres de section, légende)."""
import streamlit as st

_CSS = """
<style>
/* Contenu sur toute la largeur */
.block-container { padding: 1.2rem 2.5rem 3rem 2.5rem; max-width: 100%; }

/* ---------- Barre d'information (haut) ---------- */
.topbar {
    background: #1d4ed8;
    color: #dbeafe;
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: .4rem;
    font-size: .8rem; font-weight: 500;
    padding: .55rem 1.4rem;
    border-radius: 14px 14px 0 0;
}

/* ---------- Barre de navigation ---------- */
.navbar {
    background: #ffffff;
    border-left: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .6rem;
    padding: .95rem 1.4rem;
}
.nav-brand { font-weight: 700; font-size: 1.15rem; color: #0f172a; letter-spacing: -.01em; }
.nav-brand span { color: #1d4ed8; }
.nav-items { display: flex; gap: 1.6rem; }
.nav-item {
    color: #334155; font-size: .78rem; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase;
}

/* ---------- En-tête ---------- */
.hero {
    background: #eff6ff;
    border: 1px solid #dbeafe;
    border-radius: 0 0 14px 14px;
    padding: 2.8rem 3rem;
    display: flex; align-items: center; justify-content: space-between; gap: 2rem;
}
.hero-text { flex: 1 1 auto; min-width: 0; }
.hero-label { color: #1d4ed8; font-size: .95rem; font-weight: 600; margin: 0 0 .7rem 0; }
.hero h1 {
    color: #0f172a !important;
    font-size: 2.6rem; font-weight: 700; line-height: 1.15;
    letter-spacing: -.02em;
    margin: 0 0 1rem 0; padding: 0;
}
.hero h1 .accent { color: #1d4ed8; }
.hero p {
    color: #475569 !important;
    font-size: 1.02rem; line-height: 1.6; max-width: 560px;
    margin: 0 0 1.6rem 0;
}
.hero-cta {
    display: inline-block;
    background: #1d4ed8; color: #ffffff !important;
    font-weight: 600; font-size: .95rem;
    padding: .8rem 1.6rem;
    border-radius: 999px;
    text-decoration: none !important;
    box-shadow: 0 6px 16px rgba(29, 78, 216, .28);
}
.hero-cta:hover { background: #1e40af; }

/* Illustration (CSS) : image avec zone suspecte */
.hero-visual {
    position: relative; flex: 0 0 360px; height: 260px;
    border-radius: 18px;
    background: linear-gradient(145deg, #dbeafe 0%, #e2e8f0 100%);
    border: 1px solid #bfdbfe;
    overflow: hidden;
}
.hv-blob {
    position: absolute; left: 36%; top: 26%;
    width: 160px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle, rgba(220,38,38,.85) 0%, rgba(250,204,21,.6) 42%, rgba(34,197,94,0) 75%);
}
.hv-box {
    position: absolute; left: 33%; top: 22%;
    width: 190px; height: 150px;
    border: 2px dashed #1d4ed8; border-radius: 14px;
}
.hv-tag {
    position: absolute;
    background: #ffffff; border: 1px solid #bfdbfe; border-radius: 8px;
    padding: .3rem .65rem;
    font-size: .74rem; font-weight: 600; color: #1e3a8a;
    box-shadow: 0 2px 8px rgba(15, 23, 42, .1);
}
.hv-tag.t1 { left: 5%; top: 8%; }
.hv-tag.t2 { right: 5%; bottom: 8%; }
@media (max-width: 900px) { .hero-visual { display: none; } }

/* ---------- Cartes des 3 étapes ---------- */
.steps { display: flex; gap: 1rem; margin: 1.2rem 0 1.6rem 0; }
.step {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, .04);
}
.step-num {
    width: 2.2rem; height: 2.2rem; border-radius: 10px;
    background: #eff6ff; color: #1d4ed8;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; margin-bottom: .75rem;
}
.step-title { font-weight: 600; color: #0f172a; font-size: 1rem; margin-bottom: .15rem; }
.step-text  { color: #64748b; font-size: .85rem; }
.step.accent { background: #1d4ed8; border-color: #1d4ed8; }
.step.accent .step-num   { background: rgba(255, 255, 255, .18); color: #ffffff; }
.step.accent .step-title { color: #ffffff; }
.step.accent .step-text  { color: #dbeafe; }
@media (max-width: 800px) { .steps { flex-direction: column; } }

/* ---------- Titres de section ---------- */
.section-head { margin: .2rem 0 1rem 0; }
.section-label {
    display: flex; align-items: center; gap: .6rem;
    color: #1d4ed8; font-size: .75rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase;
    margin-bottom: .35rem;
}
.section-label .line { display: inline-block; width: 28px; height: 2px; background: #1d4ed8; }
.section-title { color: #0f172a; font-size: 1.6rem; font-weight: 700; letter-spacing: -.01em; margin: 0; line-height: 1.25; }
.section-title .accent { color: #1d4ed8; }

/* ---------- Cartes de contenu ---------- */
[class*="st-key-card"] {
    background: #ffffff;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 2px 10px rgba(15, 23, 42, .05);
}

/* Zone d'import */
[data-testid="stFileUploaderDropzone"] {
    background: #eff6ff;
    border: 2px dashed #93c5fd;
    border-radius: 14px;
}

/* Aperçu de l'image importée : largeur complète, hauteur limitée */
.st-key-card_import div[data-testid="stImage"] img {
    max-height: 520px; width: 100%; object-fit: contain;
    background: #f1f5f9; border-radius: 10px;
}

/* Boutons */
[data-testid="stBaseButton-primary"] {
    border-radius: 999px; font-weight: 600;
    box-shadow: 0 6px 16px rgba(29, 78, 216, .25);
}
[data-testid="stBaseButton-secondary"] {
    border-radius: 999px; font-weight: 600;
    border: 1.5px solid #1d4ed8; color: #1d4ed8; background: #ffffff;
}
[data-testid="stBaseButton-secondary"]:hover { background: #eff6ff; }

/* Onglets */
button[data-baseweb="tab"] { font-weight: 600; }

/* ---------- Images et légende ---------- */
div[data-testid="stImage"] img { border-radius: 8px; }
.legend { margin: .6rem 0 .2rem 0; }
.legend-bar {
    height: 12px; border-radius: 6px;
    background: linear-gradient(90deg, #00007f, #0000ff, #00ffff, #ffff00, #ff0000, #7f0000);
}
.legend-labels {
    display: flex; justify-content: space-between;
    font-size: .8rem; color: #64748b; margin-top: .2rem;
}

/* ---------- Barre latérale ---------- */
section[data-testid="stSidebar"] { border-right: 1px solid #e2e8f0; }
.brand {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #1d4ed8;
    border-radius: 10px;
    padding: .9rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, .06);
}
.brand-title { color: #0f172a; font-weight: 700; font-size: .95rem; line-height: 1.2; margin: 0; }
.brand-sub   { color: #64748b; font-size: .76rem; line-height: 1.3; margin: .15rem 0 0 0; }
.model-pill {
    display: block;
    background: #eff6ff; color: #1e3a8a;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: .4rem .7rem; margin-bottom: .4rem;
    font-size: .85rem; font-weight: 500;
}
.side-footer {
    color: #64748b; font-size: .75rem; line-height: 1.4;
    border-top: 1px solid #e2e8f0;
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


def render_section(label, title, accent=""):
    """Titre de section : petit trait + étiquette, puis titre dont la fin est en bleu."""
    accent_html = f' <span class="accent">{accent}</span>' if accent else ""
    st.markdown(
        '<div class="section-head">'
        f'<div class="section-label"><span class="line"></span>{label}</div>'
        f'<p class="section-title">{title}{accent_html}</p>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_hero():
    """Barre d'info, navigation, en-tête et cartes des 3 étapes."""
    st.markdown(
        '<div class="topbar">'
        "<span>Détection et localisation de falsifications d'images</span>"
        "<span>Formats acceptés : JPG, JPEG, PNG</span>"
        "</div>"
        '<div class="navbar">'
        '<div class="nav-brand">Image Forgery <span>Localization</span></div>'
        '<div class="nav-items">'
        '<span class="nav-item">Heatmap</span>'
        '<span class="nav-item">Segmentation</span>'
        '<span class="nav-item">Localisation</span>'
        "</div></div>"
        '<div class="hero">'
        '<div class="hero-text">'
        '<p class="hero-label">Image forensics</p>'
        '<h1>Détection et localisation<br><span class="accent">de falsifications d\'images</span></h1>'
        "<p>Visualisez où une image a pu être modifiée : cartes de chaleur et "
        "segmentation des régions suspectes, sans dépendre des métadonnées.</p>"
        '<a class="hero-cta" href="#import">Commencer l\'analyse &nbsp;&darr;</a>'
        "</div>"
        '<div class="hero-visual">'
        '<div class="hv-box"></div><div class="hv-blob"></div>'
        '<span class="hv-tag t1">Image analysée</span>'
        '<span class="hv-tag t2">Zone suspecte</span>'
        "</div></div>"
        '<div class="steps">'
        '<div class="step"><div class="step-num">1</div>'
        '<div class="step-title">Importer</div>'
        '<div class="step-text">Une image JPG, JPEG ou PNG</div></div>'
        '<div class="step accent"><div class="step-num">2</div>'
        '<div class="step-title">Choisir le modèle</div>'
        '<div class="step-text">Et régler le seuil à gauche</div></div>'
        '<div class="step"><div class="step-num">3</div>'
        '<div class="step-title">Analyser</div>'
        '<div class="step-text">Heatmap, masque et superposition</div></div>'
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