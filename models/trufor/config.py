
import os
from pathlib import Path

# Chemin vers le dépôt officiel TruFor.
# Chaque utilisateur peut définir son propre chemin.
DEFAULT_TRUFOR_ROOT = Path.home() / "TruFor" / "TruFor_train_test"

TRUFOR_ROOT = Path(
    os.getenv("TRUFOR_ROOT", str(DEFAULT_TRUFOR_ROOT))
)

# Chemin vers les poids du modèle.
DEFAULT_TRUFOR_WEIGHTS = (
    TRUFOR_ROOT / "pretrained_models" / "trufor.pth.tar"
)

TRUFOR_WEIGHTS = Path(
    os.getenv("TRUFOR_WEIGHTS", str(DEFAULT_TRUFOR_WEIGHTS))
)

# Périphérique d'exécution.
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
