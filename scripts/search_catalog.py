#!/usr/bin/env python3
"""Search the local Textures for VFX catalog snapshot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "references" / "catalog.json"

ALIASES: dict[str, tuple[str, ...]] = {
    "火": ("fire", "flame", "flames", "pyro"),
    "火焰": ("fire", "flame", "flames", "pyro"),
    "爆炸": ("explosion", "impact", "fire", "smoke"),
    "烟": ("smoke", "cloud", "mist", "steam"),
    "烟雾": ("smoke", "cloud", "mist", "steam"),
    "云": ("cloud", "smoke", "mist"),
    "灰尘": ("dust", "debris", "smoke"),
    "水": ("water", "liquid", "splash", "foam", "drops"),
    "水花": ("splash", "water", "liquid", "drops", "foam"),
    "泡沫": ("foam", "bubble", "water"),
    "闪电": ("lightning", "plasma", "electric"),
    "魔法": ("magic", "aura", "nova", "orb", "sparkles"),
    "能量": ("aura", "nova", "plasma", "magic", "ray"),
    "冲击": ("impact", "muzzle", "decal", "crater"),
    "血": ("blood", "splatter", "stain"),
    "噪声": ("noise", "procedural", "3d noise", "onoise"),
    "程序化": ("procedural", "generator", "substance designer"),
    "贴图": ("texture", "texturepack", "flipbook"),
    "翻页图": ("flipbook", "texturepack"),
    "序列帧": ("flipbook", "footage", "animation"),
    "体积": ("vdb", "volume", "smoke", "cloud"),
    "笔刷": ("brush", "brushpack", "paint"),
    "手绘": ("paint", "stylized", "brush"),
    "风格化": ("stylized", "paint"),
    "实拍": ("footage", "photo", "video", "photobash"),
    "教程": ("tutorial", "tut", "course", "forumthread"),
    "生成器": ("generator", "procedural"),
    "免费": ("free", "cc0"),
}


def split_values(values: Iterable[str] | None) -> list[str]:
    return [
        part.strip().casefold()
        for value in values or []
        for part in value.split(",")
        if part.strip()
    ]


def concepts(terms: list[str]) -> list[tuple[str, ...]]:
    result: list[tuple[str, ...]] = []
    for term in terms:
        normalized = term.strip().casefold()
        if not normalized:
            continue
        result.append(ALIASES.get(normalized, (normalized,)))
    return result


def field_text(values: Any) -> str:
    if isinstance(values, list):
        return " ".join(str(value) for value in values).casefold()
    return str(values or "").casefold()


def score_item(item: dict[str, Any], wanted: list[tuple[str, ...]]) -> float | None:
    fields = (
        (field_text(item.get("description")), 8.0),
        (field_text(item.get("tags")), 5.0),
        (field_text(item.get("types")), 4.0),
        (field_text(item.get("authors")), 2.0),
        (field_text(item.get("url")), 1.0),
    )
    total = 0.0
    for alternatives in wanted:
        best = 0.0
        for alternative in alternatives:
            needle = alternative.casefold()
            for haystack, weight in fields:
                if needle and needle in haystack:
                    exact_bonus = 0.5 if re.search(rf"\b{re.escape(needle)}\b", haystack) else 0
                    best = max(best, weight + exact_bonus)
        if best == 0:
            return None
        total += best
    return total


def contains_any(actual: list[str], wanted: list[str]) -> bool:
    folded = {value.casefold() for value in actual}
    return not wanted or any(value in folded for value in wanted)


def matches_filters(item: dict[str, Any], args: argparse.Namespace) -> bool:
    if not contains_any(item.get("types", []), args.types):
        return False
    folded_tags = {tag.casefold() for tag in item.get("tags", [])}
    if args.tags and not all(tag in folded_tags for tag in args.tags):
        return False
    if args.author:
        authors = field_text(item.get("authors"))
        if args.author.casefold() not in authors:
            return False
    if args.free and not (item.get("free_tagged") or item.get("cc0_tagged")):
        return False
    if args.handpick and not item.get("handpicked"):
        return False
    return True


def search(catalog: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    wanted = concepts(args.terms)
    ranked: list[tuple[float, dict[str, Any]]] = []
    for item in catalog.get("items", []):
        if not matches_filters(item, args):
            continue
        score = score_item(item, wanted)
        if score is None:
            continue
        ranked.append((score, item))
    ranked.sort(
        key=lambda pair: (
            -pair[0],
            (pair[1].get("description") or "").casefold(),
            pair[1].get("id", ""),
        )
    )
    return [dict(item, score=score) for score, item in ranked[: args.limit]]


def print_stats(catalog: dict[str, Any]) -> None:
    stats = catalog.get("stats", {})
    print(
        f"items={stats.get('items', 0)} urls={stats.get('with_url', 0)} "
        f"free_tagged={stats.get('free_tagged', 0)} "
        f"cc0_tagged={stats.get('cc0_tagged', 0)} "
        f"handpicked={stats.get('handpicked', 0)}"
    )
    print("types:")
    for name, count in stats.get("types", {}).items():
        print(f"  {name}: {count}")
    print("top tags:")
    for name, count in list(stats.get("tags", {}).items())[:40]:
        print(f"  {name}: {count}")


def print_text(results: list[dict[str, Any]]) -> None:
    if not results:
        print("No matching catalog entries.")
        return
    for index, item in enumerate(results, 1):
        description = item.get("description") or "Untitled catalog entry"
        url = item.get("url") or "(no URL in source)"
        authors = ", ".join(item.get("authors", [])) or "unknown author"
        types = ", ".join(item.get("types", [])) or "unknown type"
        tags = ", ".join(item.get("tags", [])[:10])
        print(f"{index}. {description}")
        print(f"   {url}")
        print(f"   author: {authors}; type: {types}; score: {item['score']:.1f}")
        if tags:
            print(f"   tags: {tags}")
    print("\nLicense, price, availability, and compatibility must be verified live.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="*", help="keywords; all terms must match")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--type", dest="type_values", action="append")
    parser.add_argument("--tag", dest="tag_values", action="append")
    parser.add_argument("--author")
    parser.add_argument("--free", action="store_true")
    parser.add_argument("--handpick", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    args.types = split_values(args.type_values)
    args.tags = split_values(args.tag_values)
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    return args


def main() -> int:
    args = parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {args.catalog}: {exc}", file=sys.stderr)
        return 2

    if args.stats:
        print_stats(catalog)
        if not (args.terms or args.types or args.tags or args.author or args.free or args.handpick):
            return 0

    results = search(catalog, args)
    if args.as_json:
        print(
            json.dumps(
                {
                    "count": len(results),
                    "license_notice": (
                        "Catalog tags are discovery hints; verify current license, "
                        "price, availability, and compatibility on the provider page."
                    ),
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
