"""Registre des modèles : associe un nom à une façon de créer le modèle.
Pour ajouter un modèle plus tard : créer son dossier + ajouter UNE ligne ici."""
from __future__ import annotations

from collections.abc import Callable

from models.base_model import BaseForgeryModel
from models.dummy.predictor import DummyModel

# nom affiché -> fonction qui crée le modèle.
# FMAE et TruFor seront ajoutés ici aux étapes suivantes.
_FACTORIES: dict[str, Callable[[], BaseForgeryModel]] = {
    DummyModel.name: DummyModel,
}


def list_models() -> list[str]:
    """Noms des modèles disponibles (pour la liste déroulante de l'interface)."""
    return list(_FACTORIES.keys())


def create_model(name: str) -> BaseForgeryModel:
    """Crée une instance du modèle demandé (sans charger les poids)."""
    if name not in _FACTORIES:
        raise KeyError(f"Modèle inconnu : '{name}'. Disponibles : {list_models()}")
    return _FACTORIES[name]()