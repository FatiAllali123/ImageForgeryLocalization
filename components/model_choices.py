"""Liste des modèles proposés dans l'interface."""
import os

from models.registry import list_models


def visible_models():
    """Modèles affichés à l'utilisateur.

    Le modèle factice (Dummy) reste dans le registre pour les tests,
    mais n'est affiché que si SHOW_DUMMY_MODEL=1 (développement de l'interface).
    """
    show_dummy = os.environ.get("SHOW_DUMMY_MODEL") == "1"
    return [name for name in list_models() if show_dummy or "dummy" not in name.lower()]