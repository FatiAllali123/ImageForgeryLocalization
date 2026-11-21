"""Configuration de FMAE : chemins et paramètres.

Aucun chemin absolu : tout est calculé à partir de la racine du projet.
"""
from pathlib import Path

# Racine du projet = 3 niveaux au-dessus de ce fichier (models/fmae/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Code officiel de FMAE, cloné dans third_party/ (ignoré par Git, jamais modifié)
FMAE_REPO_DIR = PROJECT_ROOT / "third_party" / "FMAE"

# Poids (ignorés par Git, à placer dans weights/fmae/)
WEIGHTS_DIR = PROJECT_ROOT / "weights" / "fmae"
MAE_PRETRAIN_PATH = WEIGHTS_DIR / "mae_pretrain_vit_base.pth"   # ~327 Mo
CHECKPOINT_PATH = WEIGHTS_DIR / "checkpoint-25.pth"             # ~390 Mo

# Le code officiel charge ce fichier avec un chemin RELATIF (MoE.py) :
# il faut donc exécuter le chargement depuis FMAE_REPO_DIR.
NOISEPRINT_PATH = FMAE_REPO_DIR / "IMDLBenCo" / "model_zoo" / "FMAE" / "noiseprint.pth"

# Paramètres du modèle (lus dans le code officiel et dans notre script de test)
IMAGE_SIZE = 512            # le modèle travaille en 512 x 512

# Seuil par défaut : valeur utilisée dans NOTRE script de test.
# Ce n'est pas une valeur officielle du modèle : l'utilisateur peut la changer.
DEFAULT_THRESHOLD = 0.5