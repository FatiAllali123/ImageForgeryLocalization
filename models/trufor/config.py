
import os
from pathlib import Path

# Racine du projet ImageForgeryLocalization
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dépôt officiel TruFor cloné dans third_party/
DEFAULT_TRUFOR_ROOT = (
    PROJECT_ROOT / "third_party" / "TruFor" / "TruFor_train_test"
)

# Possibilité de personnaliser le chemin avec une variable d'environnement
TRUFOR_ROOT = Path(
    os.getenv("TRUFOR_ROOT", str(DEFAULT_TRUFOR_ROOT))
)

# Poids du modèle
DEFAULT_TRUFOR_WEIGHTS = (
    TRUFOR_ROOT / "pretrained_models" / "trufor.pth.tar"
)

TRUFOR_WEIGHTS = Path(
    os.getenv("TRUFOR_WEIGHTS", str(DEFAULT_TRUFOR_WEIGHTS))
)

# Périphérique d'exécution
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
