"""
Contrat commun entre l'application et tous les modèles de détection.

L'interface (Streamlit) ne connaît QUE ce fichier : elle ne sait pas si elle
parle à FMAE, TruFor ou à un futur modèle.

Conventions (à respecter par tous les adaptateurs) :
  - image d'entrée : np.ndarray uint8, forme (H, W, 3), canaux en RGB
  - heatmap        : np.ndarray float32, forme (H, W), valeurs dans [0, 1]
  - mask           : np.ndarray uint8, forme (H, W), valeurs 0 ou 1
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


def binarize(heatmap: np.ndarray, threshold: float) -> np.ndarray:
    """Transforme une heatmap en masque binaire (0/1) selon un seuil."""
    return (heatmap >= threshold).astype(np.uint8)


@dataclass
class PredictionResult:
    """Résultat standardisé retourné par TOUS les modèles."""

    model_name: str
    heatmap: np.ndarray            # (H, W) float32 dans [0, 1]
    mask: np.ndarray               # (H, W) uint8 dans {0, 1}
    inference_time_s: float        # durée de l'inférence en secondes
    device: str                    # "cpu", "cuda", ou "precomputed"

    threshold: float | None = None         # seuil utilisé pour le masque
    detection_score: float | None = None   # None si le modèle n'en fournit pas
    # Explique ce que représente le score (ex. "Score brut du modèle").
    # Évite de le présenter à tort comme une probabilité calibrée.
    score_description: str | None = None
    is_precomputed: bool = False           # True pour le mode "exemples"
    extra: dict[str, Any] = field(default_factory=dict)  # infos propres au modèle

    def __post_init__(self) -> None:
        # Vérifications : une erreur d'adaptateur est détectée immédiatement.
        if self.heatmap.ndim != 2:
            raise ValueError(f"heatmap doit être 2D (H, W), reçu {self.heatmap.shape}")
        if self.mask.shape != self.heatmap.shape:
            raise ValueError(
                f"mask {self.mask.shape} et heatmap {self.heatmap.shape} "
                "doivent avoir la même taille"
            )
        if not np.isfinite(self.heatmap).all():
            raise ValueError("heatmap contient des NaN ou des valeurs infinies")
        if self.heatmap.min() < -1e-6 or self.heatmap.max() > 1 + 1e-6:
            raise ValueError(
                "heatmap doit être normalisée dans [0, 1] "
                f"(min={self.heatmap.min():.3f}, max={self.heatmap.max():.3f})"
            )
        if not np.isin(self.mask, (0, 1)).all():
            raise ValueError("mask doit contenir uniquement des 0 et des 1")

    @property
    def suspicious_area_percent(self) -> float:
        """Pourcentage de pixels prédits comme suspects (Fonctionnalité 5)."""
        return 100.0 * float(self.mask.mean())


class BaseForgeryModel(ABC):
    """Classe que chaque modèle (FMAE, TruFor, ...) doit hériter."""

    name: str = "base"                       # nom affiché dans l'interface
    default_threshold: float | None = 0.5    # seuil par défaut

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """Dit si le modèle est utilisable (poids présents, dépendances...).
        Retourne (True, "") ou (False, "message expliquant pourquoi")."""

    @abstractmethod
    def load(self) -> None:
        """Charge le modèle et ses poids en mémoire (appelé une seule fois)."""

    @abstractmethod
    def predict(
        self, image_rgb: np.ndarray, threshold: float | None = None
    ) -> PredictionResult:
        """Analyse une image et retourne un PredictionResult."""

    def unload(self) -> None:
        """Libère la mémoire (utile pour ne garder qu'un modèle à la fois)."""

    @staticmethod
    def _validate_image(image_rgb: np.ndarray) -> None:
        """Vérification commune de l'image d'entrée."""
        if not isinstance(image_rgb, np.ndarray):
            raise ValueError("L'image doit être un tableau NumPy")
        if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
            raise ValueError(f"Image attendue (H, W, 3), reçu {image_rgb.shape}")
        if image_rgb.dtype != np.uint8:
            raise ValueError(f"Image attendue en uint8, reçu {image_rgb.dtype}")