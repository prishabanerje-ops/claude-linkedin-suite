import io

import pytest
import linkedin_post as lp


def test_parse_args_positional_text():
    args = lp.parse_args(["hello", "world"])
    assert args.text == ["hello", "world"]
    assert args.image is None
    assert args.alt_text is None


def test_parse_args_flags():
    args = lp.parse_args(["--image", "/tmp/x.jpg", "--alt-text", "a chart"])
    assert args.image == "/tmp/x.jpg"
    assert args.alt_text == "a chart"
    assert args.text == []


def test_get_post_text_prefers_positional():
    args = lp.parse_args(["hello", "there"])
    assert lp.get_post_text(args) == "hello there"


def test_get_post_text_falls_back_to_stdin(monkeypatch):
    args = lp.parse_args([])
    monkeypatch.setattr("sys.stdin", io.StringIO("from stdin\n"))
    assert lp.get_post_text(args) == "from stdin"


def test_main_text_only_does_not_upload(monkeypatch, tmp_path):
    # Regression: no --image means no image upload and no content.media.
    env = tmp_path / "linkedin-api.env"
    env.write_text("LINKEDIN_ACCESS_TOKEN=tok\nLINKEDIN_PERSON_ID=P1\n")
    monkeypatch.setattr(lp, "ENV_FILE", env)
    captured = {}
    def fake_retry(text, token, person_id, image_urn=None, alt_text=None):
        captured.update(text=text, image_urn=image_urn)
        return {"status": "success", "post_id": "urn:li:share:1", "http_status": 201}
    monkeypatch.setattr(lp, "post_with_retry", fake_retry)
    def fail_upload(*a, **k):
        raise AssertionError("upload_image must not be called for text-only")
    monkeypatch.setattr(lp.linkedin_image, "upload_image", fail_upload)
    monkeypatch.setattr("sys.stdin", io.StringIO("just text"))
    with pytest.raises(SystemExit) as exc:
        lp.main([])
    assert exc.value.code == 0
    assert captured["text"] == "just text"
    assert captured["image_urn"] is None


def test_main_with_image_uploads_and_posts(monkeypatch, tmp_path):
    env = tmp_path / "linkedin-api.env"
    env.write_text("LINKEDIN_ACCESS_TOKEN=tok\nLINKEDIN_PERSON_ID=P1\n")
    monkeypatch.setattr(lp, "ENV_FILE", env)
    img = tmp_path / "pic.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"0" * 50)
    monkeypatch.setattr(lp.linkedin_image, "upload_image",
                        lambda path, person, tok, ver: "urn:li:image:C9")
    captured = {}
    def fake_retry(text, token, person_id, image_urn=None, alt_text=None):
        captured.update(image_urn=image_urn, alt_text=alt_text)
        return {"status": "success", "post_id": "urn:li:share:2", "http_status": 201}
    monkeypatch.setattr(lp, "post_with_retry", fake_retry)
    with pytest.raises(SystemExit) as exc:
        lp.main(["--image", str(img), "--alt-text", "my chart", "hello"])
    assert exc.value.code == 0
    assert captured["image_urn"] == "urn:li:image:C9"
    assert captured["alt_text"] == "my chart"


def test_main_bad_image_exits_before_network(monkeypatch, tmp_path):
    env = tmp_path / "linkedin-api.env"
    env.write_text("LINKEDIN_ACCESS_TOKEN=tok\nLINKEDIN_PERSON_ID=P1\n")
    monkeypatch.setattr(lp, "ENV_FILE", env)
    def fail_upload(*a, **k):
        raise AssertionError("must not upload an invalid image")
    monkeypatch.setattr(lp.linkedin_image, "upload_image", fail_upload)
    with pytest.raises(SystemExit) as exc:
        lp.main(["--image", str(tmp_path / "missing.jpg"), "hello"])
    assert exc.value.code == 1
