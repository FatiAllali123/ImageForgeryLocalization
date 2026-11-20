import numpy as np
import pytest

from models.base_model import BaseForgeryModel
from models.fmae import config as cfg
from models.fmae.predictor import FMAEModel

_available, _reason = FMAEModel().is_available()


def test_fmae_respects_contract():
    model = FMAEModel()
    assert isinstance(model, BaseForgeryModel)
    assert model.name == "FMAE"
    assert model.default_threshold == cfg.DEFAULT_THRESHOLD


def test_unavailable_when_checkpoint_missing(monkeypatch, tmp_path):
    # On simule un checkpoint absent : le modèle doit le dire clairement
    monkeypatch.setattr(cfg, "CHECKPOINT_PATH", tmp_path / "absent.pth")
    ok, message = FMAEModel().is_available()
    assert ok is False
    assert "absent.pth" in message


def test_load_refuses_when_unavailable(monkeypatch, tmp_path):
    # Si un fichier manque, load() doit lever une erreur claire (pas un crash obscur)
    monkeypatch.setattr(cfg, "CHECKPOINT_PATH", tmp_path / "absent.pth")
    with pytest.raises(RuntimeError, match="indisponible"):
        FMAEModel().load()


def test_predict_rejects_invalid_image():
    gray = np.zeros((50, 50), dtype=np.uint8)   # image 2D, pas RGB
    with pytest.raises(ValueError):
        FMAEModel().predict(gray)               # refusée AVANT tout chargement


@pytest.fixture(scope="module")
def loaded_model():
    model = FMAEModel()
    model.load()            # ~16 s : une seule fois pour tous les tests ci-dessous
    return model


@pytest.mark.skipif(not _available, reason="FMAE indisponible (poids ou paquets manquants)")
def test_predict_respects_contract(loaded_model):
    rng = np.random.default_rng(0)
    image = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)

    result = loaded_model.predict(image, threshold=0.5)

    assert result.heatmap.shape == (200, 300)
    assert result.mask.shape == (200, 300)
    assert result.heatmap.dtype == np.float32
    assert 0.0 <= result.heatmap.min() and result.heatmap.max() <= 1.0
    assert set(np.unique(result.mask)) <= {0, 1}
    assert result.inference_time_s > 0
    assert result.device in ("cpu", "cuda")
    assert result.detection_score is None


@pytest.mark.skipif(not _available, reason="FMAE indisponible (poids ou paquets manquants)")
def test_higher_threshold_gives_smaller_or_equal_area(loaded_model):
    rng = np.random.default_rng(1)
    image = rng.integers(0, 256, (160, 160, 3), dtype=np.uint8)

    low = loaded_model.predict(image, threshold=0.2).suspicious_area_percent
    high = loaded_model.predict(image, threshold=0.8).suspicious_area_percent
    assert low >= high




def test_fmae_is_registered():
    from models.registry import create_model, list_models

    assert "FMAE" in list_models()
    assert isinstance(create_model("FMAE"), FMAEModel)



def test_torch_load_defaults_to_cpu_then_is_restored(monkeypatch):
    import torch
    from models.fmae.predictor import _torch_load_defaults_to_cpu

    calls = []
    monkeypatch.setattr(torch, "load", lambda *a, **k: calls.append(k))
    recorder = torch.load

    with _torch_load_defaults_to_cpu():
        torch.load("fichier.pth")                       # appel sans map_location
        torch.load("autre.pth", map_location="cuda")    # un choix explicite est respecté

    assert calls[0]["map_location"] == "cpu"
    assert calls[1]["map_location"] == "cuda"
    assert torch.load is recorder                       # fonction d'origine restaurée