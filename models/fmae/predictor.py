"""Adaptateur FMAE -> contrat commun (BaseForgeryModel / PredictionResult).

Le code officiel de FMAE n'est jamais copié ni modifié : il est lu dans
third_party/FMAE (voir config.py). Ce fichier ne fait que l'adapter.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import time
import types
from pathlib import Path

import numpy as np

from models.base_model import BaseForgeryModel, PredictionResult, binarize
from models.fmae import config as cfg

# Paquets nécessaires à FMAE (vérifiés sans les importer : c'est rapide)
_REQUIRED_PACKAGES = ("torch", "timm", "einops", "albumentations", "cv2")

# Arguments de forward() lus dans inference.py officiel. Ils ne servent qu'au
# calcul de la loss (inutile en inférence) : on garde les valeurs officielles.
_LOSS_WEIGHTS = {"alpha": 0.3, "beta": 0.7, "gamma": 0}


def _short(path: Path) -> str:
    """Chemin relatif à la racine du projet (plus lisible dans un message)."""
    try:
        return str(path.relative_to(cfg.PROJECT_ROOT))
    except ValueError:
        return str(path)


def _prepare_official_imports() -> None:
    """Rend le code officiel importable, SANS le modifier."""
    # 1. Le code officiel importe 'jpegio' (utile seulement pour lire des
    #    coefficients JPEG, inutile à l'inférence). S'il n'est pas installé,
    #    on fournit un module vide pour que l'import réussisse.
    if "jpegio" not in sys.modules and importlib.util.find_spec("jpegio") is None:
        sys.modules["jpegio"] = types.ModuleType("jpegio")

    # 2. Le dossier du code officiel doit être dans le chemin d'import
    repo = str(cfg.FMAE_REPO_DIR)
    if repo not in sys.path:
        sys.path.insert(0, repo)


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
        """Charge FMAE une seule fois (GPU si disponible, sinon CPU)."""
        if self._model is not None:
            return  # déjà chargé

        ok, message = self.is_available()
        if not ok:
            raise RuntimeError(f"FMAE indisponible : {message}")

        import torch  # import tardif : seulement quand on charge vraiment

        _prepare_official_imports()
        from IMDLBenCo import MODELS  # code officiel (third_party/FMAE)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Construction du modèle. MoE.py charge noiseprint.pth avec un chemin
        # RELATIF : on se place temporairement dans le dossier du code officiel,
        # puis on revient TOUJOURS au dossier d'origine (finally).
        previous_dir = os.getcwd()
        try:
            os.chdir(cfg.FMAE_REPO_DIR)
            model = MODELS.get("FMAE")(vit_pretrain_path=str(cfg.MAE_PRETRAIN_PATH))
        finally:
            os.chdir(previous_dir)

        # Checkpoint de localisation. weights_only=False exécute du code pickle :
        # acceptable ici car c'est le fichier officiel, de source connue.
        checkpoint = torch.load(cfg.CHECKPOINT_PATH, map_location="cpu", weights_only=False)
        model.load_state_dict(checkpoint["model"], strict=True)

        try:
            model.to(device)
        except torch.cuda.OutOfMemoryError as exc:
            del model
            torch.cuda.empty_cache()
            raise RuntimeError(
                "Mémoire GPU insuffisante pour charger FMAE. "
                "Fermez les autres applications utilisant le GPU."
            ) from exc

        model.eval()  # mode inférence (obligatoire)

        self._model = model
        self._device = device
        self._epoch = int(checkpoint["epoch"])

    def unload(self) -> None:
        """Libère la mémoire (pour ne garder qu'un modèle à la fois)."""
        self._model = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    def predict(self, image_rgb: np.ndarray, threshold: float | None = None) -> PredictionResult:
        """Analyse une image RGB (H, W, 3) uint8 et retourne un PredictionResult."""
        self._validate_image(image_rgb)
        threshold = self.default_threshold if threshold is None else threshold

        if self._model is None:
            self.load()

        import cv2
        import torch

        _prepare_official_imports()
        from IMDLBenCo.transforms import get_albu_transforms  # code officiel

        height, width = image_rgb.shape[:2]

        # 1. Prétraitement OFFICIEL : Resize 512x512 + normalisation ImageNet.
        #    Le masque nul est exigé par l'interface albumentations du code
        #    officiel (comme dans notre script de test).
        transform = get_albu_transforms(
            type_="resize", output_size=(cfg.IMAGE_SIZE, cfg.IMAGE_SIZE)
        )
        zero_mask = np.zeros((height, width), dtype=np.uint8)
        transformed = transform(image=image_rgb, masks=[zero_mask])

        # 2. Inférence
        device = self._device
        try:
            image_tensor = transformed["image"].unsqueeze(0).to(device)
            mask_tensor = transformed["masks"][0].float().unsqueeze(0).unsqueeze(0).to(device)
            label_tensor = torch.zeros((1,), dtype=torch.float32, device=device)

            if device == "cuda":
                torch.cuda.synchronize()    # attendre la fin des tâches GPU en cours
            start = time.perf_counter()
            with torch.inference_mode():
                output = self._model(
                    image=image_tensor,
                    mask=mask_tensor,
                    edge_mask=None,
                    label=label_tensor,
                    epoch=self._epoch,
                    **_LOSS_WEIGHTS,
                )
            if device == "cuda":
                torch.cuda.synchronize()    # sinon le chronomètre s'arrête trop tôt
            elapsed = time.perf_counter() - start
        except torch.cuda.OutOfMemoryError as exc:
            torch.cuda.empty_cache()
            raise RuntimeError(
                "Mémoire GPU insuffisante pendant l'analyse. "
                "Fermez les autres applications utilisant le GPU."
            ) from exc

        # 3. Post-traitement : carte (512x512) -> taille d'origine, valeurs dans [0, 1]
        prediction = output["pred_mask"][0, 0].detach().cpu().numpy()
        heatmap = cv2.resize(prediction, (width, height), interpolation=cv2.INTER_LINEAR)
        heatmap = np.clip(heatmap, 0.0, 1.0).astype(np.float32)

        # 4. Masque binaire : le seuil est un réglage (le modèle n'en impose pas)
        mask = binarize(heatmap, threshold)

        return PredictionResult(
            model_name=self.name,
            heatmap=heatmap,
            mask=mask,
            inference_time_s=elapsed,
            device=self._device,
            threshold=threshold,
            detection_score=None,       # checkpoint de LOCALISATION : pas de score fiable
            score_description=None,
            extra={
                "epoch": self._epoch,
                "input_size": cfg.IMAGE_SIZE,
                "original_size": (height, width),
            },
        )