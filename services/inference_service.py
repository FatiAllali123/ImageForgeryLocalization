"""Orchestration de l'inférence : un seul modèle chargé en mémoire à la fois.

ModelManager ne dépend pas de Streamlit (testable avec de faux modèles).
get_manager() en garde UNE instance entre les relances de l'application.
"""
from __future__ import annotations

import gc
import threading
from collections.abc import Callable

import numpy as np
import streamlit as st

from models.base_model import BaseForgeryModel, PredictionResult
from models.registry import create_model


class ModelUnavailableError(RuntimeError):
    """Le modèle demandé ne peut pas être utilisé (poids ou paquets manquants...)."""

class ImageTooLargeError(ValueError):
    """L'image dépasse la taille maximale supportée par le modèle."""
    
class ModelManager:
    """Charge un modèle une seule fois et le garde en mémoire."""

    def __init__(self, factory: Callable[[str], BaseForgeryModel] = create_model) -> None:
        self._factory = factory
        self._lock = threading.Lock()   # évite deux analyses simultanées
        self._name: str | None = None
        self._model: BaseForgeryModel | None = None

    @property
    def current_model_name(self) -> str | None:
        return self._name

    def _release(self) -> None:
        """Décharge le modèle courant (libère la mémoire, GPU compris)."""
        if self._model is not None:
            self._model.unload()
        self._model = None
        self._name = None
        gc.collect()

    def _get_loaded_model(self, name: str) -> BaseForgeryModel:
        if self._name == name and self._model is not None:
            return self._model              # déjà chargé : aucun rechargement

        # On vérifie la disponibilité AVANT de toucher au modèle actuel
        model = self._factory(name)
        ok, message = model.is_available()
        if not ok:
            raise ModelUnavailableError(message)

        # Un seul modèle en mémoire : on libère l'ancien avant de charger le nouveau
        self._release()
        try:
            model.load()
        except Exception:
            model.unload()                  # ne laisse rien à moitié chargé
            raise
        self._model, self._name = model, name
        return model



    def analyze(
        self, name: str, image_rgb: np.ndarray, threshold: float | None = None
    ) -> PredictionResult:
        """Charge le modèle si nécessaire, puis analyse l'image."""
        with self._lock:
            model = self._get_loaded_model(name)

            # Garde-fou : certains modèles (TruFor) ne redimensionnent pas l'image
            limit = getattr(model, "max_pixels", None)
            height, width = getattr(image_rgb, "shape", (0, 0))[:2]
            if limit is not None and height * width > limit:
                raise ImageTooLargeError(
                    f"Image trop grande pour {name} : {height * width / 1e6:.1f} Mpx "
                    f"(maximum {limit / 1e6:.1f} Mpx). "
                    "Utilisez une image plus petite ou le modèle FMAE."
                )
            return model.predict(image_rgb, threshold=threshold)


@st.cache_resource(show_spinner=False)
def get_manager() -> ModelManager:
    """Une seule instance du gestionnaire pour toute l'application."""
    return ModelManager()