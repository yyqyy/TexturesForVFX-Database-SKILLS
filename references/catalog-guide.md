# Catalog guide

## What is indexed

`catalog.json` is a normalized snapshot of the public [Textures for VFX database](https://simonschreibt.notion.site/Textures-for-VFX-Database-2c72eccccfa84a0eae927d778ad746cc). It contains provider links and the source database's descriptions, authors, resource types, and tags. It does not contain the linked textures, brushes, footage, VDB files, or paid products.

The snapshot retrieved on 2026-08-31 contains 264 entries. Use `python scripts/search_catalog.py --stats` for authoritative counts in the checked-in snapshot.

## Search before loading the JSON

Use the search helper so the full catalog does not need to enter model context:

```bash
# Keywords are ANDed; aliases expand common Chinese VFX terms.
python scripts/search_catalog.py fire smoke --limit 10

# Filter by one or more source resource types.
python scripts/search_catalog.py fire --type texturepack --type generator

# Filter by exact tags or creator names.
python scripts/search_catalog.py water --tag free --author "1MaFx"

# Tags marked free or CC0 in the source; still verify the provider license.
python scripts/search_catalog.py noise --free --json

# Simon's highlighted entries.
python scripts/search_catalog.py --handpick
```

`--type` and `--tag` may be repeated or comma-separated. `--json` is best when results will be processed further. If no query is supplied, filters alone are valid.

## Source types

| Type | Treat it as | Typical next action |
|---|---|---|
| `texturepack` | Images, masks, sprites, or flipbooks | Inspect channels, resolution, tiling/looping, and runtime license |
| `brushpack` | Brushes for painting tools | Confirm application/version, then render editable source at target resolution |
| `generator` | Procedural tool, graph, script, or application | Confirm tool/version and export settings; preserve the recipe |
| `vdb` | Sparse volume data | Confirm fields, voxel size, units, frame range, and renderer/engine support |
| `footage` | Photo or video source material | Confirm frame rate, color space, alpha/matte needs, and footage license |
| `tutorial`, `tut`, `course` | Instruction rather than a production asset | Apply the method; separately license any downloadable companion files |
| `forumthread` | Discussion, breakdown, or community technique | Extract the relevant method and verify linked files independently |
| `reference` | Visual or technical reference | Use for analysis; do not assume redistribution rights |
| `talk`, `slide` | High-level process or theory | Use to choose a workflow, not as a direct asset |

The source contains legacy spellings such as `tut`; preserve them when reporting catalog facts, but search `tutorial` as well.

## Useful effect keywords

| Brief | Start with these catalog terms |
|---|---|
| 火焰 / 爆炸 | `fire`, `flame`, `explosion`, `pyro`, `smoke`, `flipbook` |
| 烟雾 / 云 / 蒸汽 | `smoke`, `cloud`, `mist`, `steam`, `dust`, `vdb` |
| 水 / 水花 / 泡沫 | `water`, `liquid`, `splash`, `foam`, `drops`, `caustics` |
| 闪电 / 能量 / 魔法 | `lightning`, `magic`, `aura`, `nova`, `plasma`, `sparkles` |
| 冲击 / 弹孔 / 污渍 | `impact`, `muzzle`, `bullet`, `decal`, `crater`, `splatter` |
| 遮罩 / 扰动 / 程序噪声 | `noise`, `procedural`, `flow`, `height`, `normal`, `substance designer` |
| 手绘 / 风格化 | `paint`, `stylized`, `brush`, `photoshop`, `krita` |
| 摄影拼贴 / 实拍 | `photobash`, `photo`, `video`, `footage` |

## Ranking and interpretation

- A title or tag match is stronger than an author/domain match.
- `handpick` means the database curator highlighted the entry; it is not a license or quality guarantee for the current production.
- `free` records a source tag at snapshot time. It does not mean unrestricted, commercial, or attribution-free use.
- `cc0` is a useful lead, but verify that the exact downloadable file is actually offered under CC0 on the current provider page.
- Similar titles from different authors or URLs are separate candidates, not duplicates to remove blindly.
- A missing URL or dead provider page should cause the candidate to be rejected or replaced, not guessed.
