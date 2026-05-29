#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch one RuneScape wiki asset and record provenance.

This is a developer tool only. It is intentionally outside the add-on runtime
path so Anki never performs network calls or imports optional image tooling.

Two conventions worth knowing (see memory-bank/techContext.md "Asset Scraping"):
- Skill icons: fetch the higher-res ``File:<Skill>_icon_(detail).png`` variant so
  new skills match the original four; the plain interface icon looks undersized.
- Item icons: ``--size N`` thumbnails then centers on a transparent NxN canvas, so
  tightly-cropped sprites keep transparent margins and render smaller than the
  legacy full-frame icons. ``ui.icon_filled_to_box()`` crops that padding at
  runtime, so alpha-padded item icons must flow through it to look the right size.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Mapping, Optional, Protocol, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_USER_AGENT = (
    "AnkiScape-fork asset-fetch/0.1 "
    f"({os.environ.get('ANKISCAPE_ASSET_FETCH_CONTACT', 'private personal fork')})"
)


class AssetFetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class WikiSource:
    name: str
    api_url: str
    page_base_url: str


OSRS_WIKI = WikiSource(
    name="osrs",
    api_url="https://oldschool.runescape.wiki/api.php",
    page_base_url="https://oldschool.runescape.wiki",
)
RS3_WIKI = WikiSource(
    name="rs3",
    api_url="https://runescape.wiki/api.php",
    page_base_url="https://runescape.wiki",
)
DEFAULT_WIKI_SOURCES: Tuple[WikiSource, ...] = (OSRS_WIKI, RS3_WIKI)


@dataclass(frozen=True)
class ImageInfo:
    source_wiki: str
    file_title: str
    file_page_url: str
    image_url: str
    sha1: str
    size: int
    mime: str
    timestamp: str
    mediatype: str
    license_string: str


@dataclass(frozen=True)
class AssetRequest:
    item_name: str
    wiki_title: str
    output_path: Path
    provenance_path: Path


@dataclass(frozen=True)
class FetchOutcome:
    item_name: str
    wiki_title: str
    output_path: str
    source_wiki: str
    image_url: str
    file_page_url: str
    skipped_existing: bool
    dry_run: bool


class WikiClient(Protocol):
    def query_image_info(self, source: WikiSource, file_title: str) -> Optional[ImageInfo]:
        ...

    def download_bytes(self, url: str) -> bytes:
        ...


class HttpWikiClient:
    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout_seconds: float = 30.0,
        retries: int = 3,
        min_interval_seconds: float = 1.1,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.min_interval_seconds = min_interval_seconds
        self._last_request_at = 0.0

    def query_image_info(self, source: WikiSource, file_title: str) -> Optional[ImageInfo]:
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "prop": "imageinfo",
            "iiprop": "url|sha1|size|mime|timestamp|mediatype|extmetadata",
            "titles": f"File:{file_title}",
        }
        url = f"{source.api_url}?{urllib.parse.urlencode(params)}"
        payload = self._request_json(url)
        pages = payload.get("query", {}).get("pages", [])
        if not isinstance(pages, list) or not pages:
            return None
        page = pages[0]
        if not isinstance(page, dict) or "missing" in page:
            return None
        imageinfo = page.get("imageinfo", [])
        if not isinstance(imageinfo, list) or not imageinfo:
            return None
        info = imageinfo[0]
        if not isinstance(info, dict):
            return None
        image_url = str(info.get("url") or self._special_file_path(source, file_title))
        title = str(page.get("title") or f"File:{file_title}")
        return ImageInfo(
            source_wiki=source.name,
            file_title=title.removeprefix("File:"),
            file_page_url=self._file_page_url(source, title),
            image_url=image_url,
            sha1=str(info.get("sha1") or ""),
            size=int(info.get("size") or 0),
            mime=str(info.get("mime") or ""),
            timestamp=str(info.get("timestamp") or ""),
            mediatype=str(info.get("mediatype") or ""),
            license_string=_extract_license_string(info.get("extmetadata")),
        )

    def download_bytes(self, url: str) -> bytes:
        return self._request_bytes(url)

    def _request_json(self, url: str) -> Mapping[str, object]:
        data = self._request_bytes(url)
        decoded = json.loads(data.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise AssetFetchError("MediaWiki API returned a non-object JSON payload.")
        return decoded

    def _request_bytes(self, url: str) -> bytes:
        last_error: Optional[BaseException] = None
        for attempt in range(self.retries + 1):
            self._respect_rate_limit()
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    self._last_request_at = time.monotonic()
                    return response.read()
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                time.sleep(min(8.0, 0.75 * (2 ** attempt)))
        raise AssetFetchError(f"Request failed after retries: {url}") from last_error

    def _respect_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)

    @staticmethod
    def _special_file_path(source: WikiSource, file_title: str) -> str:
        return f"{source.page_base_url}/Special:FilePath/{urllib.parse.quote(file_title.replace(' ', '_'))}"

    @staticmethod
    def _file_page_url(source: WikiSource, title: str) -> str:
        return f"{source.page_base_url}/wiki/{urllib.parse.quote(title.replace(' ', '_'), safe=':/')}"


