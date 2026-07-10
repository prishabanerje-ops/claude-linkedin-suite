import linkedin_post as lp


def test_retry_returns_success_first_try(monkeypatch):
    calls = {"n": 0}
    def fake_post(text, token, person_id, image_urn=None, alt_text=None):
        calls["n"] += 1
        return {"status": "success", "post_id": "urn:li:share:1", "http_status": 201}
    monkeypatch.setattr(lp, "post_to_linkedin", fake_post)
    monkeypatch.setattr(lp.time, "sleep", lambda s: None)
    result = lp.post_with_retry("t", "tok", "P1", image_urn="urn:li:image:C9")
    assert result["status"] == "success"
    assert calls["n"] == 1


def test_retry_on_media_not_ready_then_succeeds(monkeypatch):
    seq = [
        {"status": "error", "http_status": 422, "detail": "media not ready: urn:li:image:C9"},
        {"status": "success", "post_id": "urn:li:share:2", "http_status": 201},
    ]
    calls = {"n": 0}
    def fake_post(text, token, person_id, image_urn=None, alt_text=None):
        r = seq[calls["n"]]
        calls["n"] += 1
        return r
    monkeypatch.setattr(lp, "post_to_linkedin", fake_post)
    monkeypatch.setattr(lp.time, "sleep", lambda s: None)
    result = lp.post_with_retry("t", "tok", "P1", image_urn="urn:li:image:C9")
    assert result["status"] == "success"
    assert calls["n"] == 2


def test_no_retry_when_no_image(monkeypatch):
    calls = {"n": 0}
    def fake_post(text, token, person_id, image_urn=None, alt_text=None):
        calls["n"] += 1
        return {"status": "error", "http_status": 400, "detail": "bad text"}
    monkeypatch.setattr(lp, "post_to_linkedin", fake_post)
    monkeypatch.setattr(lp.time, "sleep", lambda s: None)
    result = lp.post_with_retry("t", "tok", "P1")
    assert result["status"] == "error"
    assert calls["n"] == 1


def test_retry_gives_up_after_attempts(monkeypatch):
    calls = {"n": 0}
    def fake_post(text, token, person_id, image_urn=None, alt_text=None):
        calls["n"] += 1
        return {"status": "error", "http_status": 422, "detail": "image still processing"}
    monkeypatch.setattr(lp, "post_to_linkedin", fake_post)
    monkeypatch.setattr(lp.time, "sleep", lambda s: None)
    result = lp.post_with_retry("t", "tok", "P1", image_urn="urn:li:image:C9", attempts=3)
    assert result["status"] == "error"
    assert calls["n"] == 3


def test_no_retry_on_non_media_error_with_image(monkeypatch):
    calls = {"n": 0}
    def fake_post(text, token, person_id, image_urn=None, alt_text=None):
        calls["n"] += 1
        return {"status": "error", "http_status": 401, "detail": "unauthorized"}
    monkeypatch.setattr(lp, "post_to_linkedin", fake_post)
    monkeypatch.setattr(lp.time, "sleep", lambda s: None)
    result = lp.post_with_retry("t", "tok", "P1", image_urn="urn:li:image:C9")
    assert result["status"] == "error"
    assert calls["n"] == 1
