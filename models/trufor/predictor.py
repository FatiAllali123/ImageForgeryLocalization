
"""Adaptateur du modèle officiel TruFor pour notre application."""

from __future__ import annotations

import os
import gc
import sys
import time
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F

from models.base_model import BaseForgeryModel, PredictionResult, binarize
from models.trufor.config import TRUFOR_ROOT, TRUFOR_WEIGHTS, DEVICE


class TruForModel(BaseForgeryModel):
    name = "TruFor"
    # Limite mesurée sur Quadro T1000 (4 Go) : 1,7 Mpx = 4 s ; 3 Mpx = 12 s avec
    # débordement mémoire ; 8 Mpx = plantage. TruFor ne redimensionne pas l'image.
    max_pixels = 2_000_000
    
    default_threshold = 0.5

    def __init__(self):
        self.model = None
        self.device = DEVICE

    def is_available(self) -> tuple[bool, str]:
        if not TRUFOR_ROOT.exists():
            return False, f"Code source TruFor introuvable : {TRUFOR_ROOT}"

        if not TRUFOR_WEIGHTS.exists():
            return False, f"Poids TruFor introuvables : {TRUFOR_WEIGHTS}"

        return True, ""

    def load(self) -> None:
        available, message = self.is_available()
        if not available:
            raise RuntimeError(message)

        root = str(TRUFOR_ROOT)

        if root not in sys.path:
            sys.path.insert(0, root)

        from lib.config import config, update_config
        from lib.utils import get_model

        args = SimpleNamespace(
            experiment="trufor_ph3",
            gpu=[-1],
            opts=[],
        )

        # TruFor utilise des chemins relatifs à son dépôt.
        previous_directory = os.getcwd()

        try:
            os.chdir(root)

            update_config(config, args)

            self.model = get_model(config)

            checkpoint = torch.load(
                TRUFOR_WEIGHTS,
                map_location=self.device,
                weights_only=False,
            )

            self.model.load_state_dict(checkpoint["state_dict"])
            self.model.to(self.device)
            self.model.eval()

        finally:
            os.chdir(previous_directory)

    def unload(self) -> None:
        """Libère la mémoire (un seul modèle à la fois sur le GPU)."""
        self.model = None
        gc.collect()    # détruit les tenseurs AVANT de vider le cache CUDA
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def predict(
        self,
        image_rgb: np.ndarray,
        threshold: float | None = None,
    ) -> PredictionResult:

        if self.model is None:
            raise RuntimeError("Le modèle TruFor n'est pas encore chargé.")

        self._validate_image(image_rgb)

        threshold = (
            self.default_threshold if threshold is None else threshold
        )

        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Le seuil doit être compris entre 0 et 1.")

        # Conversion de l'image au format attendu par TruFor.
        image_tensor = torch.from_numpy(
            image_rgb.transpose(2, 0, 1)
        ).float().unsqueeze(0) / 256.0

        image_tensor = image_tensor.to(self.device)

        # Inférence.
        start_time = time.perf_counter()

        with torch.no_grad():
            pred, conf, det, npp = self.model(
                image_tensor,
                save_np=False,
            )

            # Carte de localisation : probabilité de la classe falsifiée.
            pred = torch.squeeze(pred, 0)
            heatmap = F.softmax(pred, dim=0)[1]
            heatmap = heatmap.cpu().numpy().astype(np.float32)

            # Score global de détection.
            detection_score = None
            if det is not None:
                detection_score = torch.sigmoid(det).item()

            # Carte de confiance.
            confidence_map = None
            if conf is not None:
                confidence_map = (
                    torch.sigmoid(conf).squeeze().cpu().numpy()
                )

        inference_time = time.perf_counter() - start_time

        # Création du masque binaire.
        mask = binarize(heatmap, threshold)

        return PredictionResult(
            model_name=self.name,
            heatmap=heatmap,
            mask=mask,
            inference_time_s=inference_time,
            device=self.device,
            threshold=threshold,
            detection_score=detection_score,
                        score_description=(
                "Score du modèle (élevé = plutôt falsifiée). "
                "Ce n'est pas une probabilité calibrée."
            ),
            extra={
                "confidence_map": confidence_map,
            },
        )
