import io
import urllib.error
import urllib.request

import linkedin_image as li


class FakeResp:
    def __init__(self, data=b"", headers=None, status=200):
        self._data = data
        self.headers = headers or {}
        self.status = status
    def read(self):
        return self._data
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def test_build_url_encodes_and_adds_nologo():
    url = li.build_pollinations_url("a cat, in space")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "a%20cat%2C%20in%20space" in url
    assert "nologo=true" in url
    assert "seed=" not in url


def test_build_url_includes_seed_when_given():
    url = li.build_pollinations_url("x", seed=42)
    assert "seed=42" in url


def test_generate_writes_image_bytes(tmp_path, monkeypatch):
    out = tmp_path / "img.jpg"
    resp = FakeResp(data=b"\xff\xd8\xff_fakejpeg",
                    headers={"Content-Type": "image/jpeg"})
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: resp)
    result = li.generate("prompt", str(out))
    assert result == str(out)
    assert out.read_bytes() == b"\xff\xd8\xff_fakejpeg"


def test_generate_raises_on_non_image_content_type(tmp_path, monkeypatch):
    resp = FakeResp(data=b"<html>error</html>",
                    headers={"Content-Type": "text/html"})
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: resp)
    try:
        li.generate("prompt", str(tmp_path / "img.jpg"))
        assert False, "expected ImageGenError"
    except li.ImageGenError as e:
        assert "Content-Type" in str(e)


def test_generate_raises_on_http_error(tmp_path, monkeypatch):
    def boom(req, timeout=None):
        raise urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(b"quota"))
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    try:
        li.generate("prompt", str(tmp_path / "img.jpg"))
        assert False, "expected ImageGenError"
    except li.ImageGenError as e:
        assert "429" in str(e)
