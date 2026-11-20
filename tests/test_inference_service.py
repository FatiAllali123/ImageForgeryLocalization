import numpy as np
import pytest

from models.base_model import BaseForgeryModel, PredictionResult, binarize
from services.inference_service import ModelManager, ModelUnavailableError


class FakeModel(BaseForgeryModel):
    """Faux modèle : note dans 'events' tout ce qu'on lui demande."""

    default_threshold = 0.5

    def __init__(self, label, events, available=True, fail_load=False):
        self.name = label
        self._events = events
        self._available = available
        self._fail_load = fail_load

    def is_available(self):
        return (True, "") if self._available else (False, "poids absents")

    def load(self):
        self._events.append(f"load:{self.name}")
        if self._fail_load:
            raise RuntimeError("boom")

    def unload(self):
        self._events.append(f"unload:{self.name}")

    def predict(self, image_rgb, threshold=None):
        self._events.append(f"predict:{self.name}")
        h, w = image_rgb.shape[:2]
        heatmap = np.full((h, w), 0.7, dtype=np.float32)
        t = 0.5 if threshold is None else threshold
        return PredictionResult(
            model_name=self.name, heatmap=heatmap, mask=binarize(heatmap, t),
            inference_time_s=0.0, device="cpu", threshold=t,
        )


@pytest.fixture
def events():
    return []


@pytest.fixture
def manager(events):
    def factory(name):
        return FakeModel(name, events, available=(name != "Broken"), fail_load=(name == "Crash"))
    return ModelManager(factory=factory)


IMAGE = np.zeros((20, 30, 3), dtype=np.uint8)


def test_model_is_loaded_only_once(manager, events):
    first = manager.analyze("A", IMAGE)
    manager.analyze("A", IMAGE)
    assert first.model_name == "A"
    assert events.count("load:A") == 1       # chargé une seule fois
    assert events.count("predict:A") == 2    # mais utilisé deux fois


def test_switching_model_unloads_previous_one(manager, events):
    manager.analyze("A", IMAGE)
    manager.analyze("B", IMAGE)
    assert events == ["load:A", "predict:A", "unload:A", "load:B", "predict:B"]
    assert manager.current_model_name == "B"


def test_unavailable_model_raises_clear_error(manager, events):
    with pytest.raises(ModelUnavailableError, match="poids absents"):
        manager.analyze("Broken", IMAGE)
    assert manager.current_model_name is None
    assert "load:Broken" not in events


def test_unavailable_model_keeps_working_one_loaded(manager, events):
    manager.analyze("A", IMAGE)
    with pytest.raises(ModelUnavailableError):
        manager.analyze("Broken", IMAGE)
    assert manager.current_model_name == "A"     # A n'a pas été déchargé
    assert "unload:A" not in events


def test_failed_load_leaves_nothing_loaded(manager, events):
    with pytest.raises(RuntimeError, match="boom"):
        manager.analyze("Crash", IMAGE)
    assert manager.current_model_name is None
    assert "unload:Crash" in events              # nettoyage effectué