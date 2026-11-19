import numpy as np
import pytest

from models.base_model import PredictionResult
from models.registry import create_model, list_models


def fake_image(h=120, w=200):
    rng = np.random.default_rng(0)
    return rng.integers(0, 256, (h, w, 3), dtype=np.uint8)


def test_dummy_is_registered():
    assert any("Dummy" in name for name in list_models())


def test_dummy_returns_valid_result():
    model = create_model(list_models()[0])
    model.load()
    img = fake_image()
    res = model.predict(img)
    assert res.heatmap.shape == img.shape[:2]
    assert res.mask.shape == img.shape[:2]
    assert 0.0 <= res.suspicious_area_percent <= 100.0
    assert res.inference_time_s >= 0


def test_higher_threshold_gives_smaller_area():
    model = create_model(list_models()[0])
    img = fake_image()
    low = model.predict(img, threshold=0.2).suspicious_area_percent
    high = model.predict(img, threshold=0.8).suspicious_area_percent
    assert low > high


def test_invalid_image_is_rejected():
    model = create_model(list_models()[0])
    gray = np.zeros((50, 50), dtype=np.uint8)   # image 2D, pas RGB
    with pytest.raises(ValueError):
        model.predict(gray)


def test_result_rejects_unnormalized_heatmap():
    bad_heatmap = np.full((10, 10), 2.0, dtype=np.float32)   # hors de [0, 1]
    with pytest.raises(ValueError):
        PredictionResult(
            model_name="x",
            heatmap=bad_heatmap,
            mask=np.zeros((10, 10), dtype=np.uint8),
            inference_time_s=0.0,
            device="cpu",
        )


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        create_model("ModeleInexistant")