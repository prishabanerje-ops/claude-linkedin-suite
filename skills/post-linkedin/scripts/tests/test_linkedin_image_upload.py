import io
import json
import urllib.error
import urllib.request

import linkedin_image as li


class FakeResp:
    def __init__(self, data=b"", status=200):
        self._data = data
        self.status = status
    def read(self):
        return self._data
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def test_initialize_upload_parses_url_and_urn(monkeypatch):
    payload = {"value": {"uploadUrl": "https://up.example/abc",
                         "image": "urn:li:image:C123"}}
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda req: FakeResp(json.dumps(payload).encode()))
    url, urn = li.initialize_upload("urn:li:person:P1", "tok", "202506")
    assert url == "https://up.example/abc"
    assert urn == "urn:li:image:C123"


def test_initialize_upload_raises_on_missing_fields(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda req: FakeResp(json.dumps({"value": {}}).encode()))
    try:
        li.initialize_upload("urn:li:person:P1", "tok", "202506")
        assert False, "expected ImageUploadError"
    except li.ImageUploadError as e:
        assert "uploadUrl" in str(e) or "image" in str(e)


def test_initialize_upload_raises_on_http_error(monkeypatch):
    def boom(req):
        raise urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(b"no scope"))
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    try:
        li.initialize_upload("urn:li:person:P1", "tok", "202506")
        assert False, "expected ImageUploadError"
    except li.ImageUploadError as e:
        assert "403" in str(e)


def test_put_image_bytes_ok(tmp_path, monkeypatch):
    img = tmp_path / "x.jpg"
    img.write_bytes(b"\xff\xd8\xff_data")
    monkeypatch.setattr(urllib.request, "urlopen", lambda req: FakeResp(status=201))
    status = li.put_image_bytes("https://up.example/abc", str(img), "tok")
    assert status == 201


def test_put_image_bytes_raises_on_http_error(tmp_path, monkeypatch):
    img = tmp_path / "x.jpg"
    img.write_bytes(b"data")
    def boom(req):
        raise urllib.error.HTTPError("u", 400, "Bad", {}, io.BytesIO(b"bad upload"))
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    try:
        li.put_image_bytes("https://up.example/abc", str(img), "tok")
        assert False, "expected ImageUploadError"
    except li.ImageUploadError as e:
        assert "400" in str(e)


def test_upload_image_orchestrates(tmp_path, monkeypatch):
    img = tmp_path / "x.jpg"
    img.write_bytes(b"\xff\xd8\xff_data")
    monkeypatch.setattr(li, "initialize_upload",
                        lambda person, tok, ver: ("https://up.example/abc", "urn:li:image:C9"))
    monkeypatch.setattr(li, "put_image_bytes",
                        lambda url, path, tok: 201)
    urn = li.upload_image(str(img), "urn:li:person:P1", "tok", "202506")
    assert urn == "urn:li:image:C9"
