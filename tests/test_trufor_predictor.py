"""Tests de l'adaptateur TruFor qui ne nécessitent ni poids ni GPU."""
import numpy as np
import pytest

from models.base_model import BaseForgeryModel
from models.trufor.predictor import TruForModel


def test_trufor_follows_the_common_contract():
    model = TruForModel()
    assert isinstance(model, BaseForgeryModel)
    assert model.name == "TruFor"


def test_trufor_unload_is_safe_when_nothing_is_loaded():
    model = TruForModel()
    model.unload()                  # ne doit pas planter
    assert model.model is None


def test_trufor_predict_refuses_before_load():
    model = TruForModel()
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    with pytest.raises(RuntimeError):
        model.predict(image)


def test_trufor_declares_a_size_limit():
    assert TruForModel.max_pixels is not None