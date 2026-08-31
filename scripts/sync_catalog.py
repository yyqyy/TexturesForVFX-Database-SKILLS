#!/usr/bin/env python3
"""Synchronize the public Textures for VFX Notion database into catalog.json."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SOURCE_PAGE_URL = (
    "https://simonschreibt.notion.site/"
    "Textures-for-VFX-Database-2c72eccccfa84a0eae927d778ad746cc"
)
API_ROOT = "https://www.notion.so/api/v3"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "references" / "catalog.json"
USER_AGENT = "textures-for-vfx-skill/1.0 (+public catalog metadata sync)"


class CatalogSyncError(RuntimeError):
    """Raised when the public catalog cannot be read safely."""


def post_json(endpoint: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = Request(
        f"{API_ROOT}/{endpoint}",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise CatalogSyncError(
            f"Notion {endpoint} returned HTTP {exc.code}: {detail}"
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise CatalogSyncError(f"Notion {endpoint} failed: {exc}") from exc


def page_id_from_url(url: str) -> str:
    tail = url.rstrip("/").rsplit("-", 1)[-1].split("?", 1)[0]
    try:
        return str(uuid.UUID(tail))
    except ValueError as exc:
        raise CatalogSyncError(f"Cannot find a Notion page UUID in {url!r}") from exc


def record_value(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    value = record.get("value")
    if isinstance(value, dict) and isinstance(value.get("value"), dict):
        return value["value"]
    return value if isinstance(value, dict) else None


def records(table: Any) -> Iterable[dict[str, Any]]:
    if not isinstance(table, dict):
        return []
    return (value for raw in table.values() if (value := record_value(raw)) is not None)


def discover_database(
    source_url: str, timeout: float
) -> tuple[str, str, str, dict[str, Any], dict[str, Any]]:
    page_id = page_id_from_url(source_url)
    page = post_json(
        "loadPageChunk",
        {
            "pageId": page_id,
            "limit": 1000,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False,
        },
        timeout,
    )
    record_map = page.get("recordMap", {})
    collection_block = next(
        (
            block
            for block in records(record_map.get("block"))
            if block.get("type") == "collection_view" and block.get("collection_id")
        ),
        None,
    )
    if not collection_block:
        raise CatalogSyncError("The source page contains no discoverable collection view")

    collection_id = collection_block["collection_id"]
    view_ids = collection_block.get("view_ids") or []
    available_views = {
        view["id"]: view
        for view in records(record_map.get("collection_view"))
        if view.get("id") in view_ids
    }
    view = next(
        (candidate for candidate in available_views.values() if candidate.get("type") == "table"),
        next(iter(available_views.values()), None),
    )
    if not view:
        raise CatalogSyncError("The source collection contains no readable view")

    pointer = view.get("format", {}).get("collection_pointer", {})
    space_id = pointer.get("spaceId") or collection_block.get("space_id")
    if not space_id:
        raise CatalogSyncError("The source collection has no space identifier")

    collection_entry = record_map.get("collection", {}).get(collection_id)
    collection = record_value(collection_entry)
    if not collection:
        raise CatalogSyncError("The source collection schema is missing")
    return page_id, collection_id, space_id, view, collection


def query_database(
    collection_id: str,
    space_id: str,
    view: dict[str, Any],
    timeout: float,
    limit: int,
) -> tuple[list[str], dict[str, Any]]:
    query = view.get("query2") or {}
    loader: dict[str, Any] = {
        "type": "reducer",
        "reducers": {
            "collection_group_results": {
                "type": "results",
                "limit": limit,
                "loadContentCover": True,
            }
        },
        "sort": query.get("sort", []),
        "aggregations": query.get("aggregations", []),
        "filter": {"filters": [], "operator": "and"},
        "searchQuery": "",
        "userTimeZone": "UTC",
    }
    response = post_json(
        "queryCollection",
        {
            "collection": {"id": collection_id, "spaceId": space_id},
            "collectionView": {"id": view["id"], "spaceId": space_id},
            "loader": loader,
        },
        timeout,
    )
    results = (
        response.get("result", {})
        .get("reducerResults", {})
        .get("collection_group_results", {})
    )
    block_ids = results.get("blockIds") or []
    if results.get("hasMore"):
        raise CatalogSyncError(
            f"The source contains more than the configured limit of {limit} rows"
        )
    block_table = response.get("recordMap", {}).get("block", {})
    if not block_ids or not isinstance(block_table, dict):
        raise CatalogSyncError("The collection query returned no rows")
    return block_ids, block_table


def rich_text(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    text: list[str] = []
    for segment in value:
        if isinstance(segment, list) and segment and isinstance(segment[0], str):
            text.append(segment[0])
        elif isinstance(segment, str):
            text.append(segment)
    return "".join(text).strip()


def annotated_links(value: Any) -> Iterable[str]:
    if isinstance(value, list):
        if (
            len(value) >= 2
            and value[0] == "a"
            and isinstance(value[1], str)
            and value[1].startswith(("http://", "https://"))
        ):
            yield value[1]
        for child in value:
            yield from annotated_links(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from annotated_links(child)


def resource_url(value: Any) -> str | None:
    link = next(iter(annotated_links(value)), None)
    if link:
        return link.strip()
    text = rich_text(value)
    return text if text.startswith(("http://", "https://")) else None


def split_multi(value: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for part in rich_text(value).split(","):
        normalized = part.strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def iso_millis(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def schema_keys(collection: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for schema_name in ("schema", "deleted_schema"):
        schema = collection.get(schema_name) or {}
        for key, definition in schema.items():
            if isinstance(definition, dict) and definition.get("name"):
                result.setdefault(definition["name"].casefold(), []).append(key)
    return result


def merged_multi(properties: dict[str, Any], keys: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for key in keys:
        for value in split_multi(properties.get(key)):
            folded = value.casefold()
            if folded not in seen:
                seen.add(folded)
                values.append(value)
    return values


def normalize_rows(
    block_ids: list[str], block_table: dict[str, Any], collection: dict[str, Any]
) -> list[dict[str, Any]]:
    keys = schema_keys(collection)
    title_key = (keys.get("description") or ["title"])[0]
    url_key = (keys.get("url") or [None])[0]
    type_keys = keys.get("type", [])
    tag_keys = keys.get("tags", [])
    author_keys = keys.get("author", [])
    items: list[dict[str, Any]] = []

    for block_id in block_ids:
        row = record_value(block_table.get(block_id))
        if not row or row.get("type") != "page" or not row.get("alive", True):
            continue
        properties = row.get("properties") or {}
        types = merged_multi(properties, type_keys)
        tags = merged_multi(properties, tag_keys)
        authors = merged_multi(properties, author_keys)
        folded_tags = {tag.casefold() for tag in tags}
        item = {
            "id": block_id,
            "description": rich_text(properties.get(title_key)) or None,
            "url": resource_url(properties.get(url_key)) if url_key else None,
            "authors": authors,
            "types": types,
            "tags": tags,
            "free_tagged": "free" in folded_tags,
            "cc0_tagged": "cc0" in folded_tags,
            "handpicked": "handpick" in folded_tags,
            "last_edited_at": iso_millis(row.get("last_edited_time")),
        }
        items.append(item)

    if len(items) != len(block_ids):
        raise CatalogSyncError(
            f"Normalized {len(items)} live rows from {len(block_ids)} query results"
        )
    items.sort(
        key=lambda item: (
            (item["description"] or "").casefold(),
            ",".join(item["authors"]).casefold(),
            item["url"] or "",
            item["id"],
        )
    )
    return items


def count_values(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(value for item in items for value in item[key])
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].casefold())))


def build_catalog(source_url: str, timeout: float, limit: int) -> dict[str, Any]:
    page_id, collection_id, space_id, view, collection = discover_database(
        source_url, timeout
    )
    block_ids, block_table = query_database(
        collection_id, space_id, view, timeout, limit
    )
    items = normalize_rows(block_ids, block_table, collection)
    return {
        "schema_version": 1,
        "source": {
            "page_url": source_url,
            "page_id": page_id,
            "collection_id": collection_id,
            "view_id": view["id"],
            "retrieved_at": datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
            "source_last_edited_at": iso_millis(collection.get("last_edited_time")),
        },
        "stats": {
            "items": len(items),
            "with_url": sum(bool(item["url"]) for item in items),
            "free_tagged": sum(item["free_tagged"] for item in items),
            "cc0_tagged": sum(item["cc0_tagged"] for item in items),
            "handpicked": sum(item["handpicked"] for item in items),
            "types": count_values(items, "types"),
            "tags": count_values(items, "tags"),
        },
        "items": items,
    }


def comparable(catalog: dict[str, Any]) -> dict[str, Any]:
    clone = json.loads(json.dumps(catalog))
    clone.get("source", {}).pop("retrieved_at", None)
    return clone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=SOURCE_PAGE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument(
        "--check", action="store_true", help="compare live data without writing"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        catalog = build_catalog(args.source_url, args.timeout, args.limit)
    except CatalogSyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        try:
            existing = json.loads(args.output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"out of date: cannot read {args.output}: {exc}", file=sys.stderr)
            return 1
        if comparable(existing) != comparable(catalog):
            old_count = existing.get("stats", {}).get("items", "unknown")
            print(
                f"out of date: {old_count} local items, "
                f"{catalog['stats']['items']} live items"
            )
            return 1
        print(f"up to date: {catalog['stats']['items']} items")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {catalog['stats']['items']} items "
        f"({catalog['stats']['with_url']} with URLs) to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
