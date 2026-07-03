import pytest

import linkedin_post as lp


def test_payload_text_only_has_no_content():
    p = lp.build_post_payload("hello world", "PERSON123")
    assert p["author"] == "urn:li:person:PERSON123"
    assert p["commentary"] == "hello world"
    assert p["lifecycleState"] == "PUBLISHED"
    assert p["visibility"] == "PUBLIC"
    assert "content" not in p


def test_payload_with_image_adds_media():
    p = lp.build_post_payload("hi", "P1", image_urn="urn:li:image:C9", alt_text="a chart")
    assert p["content"] == {"media": {"id": "urn:li:image:C9", "altText": "a chart"}}


def test_payload_with_image_defaults_alt_text_to_empty():
    p = lp.build_post_payload("hi", "P1", image_urn="urn:li:image:C9")
    assert p["content"]["media"]["altText"] == ""


def test_validate_image_ok(tmp_path):
    img = tmp_path / "ok.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"0" * 100)
    lp.validate_image(str(img))  # should not raise


def test_validate_image_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        lp.validate_image(str(tmp_path / "nope.jpg"))


def test_validate_image_wrong_ext(tmp_path):
    bad = tmp_path / "x.gif"
    bad.write_bytes(b"GIF89a")
    with pytest.raises(ValueError):
        lp.validate_image(str(bad))


def test_validate_image_too_large(tmp_path):
    big = tmp_path / "big.png"
    big.write_bytes(b"0" * (5 * 1024 * 1024 + 1))
    with pytest.raises(ValueError):
        lp.validate_image(str(big))
