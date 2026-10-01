"""Cache-backed Wiki JSON reads for quest catalog generation."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path


class CacheMissError(FileNotFoundError):
    """Raised when a cache-only generation lacks a required response."""


def load_or_fetch_json(
    cache_path: Path,
    params: Mapping[str, object],
    *,
    api_url: str,
    user_agent: str,
    cache_only: bool,
) -> Mapping[str, object]:
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    if cache_only:
        raise CacheMissError(f"required quest cache file is missing: {cache_path}")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{api_url}?{query}",
        headers={"User-Agent": user_agent},
    )
    last_error: BaseException | None = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            tmp_path = cache_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            tmp_path.replace(cache_path)
            return payload
        except urllib.error.HTTPError as exc:  # pragma: no cover - network only
            last_error = exc
            time.sleep((10 if exc.code == 429 else 1.5) * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:  # pragma: no cover - network only
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Wiki API request failed for {cache_path.stem}: {last_error}")
