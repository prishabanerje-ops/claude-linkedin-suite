#!/usr/bin/env python3
"""
Post text content to LinkedIn using the LinkedIn API.
Reads credentials from ~/.config/linkedin-api.env

Usage:
    python linkedin_post.py "Your post text here"
    echo "Your post text" | python linkedin_post.py
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

import linkedin_image


ENV_FILE = Path.home() / ".config" / "linkedin-api.env"

LINKEDIN_VERSION = "202506"
SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB

# LinkedIn parses `commentary` as "little text format"; these reserved chars
# must be backslash-escaped or the API silently truncates/mangles the post.
# `#` is deliberately NOT escaped so hashtags keep working.
LITTLE_TEXT_RESERVED = "\\|{}@[]()<>*_~"


def escape_little_text(text: str) -> str:
    return "".join("\\" + ch if ch in LITTLE_TEXT_RESERVED else ch for ch in text)


def load_env(path: Path) -> dict:
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env


def validate_image(path):
    """Raise if path is not an existing PNG/JPEG file under 5 MB."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    if p.suffix.lower() not in SUPPORTED_IMAGE_EXT:
        raise ValueError(
            f"Unsupported image type '{p.suffix}'; use PNG or JPEG"
        )
    size = p.stat().st_size
    if size >= MAX_IMAGE_BYTES:
        raise ValueError(f"Image too large ({size} bytes); must be < 5 MB")


def build_post_payload(text, person_id, image_urn=None, alt_text=None):
    """Build the /rest/posts request body. Adds content.media iff image_urn."""
    payload = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "visibility": "PUBLIC",
        "commentary": escape_little_text(text),
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
    }
    if image_urn:
        payload["content"] = {"media": {"id": image_urn, "altText": alt_text or ""}}
    return payload


def post_to_linkedin(text: str, token: str, person_id: str, image_urn=None, alt_text=None) -> dict:
    url = "https://api.linkedin.com/rest/posts"
    payload = build_post_payload(text, person_id, image_urn=image_urn, alt_text=alt_text)
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            location = resp.headers.get("x-restli-id") or resp.headers.get("Location", "")
            return {"status": "success", "post_id": location, "http_status": resp.status}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"status": "error", "http_status": e.code, "detail": body}


def _is_media_not_ready(result):
    """Heuristic: did the post fail because the image asset isn't queryable yet?"""
    detail = str(result.get("detail", "")).lower()
    return any(k in detail for k in ("media", "asset", "processing", "not ready"))


def post_with_retry(text, token, person_id, image_urn=None, alt_text=None,
                    attempts=3, delay=2):
    """Post, retrying only the image-URN race (image present + media-not-ready)."""
    result = None
    for i in range(attempts):
        result = post_to_linkedin(text, token, person_id, image_urn, alt_text)
        if result["status"] == "success":
            return result
        if not (image_urn and _is_media_not_ready(result)):
            return result
        if i < attempts - 1:
            time.sleep(delay)
    return result


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Post text (and optionally one image) to LinkedIn."
    )
    parser.add_argument("text", nargs="*",
                        help="Post text (optional; falls back to stdin)")
    parser.add_argument("--image", default=None,
                        help="Path to a PNG/JPEG image to attach (< 5 MB)")
    parser.add_argument("--alt-text", dest="alt_text", default=None,
                        help="Alt text for the image (accessibility/SEO)")
    return parser.parse_args(argv)


def get_post_text(args):
    if args.text:
        return " ".join(args.text)
    return sys.stdin.read().strip()


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if not ENV_FILE.exists():
        print(json.dumps({"status": "error", "detail": f"Env file not found: {ENV_FILE}"}))
        sys.exit(1)

    env = load_env(ENV_FILE)
    token = env.get("LINKEDIN_ACCESS_TOKEN", "")
    person_id = env.get("LINKEDIN_PERSON_ID", "")
    if not token or not person_id:
        print(json.dumps({"status": "error",
                          "detail": "LINKEDIN_ACCESS_TOKEN or LINKEDIN_PERSON_ID missing from env file"}))
        sys.exit(1)

    text = get_post_text(args)
    if not text:
        print(json.dumps({"status": "error", "detail": "No post text provided"}))
        sys.exit(1)

    image_urn = None
    alt_text = args.alt_text
    if args.image:
        try:
            validate_image(args.image)
        except (FileNotFoundError, ValueError) as e:
            print(json.dumps({"status": "error", "detail": str(e)}))
            sys.exit(1)
        try:
            image_urn = linkedin_image.upload_image(
                args.image, f"urn:li:person:{person_id}", token, LINKEDIN_VERSION
            )
        except linkedin_image.ImageUploadError as e:
            print(json.dumps({"status": "error", "detail": str(e)}))
            sys.exit(1)
        if not alt_text:
            alt_text = text.splitlines()[0][:300]
        print(json.dumps({"status": "info", "image_urn": image_urn,
                          "image_path": args.image}))

    result = post_with_retry(text, token, person_id, image_urn, alt_text)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
