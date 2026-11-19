import io

import numpy as np
import pytest
from PIL import Image

from services import image_processing as ip
from services.image_processing import ImageLoadError, load_image_from_bytes


def make_bytes(mode="RGB", size=(120, 80), fmt="PNG", color=None):
    """Fabrique une image en mémoire et retourne ses octets."""
    img = Image.new(mode, size, color if color is not None else 128)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_valid_png_returns_contract_format():
    arr = load_image_from_bytes(make_bytes(fmt="PNG"), "a.png")
    assert arr.dtype == np.uint8
    assert arr.shape == (80, 120, 3)          # (H, W, 3)


def test_valid_jpeg_ok():
    arr = load_image_from_bytes(make_bytes(fmt="JPEG"), "a.jpg")
    assert arr.shape == (80, 120, 3)


def test_grayscale_is_converted_to_3_channels():
    arr = load_image_from_bytes(make_bytes(mode="L", fmt="PNG"), "g.png")
    assert arr.shape == (80, 120, 3)


def test_rgba_is_converted_to_rgb():
    data = make_bytes(mode="RGBA", fmt="PNG", color=(10, 20, 30, 255))
    arr = load_image_from_bytes(data, "t.png")
    assert arr.shape == (80, 120, 3)


def test_channels_are_rgb_not_bgr():
    # Image rouge pur : en RGB, le canal 0 doit être 255
    data = make_bytes(fmt="PNG", color=(255, 0, 0))
    arr = load_image_from_bytes(data, "red.png")
    assert arr[0, 0, 0] == 255 and arr[0, 0, 2] == 0


def test_wrong_extension_rejected():
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(make_bytes(), "a.gif")


def test_fake_extension_rejected():
    # contenu GIF, mais nom .png
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(make_bytes(fmt="GIF", mode="P"), "fake.png")


def test_empty_file_rejected():
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(b"", "a.png")


def test_corrupted_bytes_rejected():
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(b"ceci n'est pas une image", "a.png")


def test_too_small_rejected():
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(make_bytes(size=(10, 10)), "tiny.png")


def test_too_many_pixels_rejected(monkeypatch):
    monkeypatch.setattr(ip, "MAX_PIXELS", 1000)   # limite très basse pour le test
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(make_bytes(size=(120, 80)), "big.png")


def test_file_too_heavy_rejected(monkeypatch):
    monkeypatch.setattr(ip, "MAX_FILE_BYTES", 10)
    with pytest.raises(ImageLoadError):
        load_image_from_bytes(make_bytes(), "heavy.png")


def test_missing_path_rejected():
    with pytest.raises(ImageLoadError):
        ip.load_image_from_path("n_existe_pas.png")