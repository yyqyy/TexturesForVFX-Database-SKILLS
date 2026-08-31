---
name: textures-for-vfx
description: Find, evaluate, and plan acquisition or creation of VFX textures, flipbooks, VDBs, brush packs, footage, generators, and learning resources from the curated Textures for VFX database. Use for game or film VFX asset sourcing and texture-making workflows; do not use for generic PBR material libraries or unauthorized downloading.
---

# Textures for VFX

Turn a VFX brief into a short, usable asset plan. The bundled catalog is a searchable metadata snapshot of Simon Trümpler's public Textures for VFX database; third-party assets are not bundled.

## Route the request

- To find existing resources, read [references/catalog-guide.md](references/catalog-guide.md) and search the local catalog with `scripts/search_catalog.py`.
- Before downloading, adapting, or importing a result, read [references/acquisition-and-use.md](references/acquisition-and-use.md).
- When no result fits, the license is unsuitable, or the user asks to make an original asset, read [references/creation-recipes.md](references/creation-recipes.md).
- Only when maintaining this skill's snapshot, read [references/catalog-maintenance.md](references/catalog-maintenance.md).

## Workflow

1. Convert the brief into an asset specification: effect family, visual style, target engine or DCC, deliverable type, resolution, animation/looping, channels, performance budget, and license constraints. Infer ordinary details from the project; ask only when a missing choice materially changes the result.
2. Search the local snapshot before browsing broadly. Start with effect keywords, then narrow by resource type, `free`/`cc0` hints, author, or `handpick`.
3. Prefer a small ranked set of strong candidates. Explain what each candidate supplies and whether it is a ready asset, a generator, or a learning resource.
4. Open the current provider page for every candidate that may be used. Verify availability, price, license, attribution, file format, resolution, engine/tool compatibility, and download path. Treat catalog tags as discovery hints, never as current legal or technical proof.
5. Obtain files only within the user's authorization. Do not purchase, sign in, accept a license, or bulk-download the catalog unless the user explicitly asks for that action.
6. If existing assets are unsuitable, propose or create the narrowest original pipeline that meets the specification. Preserve editable source files and record generation settings.
7. Report the chosen source URL, verified license/status, intended local import path, conversion steps, and any unresolved uncertainty.

## Search commands

Run from this skill directory:

```bash
python scripts/search_catalog.py fire free --type texturepack --limit 8
python scripts/search_catalog.py smoke --type vdb --json
python scripts/search_catalog.py "风格化" "水花" --type tutorial --limit 6
python scripts/search_catalog.py --handpick --limit 12
```

Use `--stats` to inspect available types and common tags. Search output is a candidate list, not permission to use or redistribute an asset.

## Result contract

For sourcing tasks, return a concise comparison containing:

- resource and direct provider URL;
- why it matches the brief;
- asset/resource type and expected format;
- current price/license/attribution status, or `unverified`;
- proposed project path and processing steps;
- a creation fallback when no candidate is production-safe.
