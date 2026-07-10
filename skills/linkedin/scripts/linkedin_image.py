#!/usr/bin/env python3
"""Image generation (Pollinations, keyless) + LinkedIn Images API upload.

Stdlib only. Used by linkedin_post.py for uploads; runnable as a CLI for
generation.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"


class ImageGenError(Exception):
    pass


def build_pollinations_url(prompt, seed=None):
    enc = urllib.parse.quote(prompt, safe="")
    url = f"{POLLINATIONS_BASE}{enc}?nologo=true"
    if seed is not None:
        url += f"&seed={seed}"
    return url


def generate(prompt, out_path, seed=None, timeout=100):
    """Generate an image via Pollinations and write it to out_path.

    Returns out_path on success. Raises ImageGenError on any failure.
    Note: the free model caps output at 768x768; size params are ignored.
    """
    url = build_pollinations_url(prompt, seed)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            data = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()[:200] if hasattr(e, "read") else b""
        raise ImageGenError(f"Pollinations HTTP {e.code}: {body!r}")
    except urllib.error.URLError as e:
        raise ImageGenError(f"Pollinations request failed: {e.reason}")
    if not ctype.startswith("image/"):
        raise ImageGenError(
            f"Expected image, got Content-Type={ctype!r}; body[:200]={data[:200]!r}"
        )
    if not data:
        raise ImageGenError("Pollinations returned an empty body")
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path


LINKEDIN_API = "https://api.linkedin.com"


class ImageUploadError(Exception):
    pass


def initialize_upload(person_urn, token, version):
    """Register an image upload. Returns (upload_url, image_urn)."""
    url = f"{LINKEDIN_API}/rest/images?action=initializeUpload"
    body = json.dumps({"initializeUploadRequest": {"owner": person_urn}}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": version,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise ImageUploadError(f"initializeUpload HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise ImageUploadError(f"initializeUpload request failed: {e.reason}")
    value = payload.get("value", {})
    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")
    if not upload_url or not image_urn:
        raise ImageUploadError(
            f"initializeUpload response missing uploadUrl/image: {payload}"
        )
    return upload_url, image_urn


def put_image_bytes(upload_url, image_path, token):
    """PUT raw image bytes to the upload URL. Returns the HTTP status."""
    with open(image_path, "rb") as f:
        data = f.read()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }
    req = urllib.request.Request(upload_url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise ImageUploadError(f"image PUT HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise ImageUploadError(f"image PUT request failed: {e.reason}")
    if status not in (200, 201):
        raise ImageUploadError(f"image PUT unexpected status {status}")
    return status


def upload_image(image_path, person_urn, token, version):
    """Full upload: initialize -> PUT bytes. Returns the image URN."""
    upload_url, image_urn = initialize_upload(person_urn, token, version)
    put_image_bytes(upload_url, image_path, token)
    return image_urn


def cli_main(argv):
    parser = argparse.ArgumentParser(
        description="Generate an image via Pollinations (keyless, free)."
    )
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--out", required=True, help="Output file path (.jpg)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Optional integer seed for reproducibility")
    args = parser.parse_args(argv)
    try:
        path = generate(args.prompt, args.out, seed=args.seed)
        print(json.dumps({"status": "success", "path": path}))
        return 0
    except ImageGenError as e:
        print(json.dumps({"status": "error", "detail": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(cli_main(sys.argv[1:]))
