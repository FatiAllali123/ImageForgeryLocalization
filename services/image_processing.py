"""Lecture et validation des images envoyées par l'utilisateur.

Sortie garantie : np.ndarray uint8, forme (H, W, 3), canaux RGB
(le format du contrat commun, voir models/base_model.py).

On utilise Pillow (et non OpenCV) pour lire : Pillow donne directement du RGB,
alors qu'OpenCV donne du BGR (piège classique).

IMPORTANT : on ne redimensionne JAMAIS l'image ici. Redimensionner détruit
les traces de falsification (artefacts JPEG, bruit). Si l'image est trop
grande, on la REFUSE avec un message clair.
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

# --- Limites (faciles à modifier) ---
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_FORMATS = {"JPEG", "PNG"}          # format RÉEL détecté par Pillow
MAX_FILE_BYTES = 20 * 1024 * 1024          # 20 Mo
MAX_PIXELS = 25_000_000                    # 25 mégapixels (~5000 x 5000)
MIN_SIDE = 32                              # côté minimum en pixels


class ImageLoadError(ValueError):
    """Erreur de lecture d'image. Son message est affichable tel quel à l'utilisateur."""


def load_image_from_bytes(data: bytes, filename: str = "image") -> np.ndarray:
    """Valide puis décode une image. Retourne un tableau RGB uint8 (H, W, 3)."""
    # 1) Extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ImageLoadError(
            f"Format '{ext or 'inconnu'}' non accepté. Utilisez JPG, JPEG ou PNG."
        )

    # 2) Taille du fichier
    if len(data) == 0:
        raise ImageLoadError("Le fichier est vide.")
    if len(data) > MAX_FILE_BYTES:
        raise ImageLoadError(
            f"Fichier trop lourd ({len(data) / 1e6:.1f} Mo). "
            f"Maximum : {MAX_FILE_BYTES // (1024 * 1024)} Mo."
        )

    # 3) Ouverture (lit seulement l'en-tête : taille et format, pas encore les pixels)
    try:
        img = Image.open(io.BytesIO(data))
    except UnidentifiedImageError:
        raise ImageLoadError("Fichier illisible : ce n'est pas une image valide.")
    except Exception:  # ex. image « bombe de décompression »
        raise ImageLoadError("Image illisible ou dangereusement grande.")

    # 4) Le CONTENU doit vraiment être du JPEG/PNG (pas un GIF renommé en .png)
    if img.format not in ALLOWED_FORMATS:
        raise ImageLoadError(
            f"Le contenu du fichier est de type '{img.format}', "
            "pas JPEG ni PNG (même si l'extension le prétend)."
        )

    # 5) Dimensions, vérifiées AVANT de décoder les pixels (économise la mémoire)
    width, height = img.size
    if min(width, height) < MIN_SIDE:
        raise ImageLoadError(
            f"Image trop petite ({width}x{height}). Minimum : {MIN_SIDE} pixels de côté."
        )
    if width * height > MAX_PIXELS:
        raise ImageLoadError(
            f"Image trop grande ({width}x{height} = {width * height / 1e6:.1f} Mpx). "
            f"Maximum : {MAX_PIXELS / 1e6:.0f} Mpx."
        )

    # 6) Décodage réel des pixels (détecte les fichiers tronqués/corrompus)
    try:
        img.load()
    except Exception:
        raise ImageLoadError("Image corrompue : impossible de décoder les pixels.")

    # 7) Conversion en RGB (gère niveaux de gris, palette, RGBA, CMYK...)
    rgb = img.convert("RGB")
    return np.asarray(rgb, dtype=np.uint8).copy()   # .copy() = tableau modifiable


def load_image_from_path(path: str | Path) -> np.ndarray:
    """Même chose, depuis un fichier sur le disque (utile pour les tests et les exemples)."""
    path = Path(path)
    if not path.is_file():
        raise ImageLoadError(f"Fichier introuvable : {path}")
    return load_image_from_bytes(path.read_bytes(), path.name)