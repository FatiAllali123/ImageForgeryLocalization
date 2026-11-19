"""Modèle FACTICE : uniquement pour développer et tester l'application.
Il ne détecte aucune falsification (la 'heatmap' est une tache au centre)."""
from __future__ import annotations

import time

import numpy as np

from models.base_model import BaseForgeryModel, PredictionResult, binarize


class DummyModel(BaseForgeryModel):
    name = "Dummy (test, non réel)"
    default_threshold = 0.5

    def is_available(self) -> tuple[bool, str]:
        return True, ""            # pas de poids, toujours disponible

    def load(self) -> None:
        pass                       # rien à charger

    def predict(self, image_rgb, threshold=None) -> PredictionResult:
        self._validate_image(image_rgb)
        threshold = self.default_threshold if threshold is None else threshold

        start = time.perf_counter()
        h, w = image_rgb.shape[:2]

        # Tache gaussienne centrée : valeur 1 au centre, proche de 0 sur les bords
        yy, xx = np.mgrid[0:h, 0:w]
        sigma = 0.15 * min(h, w)
        heatmap = np.exp(
            -((yy - h / 2) ** 2 + (xx - w / 2) ** 2) / (2 * sigma**2)
        ).astype(np.float32)

        mask = binarize(heatmap, threshold)
        elapsed = time.perf_counter() - start

        return PredictionResult(
            model_name=self.name,
            heatmap=heatmap,
            mask=mask,
            inference_time_s=elapsed,
            device="cpu",
            threshold=threshold,
            detection_score=float(heatmap.mean()),
            score_description="Score factice (modèle de test)",
        )