#!/usr/bin/env python3
"""
Extract X (Twitter) posts and articles to Markdown.

Primary method: FxTwitter API (https://api.fxtwitter.com).
Supports long-form X Articles including cover images and inline media.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import struct
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

FXTWITTER_API = "https://api.fxtwitter.com"
USER_AGENT = "x-to-markdown-skill/1.0"


def resolve_fxtwitter_url(url: str) -> str:
    """Turn an x.com or twitter.com URL into an api.fxtwitter.com URL."""
    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc.lower()
    if netloc not in ("x.com", "twitter.com", "www.x.com", "www.twitter.com", "fixupx.com", "fxtwitter.com", "vxtwitter.com"):
        raise ValueError(f"Unsupported URL host: {netloc}")

    path = parsed.path.strip("/")

    # Article URL: x.com/i/article/<id>
    m = re.match(r"i/article/(\d+)", path)
    if m:
        # FxTwitter does not expose an article-only endpoint, but the article is
        # always attached to a parent tweet. We need the status URL to fetch it.
        # Print a helpful message and exit.
        raise ValueError(
            "Article-only URLs (x.com/i/article/...) cannot be fetched directly. "
            "Please use the parent post URL (x.com/<user>/status/<id>) that links to the article."
        )

    # Status URL: <user>/status/<id>
    m = re.match(r"([^/]+)/status/(\d+)", path)
    if not m:
        raise ValueError(f"Could not parse X status URL: {url}")
    user, status_id = m.groups()
    return f"{FXTWITTER_API}/{user}/status/{status_id}"


def http_get_json(url: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def media_id_to_key(media_id: int | str) -> str:
    """Best-effort conversion of X media snowflake id to pbs.twimg.com media key.

    X media keys are base64url-encoded 11-byte blobs: the media id as 8 big-endian
    bytes plus a 3-byte suffix. The suffix is not deterministic from the id alone,
    so this helper returns the id-only prefix. The real URLs are provided by
    FxTwitter in media_entities; this function is only a fallback.
    """
    mid = int(media_id)
    blob = struct.pack(">Q", mid)
    return base64.urlsafe_b64encode(blob).rstrip(b"=").decode()


def find_media_url(media_entities: list[dict], media_id: str | None = None, local_media_id: str | None = None) -> str | None:
    """Find the original image URL for a media entity referenced from article content."""
    for ent in media_entities:
        if media_id is not None and str(ent.get("media_id")) == str(media_id):
            return ent.get("media_info", {}).get("original_img_url")
    return None


def process_inline_segment(text: str, inline_ranges: list[dict], entity_ranges: list[dict], entity_map: dict, media_entities: list[dict]) -> str:
    """Render a single Draft.js block's inline text with styles, links and emojis.

    Uses a segment-based approach so overlapping bold/italic/link/twemoji ranges
    are handled without producing broken Markdown.
    """
    # Collect style ranges
    style_md = {"BOLD": "**", "ITALIC": "_", "CODE": "`"}
    boundaries: set[int] = {0, len(text)}
    style_ranges: list[tuple[int, int, str]] = []
    for r in inline_ranges:
        style = r.get("style", "").upper()
        if style not in style_md:
            continue
        start, length = r["offset"], r["length"]
        end = start + length
        style_ranges.append((start, end, style))
        boundaries.add(start)
        boundaries.add(end)

    # Collect inline entity ranges (LINK, TWEMOJI)
    entity_ranges_clean: list[tuple[int, int, dict]] = []
    for er in entity_ranges:
        key = str(er.get("key"))
        ent = entity_map.get(key)
        if not ent:
            continue
        t = ent.get("type", "").upper()
        if t not in ("LINK", "TWEMOJI"):
            continue
        start, length = er["offset"], er["length"]
        end = start + length
        entity_ranges_clean.append((start, end, ent))
        boundaries.add(start)
        boundaries.add(end)

    if not style_ranges and not entity_ranges_clean:
        return text

    points = sorted(boundaries)
    segments: list[tuple[int, int]] = []
    for i in range(len(points) - 1):
        if points[i] < points[i + 1]:
            segments.append((points[i], points[i + 1]))

    def active_styles(start: int, end: int) -> list[str]:
        return [style for s, e, style in style_ranges if s <= start and e >= end]

    def active_entity(start: int, end: int) -> dict | None:
        for s, e, ent in entity_ranges_clean:
            if s <= start and e >= end:
                return ent
        return None

    result = []
    for start, end in segments:
        seg_text = text[start:end]
        styles = active_styles(start, end)
        ent = active_entity(start, end)
        t = ent.get("type", "").upper() if ent else None

        if t == "TWEMOJI":
            url = ent.get("data", {}).get("url", "")
            result.append(f"![]({url})")
            continue

        # Apply style markers
        prefix = "".join(style_md[s] for s in styles)
        suffix = "".join(style_md[s] for s in reversed(styles))
        rendered = f"{prefix}{seg_text}{suffix}"

        if t == "LINK" and seg_text.strip():
            url = ent.get("data", {}).get("url", "")
            rendered = f"[{rendered}]({url})"

        result.append(rendered)

    return "".join(result)


def blocks_to_markdown(
    article: dict,
    media_entities: list[dict],
    *,
    local_media_map: dict[str, str] | None = None,
    base_url: str = "",
) -> str:
    blocks = article["content"]["blocks"]
    entity_map: dict[str, dict] = {}
    for e in article["content"].get("entityMap", []):
        entity_map[str(e.get("key"))] = e.get("value", e)

    md: list[str] = []
    list_stack: list[str] = []  # "ul" or "ol"
    ol_counter = 0

    def flush_list():
        nonlocal list_stack, ol_counter
        if list_stack:
            md.append("")
            list_stack = []
            ol_counter = 0

    for block in blocks:
        btype = block.get("type", "unstyled")
        text = block.get("text", "")
        inline = block.get("inlineStyleRanges", [])
        entity_ranges = block.get("entityRanges", [])

        if btype == "atomic":
            # Atomic blocks hold a single entity (image, divider, markdown embed).
            if not entity_ranges:
                continue
            ent = entity_map.get(str(entity_ranges[0]["key"]))
            if not ent:
                continue
            t = ent.get("type", "").upper()
            data = ent.get("data", {})

            if t == "MEDIA":
                caption = data.get("caption", "").strip()
                img_url = None
                for item in data.get("mediaItems", []):
                    mid = item.get("mediaId")
                    img_url = find_media_url(media_entities, media_id=mid)
                    if img_url:
                        break
                if not img_url:
                    # Fallback placeholder so the user knows an image existed.
                    fallback_id = data.get("mediaItems", [{}])[0].get("mediaId", "unknown")
                    img_url = f"https://pbs.twimg.com/media/{media_id_to_key(fallback_id)}.jpg"
                if local_media_map and img_url in local_media_map:
                    img_url = local_media_map[img_url]
                flush_list()
                md.append("")
                md.append(f"![{caption}]({img_url})")
                if caption:
                    md.append(f"*{caption}*")
                md.append("")
            elif t == "DIVIDER":
                flush_list()
                md.append("")
                md.append("---")
                md.append("")
            elif t == "MARKDOWN":
                flush_list()
                md.append("")
                md.append(data.get("markdown", "").strip())
                md.append("")
            continue

        # Skip empty unstyled blocks unless they break a list
        if btype == "unstyled" and not text.strip():
            flush_list()
            continue

        processed = process_inline_segment(text, inline, entity_ranges, entity_map, media_entities)

        if btype == "unstyled":
            flush_list()
            md.append(processed)
        elif btype == "header-one":
            flush_list()
            md.append(f"# {processed}")
        elif btype == "header-two":
            flush_list()
            md.append(f"## {processed}")
        elif btype == "header-three":
            flush_list()
            md.append(f"### {processed}")
        elif btype == "blockquote":
            flush_list()
            md.append("> " + processed.replace("\n", "\n> "))
        elif btype == "unordered-list-item":
            if list_stack and list_stack[-1] != "ul":
                flush_list()
            if not list_stack:
                md.append("")
                list_stack.append("ul")
            md.append(f"- {processed}")
        elif btype == "ordered-list-item":
            if list_stack and list_stack[-1] != "ol":
                flush_list()
            if not list_stack:
                md.append("")
                list_stack.append("ol")
                ol_counter = 1
            md.append(f"{ol_counter}. {processed}")
            ol_counter += 1
        elif btype == "code-block":
            flush_list()
            md.append(f"```\n{processed}\n```")
        else:
            flush_list()
            md.append(processed)

    flush_list()
    return "\n".join(md).strip()


def tweet_to_markdown(tweet: dict) -> str:
    """Convert a regular (non-article) tweet to markdown."""
    author = tweet.get("author", {})
    text = tweet.get("text", "") or tweet.get("raw_text", {}).get("text", "")
    created = tweet.get("created_at", "")
    url = tweet.get("url", "")

    md = []
    md.append(f"**{author.get('name', '')}** (@{author.get('screen_name', '')})")
    md.append(f"{created}")
    md.append("")
    md.append(text)
    md.append("")

    media = tweet.get("media", {})
    photos = media.get("photos", [])
    for p in photos:
        md.append(f"![]({p.get('url', p.get('media_url_https', ''))})")
    videos = media.get("videos", [])
    for v in videos:
        md.append(f"[Video]({v.get('url', '')})")

    md.append("")
    md.append(f"— [View on X]({url})")
    return "\n".join(md)


def download_image(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def build_markdown(data: dict, *, download: bool = False, output_dir: Path | None = None) -> str:
    tweet = data.get("tweet", data)
    author = tweet.get("author", {})
    url = tweet.get("url", "")
    created = tweet.get("created_at", "")

    article = tweet.get("article")
    if article:
        title = article.get("title", "")
        preview = article.get("preview_text", "")
        media_entities = article.get("media_entities", [])
        cover = article.get("cover_media", {}).get("media_info", {}).get("original_img_url", "")

        image_dir: Path | None = None
        local_media_map: dict[str, str] | None = None
        if download and output_dir:
            image_dir = output_dir / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            local_media_map = {}

            def local_name(idx: int, src_url: str) -> str:
                ext = Path(urllib.parse.urlparse(src_url).path).suffix or ".jpg"
                return f"image_{idx:03d}{ext}"

            if cover:
                dest = image_dir / local_name(0, cover)
                download_image(cover, dest)
                cover = f"images/{dest.name}"

            for idx, ent in enumerate(media_entities, start=1):
                src = ent.get("media_info", {}).get("original_img_url", "")
                if not src:
                    continue
                dest = image_dir / local_name(idx, src)
                download_image(src, dest)
                local_media_map[src] = f"images/{dest.name}"

        body = blocks_to_markdown(article, media_entities, local_media_map=local_media_map, base_url=url)

        frontmatter = {
            "title": title,
            "author": f"{author.get('name', '')} (@{author.get('screen_name', '')})",
            "url": url,
            "published": created,
            "source": "X (Twitter)",
        }
        fm_lines = ["---"]
        for k, v in frontmatter.items():
            fm_lines.append(f"{k}: {json.dumps(v)}")
        fm_lines.append("---")

        md_parts = ["\n".join(fm_lines), ""]
        if cover:
            md_parts.append(f"![{title}]({cover})")
            md_parts.append("")
        md_parts.append(f"# {title}")
        md_parts.append("")
        md_parts.append(body)
        md_parts.append("")
        md_parts.append(f"— [Original post on X]({url})")
        return "\n".join(md_parts)

    return tweet_to_markdown(tweet)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert an X (Twitter) post or article to Markdown.")
    parser.add_argument("url", help="X/Twitter URL (status or article link)")
    parser.add_argument("-o", "--output", help="Output markdown file (default: stdout)")
    parser.add_argument("--download-media", action="store_true", help="Download images next to the output file")
    parser.add_argument("--json", action="store_true", help="Print raw FxTwitter JSON instead of Markdown")
    args = parser.parse_args()

    try:
        api_url = resolve_fxtwitter_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        data = http_get_json(api_url)
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code} from FxTwitter: {e.reason}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to fetch from FxTwitter: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    output_path: Path | None = Path(args.output) if args.output else None
    md = build_markdown(
        data,
        download=args.download_media,
        output_dir=output_path.parent if output_path else None,
    )

    if output_path:
        output_path.write_text(md, encoding="utf-8")
        print(f"Saved: {output_path}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
