"""Visualisation des résultats de détection de falsification.

Toutes les fonctions respectent le contrat commun (models/base_model.py) :
- image   : np.ndarray uint8, forme (H, W, 3), canaux RGB
- heatmap : np.ndarray float32, forme (H, W), valeurs dans [0, 1]
- mask    : np.ndarray uint8,   forme (H, W), valeurs 0 ou 1
Les fonctions ne modifient jamais leurs arguments : elles renvoient un nouveau tableau.
"""
import io

import numpy as np
from PIL import Image

# Rouge utilisé pour la superposition du masque
RED = (255, 0, 0)


# ----------------------------- vérifications -----------------------------
def _check_image(image_rgb):
    if (not isinstance(image_rgb, np.ndarray) or image_rgb.dtype != np.uint8
            or image_rgb.ndim != 3 or image_rgb.shape[2] != 3):
        raise ValueError("image_rgb doit être un tableau uint8 de forme (H, W, 3)")


def _check_heatmap(heatmap):
    if not isinstance(heatmap, np.ndarray) or heatmap.ndim != 2:
        raise ValueError("heatmap doit être un tableau 2D (H, W)")
    if not np.isfinite(heatmap).all():
        raise ValueError("heatmap contient des NaN ou des valeurs infinies")
    if heatmap.min() < 0 or heatmap.max() > 1:
        raise ValueError("heatmap doit avoir des valeurs dans [0, 1]")


def _check_mask(mask):
    if not isinstance(mask, np.ndarray) or mask.ndim != 2:
        raise ValueError("mask doit être un tableau 2D (H, W)")
    if not np.isin(mask, (0, 1)).all():
        raise ValueError("mask doit contenir uniquement 0 ou 1")


def _check_same_size(image_rgb, other):
    if image_rgb.shape[:2] != other.shape[:2]:
        raise ValueError(
            f"tailles différentes : image {image_rgb.shape[:2]} / carte {other.shape[:2]}")


def _check_alpha(alpha):
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha doit être entre 0 et 1")


# ------------------------------ fonctions publiques ------------------------------
def colorize_heatmap(heatmap):
    """Heatmap [0, 1] -> image RGB uint8 (bleu = peu suspect, rouge = très suspect)."""
    _check_heatmap(heatmap)
    x = heatmap.astype(np.float32)
    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).round().astype(np.uint8)


def overlay_heatmap(image_rgb, heatmap, alpha=0.5):
    """Superpose la heatmap colorée sur toute l'image."""
    _check_image(image_rgb)
    _check_heatmap(heatmap)
    _check_same_size(image_rgb, heatmap)
    _check_alpha(alpha)
    colored = colorize_heatmap(heatmap).astype(np.float32)
    out = (1 - alpha) * image_rgb.astype(np.float32) + alpha * colored
    return np.clip(out.round(), 0, 255).astype(np.uint8)


def overlay_mask(image_rgb, mask, color=RED, alpha=0.5):
    """Colorie en rouge (transparent) uniquement les pixels où mask == 1."""
    _check_image(image_rgb)
    _check_mask(mask)
    _check_same_size(image_rgb, mask)
    _check_alpha(alpha)
    out = image_rgb.astype(np.float32)
    region = mask.astype(bool)
    out[region] = (1 - alpha) * out[region] + alpha * np.array(color, dtype=np.float32)
    return np.clip(out.round(), 0, 255).astype(np.uint8)


def mask_to_255(mask):
    """Masque 0/1 -> 0/255, pour l'affichage et l'export en PNG."""
    _check_mask(mask)
    return (mask * 255).astype(np.uint8)


def to_png_bytes(array):
    """Tableau uint8 (H, W) ou (H, W, 3) -> octets PNG (pour un bouton de téléchargement)."""
    if not isinstance(array, np.ndarray) or array.dtype != np.uint8 or array.ndim not in (2, 3):
        raise ValueError("array doit être un tableau uint8 de forme (H, W) ou (H, W, 3)")
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="PNG")
    return buffer.getvalue()