"""Adaptateur FMAE -> contrat commun (BaseForgeryModel / PredictionResult).

Le code officiel de FMAE n'est jamais copié ni modifié : il est lu dans
third_party/FMAE (voir config.py). Ce fichier ne fait que l'adapter.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from models.base_model import BaseForgeryModel, PredictionResult
from models.fmae import config as cfg

# Paquets nécessaires à FMAE (vérifiés sans les importer : c'est rapide)
_REQUIRED_PACKAGES = ("torch", "timm", "einops", "albumentations", "cv2")


def _short(path: Path) -> str:
    """Chemin relatif à la racine du projet (plus lisible dans un message)."""
    try:
        return str(path.relative_to(cfg.PROJECT_ROOT))
    except ValueError:
        return str(path)


class FMAEModel(BaseForgeryModel):
    name = "FMAE"
    default_threshold = cfg.DEFAULT_THRESHOLD

    def __init__(self) -> None:
        self._model = None      # modèle PyTorch (rempli par load())
        self._device = None     # "cuda" ou "cpu"
        self._epoch = None      # époque lue dans le checkpoint

    def is_available(self) -> tuple[bool, str]:
        """Vérifie les fichiers et les paquets, sans rien charger en mémoire."""
        required_files = (
            cfg.FMAE_REPO_DIR,
            cfg.MAE_PRETRAIN_PATH,
            cfg.CHECKPOINT_PATH,
            cfg.NOISEPRINT_PATH,
        )
        missing = [_short(p) for p in required_files if not p.exists()]
        if missing:
            return False, "fichiers FMAE introuvables : " + ", ".join(missing)

        absent = [p for p in _REQUIRED_PACKAGES if importlib.util.find_spec(p) is None]
        if absent:
            return False, (
                "paquets manquants : " + ", ".join(absent)
                + " (pip install -r requirements/fmae.txt)"
            )
        return True, ""

    def load(self) -> None:
        raise NotImplementedError("load() sera écrit à l'étape suivante")

    def predict(self, image_rgb: np.ndarray, threshold: float | None = None) -> PredictionResult:
        raise NotImplementedError("predict() sera écrit à l'étape suivante")