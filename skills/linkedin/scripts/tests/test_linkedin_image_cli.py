import json

import linkedin_image as li


def test_cli_success_prints_path(tmp_path, monkeypatch, capsys):
    out = tmp_path / "img.jpg"
    monkeypatch.setattr(li, "generate",
                        lambda prompt, out_path, seed=None: out_path)
    code = li.cli_main(["--prompt", "a robot", "--out", str(out)])
    assert code == 0
    printed = json.loads(capsys.readouterr().out.strip())
    assert printed["status"] == "success"
    assert printed["path"] == str(out)


def test_cli_error_returns_1(tmp_path, monkeypatch, capsys):
    def boom(prompt, out_path, seed=None):
        raise li.ImageGenError("boom 429")
    monkeypatch.setattr(li, "generate", boom)
    code = li.cli_main(["--prompt", "x", "--out", str(tmp_path / "i.jpg")])
    assert code == 1
    printed = json.loads(capsys.readouterr().out.strip())
    assert printed["status"] == "error"
    assert "boom 429" in printed["detail"]


def test_cli_passes_seed(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(li, "generate",
                        lambda prompt, out_path, seed=None: seen.setdefault("seed", seed) or out_path)
    li.cli_main(["--prompt", "x", "--out", str(tmp_path / "i.jpg"), "--seed", "7"])
    assert seen["seed"] == 7
