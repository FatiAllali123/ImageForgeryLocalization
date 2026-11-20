
"""Registre des modèles : associe un nom à une façon de créer le modèle.
Pour ajouter un modèle plus tard : créer son dossier + ajouter UNE ligne ici."""

from __future__ import annotations

from collections.abc import Callable

from models.base_model import BaseForgeryModel
from models.dummy.predictor import DummyModel
from models.fmae.predictor import FMAEModel
from models.trufor.predictor import TruForModel

# nom affiché -> fonction qui crée le modèle.
# Dummy reste en premier : certains tests s'appuient sur list_models()[0].
_FACTORIES: dict[str, Callable[[], BaseForgeryModel]] = {
    DummyModel.name: DummyModel,
    FMAEModel.name: FMAEModel,
    TruForModel.name: TruForModel,
}


def list_models() -> list[str]:
    """Noms des modèles disponibles (pour la liste déroulante de l'interface)."""
    return list(_FACTORIES.keys())


def create_model(name: str) -> BaseForgeryModel:
    """Crée une instance du modèle demandé (sans charger les poids)."""
    if name not in _FACTORIES:
        raise KeyError(f"Modèle inconnu : '{name}'. Disponibles : {list_models()}")
    return _FACTORIES[name]()
