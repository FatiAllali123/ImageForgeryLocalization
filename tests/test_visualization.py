import io

import numpy as np
import pytest
from PIL import Image

from models.registry import create_model, list_models
from services.visualization import (
    colorize_heatmap, mask_to_255, overlay_heatmap, overlay_mask, to_png_bytes)


def gray_image(h=8, w=8, value=100):
    return np.full((h, w, 3), value, dtype=np.uint8)


def test_colorize_shape_and_dtype():
    out = colorize_heatmap(np.random.default_rng(0).random((10, 12)).astype(np.float32))
    assert out.shape == (10, 12, 3) and out.dtype == np.uint8


def test_colorize_extremes():
    low = colorize_heatmap(np.zeros((2, 2), dtype=np.float32))[0, 0]    # RGB
    high = colorize_heatmap(np.ones((2, 2), dtype=np.float32))[0, 0]
    assert low[2] > low[0]      # 0 -> plutôt bleu
    assert high[0] > high[2]    # 1 -> plutôt rouge


def test_colorize_rejects_out_of_range():
    with pytest.raises(ValueError):
        colorize_heatmap(np.full((4, 4), 1.5, dtype=np.float32))


def test_mask_to_255_values():
    mask = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    assert set(np.unique(mask_to_255(mask))) == {0, 255}


def test_mask_to_255_rejects_already_255():
    with pytest.raises(ValueError):
        mask_to_255(np.array([[0, 255]], dtype=np.uint8))


def test_overlay_mask_only_changes_masked_pixels():
    img = gray_image()
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[2:4, 2:4] = 1
    out = overlay_mask(img, mask, alpha=0.5)
    assert np.array_equal(out[mask == 0], img[mask == 0])     # dehors : inchangé
    px = out[2, 2]
    assert px[0] > 100 and px[1] < 100 and px[2] < 100        # dedans : plus rouge


def test_overlay_mask_full_alpha_is_pure_red():
    img = gray_image()
    mask = np.ones((8, 8), dtype=np.uint8)
    out = overlay_mask(img, mask, alpha=1.0)
    assert (out == np.array([255, 0, 0], dtype=np.uint8)).all()


def test_overlay_mask_rejects_shape_mismatch():
    with pytest.raises(ValueError):
        overlay_mask(gray_image(8, 8), np.zeros((4, 4), dtype=np.uint8))


def test_overlay_heatmap_shape():
    out = overlay_heatmap(gray_image(), np.zeros((8, 8), dtype=np.float32))
    assert out.shape == (8, 8, 3) and out.dtype == np.uint8


def test_png_roundtrip():
    arr = np.random.default_rng(1).integers(0, 256, (6, 5, 3), dtype=np.uint8)
    back = np.array(Image.open(io.BytesIO(to_png_bytes(arr))))
    assert np.array_equal(arr, back)


def test_works_with_dummy_model():
    model = create_model(list_models()[0])   # le premier modèle du registre (Dummy pour l'instant)
    model.load()
    image = np.random.default_rng(0).integers(0, 256, (64, 64, 3), dtype=np.uint8)
    result = model.predict(image)
    assert colorize_heatmap(result.heatmap).shape == (64, 64, 3)
    assert overlay_mask(image, result.mask).shape == image.shape
    assert set(np.unique(mask_to_255(result.mask))) <= {0, 255}