WIKI_TITLE_OVERRIDES: Dict[str, str] = {
    "Tree": "Logs.png",
    "Oak": "Oak logs.png",
    "Willow": "Willow logs.png",
    "Teak": "Teak logs.png",
    "Maple": "Maple logs.png",
    "Mahogany": "Mahogany logs.png",
    "Yew": "Yew logs.png",
    "Magic": "Magic logs.png",
    "Redwood": "Redwood logs.png",
}


def _strip_file_prefix(title: str) -> str:
    return title[5:] if title.startswith("File:") else title


def _ensure_file_extension(title: str) -> str:
    if re.search(r"\.(png|gif|jpg|jpeg|webp)$", title, flags=re.IGNORECASE):
        return title
    return f"{title}.png"


def wiki_title_for_item(item_name: str, override: Optional[str] = None) -> str:
    if override:
        return _ensure_file_extension(_strip_file_prefix(override.strip()))
    return _ensure_file_extension(WIKI_TITLE_OVERRIDES.get(item_name, item_name).strip())


def _key_slug(value: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", value.lower()))


def _load_registry_items() -> Tuple[object, ...]:
    try:
        from constants import ITEM_DEFINITIONS
    except ImportError as exc:
        raise AssetFetchError("Could not import ITEM_DEFINITIONS from constants.py.") from exc
    return tuple(ITEM_DEFINITIONS)


def resolve_item_from_key(key: str) -> object:
    normalized = _key_slug(key)
    for item in _load_registry_items():
        candidates = {
            str(getattr(item, "id", "")),
            _key_slug(str(getattr(item, "display_name", ""))),
            _key_slug(str(getattr(item, "storage_key", ""))),
        }
        if normalized in candidates:
            return item
    raise AssetFetchError(f"No item registry entry matched --key {key!r}.")


def resolve_asset_request(
    item_name: Optional[str],
    key: Optional[str],
    out_path: Optional[Path],
    wiki_title_override: Optional[str],
    provenance_path: Path,
) -> AssetRequest:
    registry_item = resolve_item_from_key(key) if key else None
    resolved_item_name = item_name
    resolved_out = out_path
    if registry_item is not None:
        resolved_item_name = resolved_item_name or str(getattr(registry_item, "display_name"))
        asset_path = getattr(registry_item, "asset_path")
        if resolved_out is None and asset_path:
            resolved_out = Path(str(asset_path))
    if not resolved_item_name:
        raise AssetFetchError("Provide an item display name or --key.")
    if resolved_out is None:
        raise AssetFetchError("Provide --out or a --key with an asset_path in the item registry.")
    return AssetRequest(
        item_name=resolved_item_name,
        wiki_title=wiki_title_for_item(resolved_item_name, wiki_title_override),
        output_path=resolved_out.expanduser(),
        provenance_path=provenance_path.expanduser(),
    )


def resolve_image_info(
    file_title: str,
    client: WikiClient,
    sources: Sequence[WikiSource] = DEFAULT_WIKI_SOURCES,
) -> ImageInfo:
    for source in sources:
        image_info = client.query_image_info(source, file_title)
        if image_info is not None:
            return image_info
    source_names = ", ".join(source.name for source in sources)
    raise AssetFetchError(f"Could not resolve File:{file_title} from {source_names}.")


def fetch_asset(
    request: AssetRequest,
    client: WikiClient,
    size: Optional[int] = None,
    force: bool = False,
    dry_run: bool = False,
) -> FetchOutcome:
    image_info = resolve_image_info(request.wiki_title, client)
    output_path = request.output_path if request.output_path.is_absolute() else REPO_ROOT / request.output_path
    skipped_existing = output_path.exists() and not force
    if not dry_run and not skipped_existing:
        image_bytes = client.download_bytes(image_info.image_url)
        write_png(image_bytes, output_path, size)
        update_provenance(request.provenance_path, output_path, image_info)
    return FetchOutcome(
        item_name=request.item_name,
        wiki_title=request.wiki_title,
        output_path=str(output_path),
        source_wiki=image_info.source_wiki,
        image_url=image_info.image_url,
        file_page_url=image_info.file_page_url,
        skipped_existing=skipped_existing,
        dry_run=dry_run,
    )


def write_png(image_bytes: bytes, output_path: Path, size: Optional[int]) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise AssetFetchError("Pillow is required for PNG normalization. Run with `uv run`.") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(image_bytes)) as opened:
        image = opened.convert("RGBA")
        if size is not None:
            if size <= 0:
                raise AssetFetchError("--size must be a positive integer.")
            image.thumbnail((size, size))
            canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            offset = ((size - image.width) // 2, (size - image.height) // 2)
            canvas.alpha_composite(image, dest=offset)
            image = canvas
        with NamedTemporaryFile("wb", delete=False, dir=str(output_path.parent), suffix=".png") as temp_file:
            temp_name = temp_file.name
            image.save(temp_file, format="PNG")
        os.replace(temp_name, output_path)


def update_provenance(provenance_path: Path, output_path: Path, image_info: ImageInfo) -> None:
    path = provenance_path if provenance_path.is_absolute() else REPO_ROOT / provenance_path
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: Dict[str, object] = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as file_obj:
            loaded = json.load(file_obj)
        if isinstance(loaded, dict):
            existing = loaded
    key = _provenance_key(output_path)
    existing[key] = asdict(image_info)
    with NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as temp_file:
        temp_name = temp_file.name
        json.dump(existing, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, path)


def _provenance_key(output_path: Path) -> str:
    absolute = output_path if output_path.is_absolute() else REPO_ROOT / output_path
    try:
        return str(absolute.relative_to(REPO_ROOT))
    except ValueError:
        return str(absolute)


def _extract_license_string(extmetadata: object) -> str:
    if not isinstance(extmetadata, dict):
        return "unknown"
    for key in ("LicenseShortName", "License", "UsageTerms"):
        value = extmetadata.get(key)
        if isinstance(value, dict) and value.get("value"):
            return _strip_html(str(value["value"]))
    return "unknown"


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", value)
    return html.unescape(without_tags).strip() or "unknown"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a single RuneScape wiki icon for AnkiScape.")
    parser.add_argument("item", nargs="?", help="Item display name, e.g. 'Yew logs' or 'Rune essence'.")
    parser.add_argument("--out", type=Path, help="Output path for the normalized PNG.")
    parser.add_argument("--key", help="Resolve item name/path from item_registry/constants.")
    parser.add_argument("--wiki-title", help="Override the wiki File title. 'File:' prefix and .png are optional.")
    parser.add_argument(
        "--size",
        type=int,
        help=(
            "Pad/resize to an NxN transparent PNG (thumbnail then center). "
            "Tightly-cropped sprites keep margins; ui.icon_filled_to_box() crops "
            "them at runtime so they match legacy full-frame icons."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Resolve and print source/target without downloading.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    parser.add_argument("--provenance", type=Path, default=Path("assets_provenance.json"))
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        request = resolve_asset_request(args.item, args.key, args.out, args.wiki_title, args.provenance)
        outcome = fetch_asset(
            request=request,
            client=HttpWikiClient(user_agent=args.user_agent),
            size=args.size,
            force=args.force,
            dry_run=args.dry_run,
        )
    except AssetFetchError as exc:
        parser.exit(2, f"error: {exc}\n")

    print(json.dumps(asdict(outcome), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
