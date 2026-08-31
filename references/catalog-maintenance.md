# Catalog maintenance

This reference is for updating the checked-in metadata snapshot, not for ordinary asset searches.

## Update locally

The synchronizer reads the public Notion page and its default table view without credentials:

```bash
python scripts/sync_catalog.py --check
python scripts/sync_catalog.py
python scripts/search_catalog.py --stats
```

`--check` performs a live comparison without writing. A normal run replaces `references/catalog.json` deterministically, apart from the retrieval timestamp.

After a refresh:

1. Review item-count changes, new/removed types and tags, missing URLs, malformed schemes, and unexpectedly large diffs.
2. Run representative searches for texture packs, tutorials, generators, VDBs, free/CC0 hints, handpicks, and Chinese aliases.
3. Run the skill validator.
4. Update the snapshot date or counts in `references/catalog-guide.md` only when they changed.
5. Batch meaningful catalog, workflow, or schema changes into one substantial commit. Do not publish a commit for every individual link or routine probe.

The synchronizer uses Notion's public web data endpoints because this page is not exposed through the official Notion integration API. Those endpoints may change. If discovery fails, inspect the public page structure and update only the narrow parser/request layer; do not silently emit an empty or partial catalog.

Never make `sync_catalog.py` push Git changes. Remote publication remains a separate, explicitly authorized action after local review and validation.
