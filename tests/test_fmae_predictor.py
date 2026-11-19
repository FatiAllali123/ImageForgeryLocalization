from models.base_model import BaseForgeryModel
from models.fmae import config as cfg
from models.fmae.predictor import FMAEModel


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