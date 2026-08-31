# Acquisition and use

## Verify the provider before obtaining a file

For each shortlisted catalog entry:

1. Open the catalog URL and identify the current canonical product, article, repository, or download page.
2. Verify the exact file is still available. Record price, license name or license-page URL, attribution text, commercial-use permission, modification permission, redistribution limits, and any seat/account restrictions.
3. Verify technical facts: format, dimensions, bit depth, channel layout, frame count/rate, loop or tile behavior, supported application/engine versions, and archive size.
4. Prefer the creator's or vendor's own page. If it redirects to a marketplace or mirror, preserve both the catalog URL and final provider URL.
5. Download only the selected files. Keep the original archive or source file separate from processed runtime assets.

Never infer a license from a thumbnail, filename, `free` tag, search snippet, or tutorial description. A tutorial's viewing rights do not automatically cover its project files.

## Recommended project paths

Keep provenance next to the asset. Adapt the root to the user's project conventions:

```text
VFX/<Effect>/<AssetName>/
|-- Source/       Original download, editable graph, footage, or simulation cache
|-- Processed/    Cropped, keyed, packed, normalized, or baked intermediates
|-- Runtime/      Engine-ready textures, flipbooks, meshes, materials, or VDBs
`-- License/      License text, source URL, attribution, and acquisition date
```

Common roots:

- Unity: `Assets/VFX/<Effect>/<AssetName>/...`
- Unreal: source-control path under `Content/VFX/<Effect>/<AssetName>/...`, imported package path `/Game/VFX/<Effect>/<AssetName>/...`
- Houdini: `$JOB/vfx/<effect>/<asset>/...`
- Blender: project-relative `//assets/vfx/<effect>/<asset>/...`

Follow an existing repository convention when one exists. Do not create a second competing VFX hierarchy.

Record at least this provenance alongside production files:

```json
{
  "name": "provider asset name",
  "catalog_url": "original database URL",
  "provider_url": "current canonical URL",
  "creator": "creator or vendor",
  "license": "verified license or unverified",
  "license_url": "license evidence URL",
  "attribution": "required attribution text or none",
  "acquired_at": "YYYY-MM-DD",
  "source_files": ["Source/original-file.ext"],
  "processing": ["operations applied to the original"],
  "runtime_files": ["Runtime/final-file.ext"]
}
```

## Preparation by asset type

### Static textures and masks

- Preserve the highest-quality original. Use PNG/TGA for ordinary lossless 8-bit assets and EXR when HDR or higher precision is required.
- Treat color/emission plates as sRGB unless the source pipeline says otherwise. Import scalar masks, normals, flow maps, height, and packed data as linear/non-color data.
- Inspect alpha fringes and whether the source is straight or premultiplied. Dilate RGB beyond transparent edges before mip generation when needed.
- Confirm tiling and seam behavior. Do not label an image seamless merely because it looks repetitive.
- Pack channels only after documenting the mapping, for example `R=opacity, G=erosion, B=distortion, A=emission mask`.

### Flipbooks and animated textures

- Record grid columns/rows, frame count, frame order, source frame rate, duration, and loop behavior.
- Crop consistently around the effect, preserve padding for filtering, and verify no frame crosses cell boundaries after mip generation.
- Decide whether color, opacity, motion vectors, normals, and emission need separate sheets or packed channels.
- Test the imported sheet at runtime, including first/last-frame continuity and low-resolution mips.

### VDB and simulation caches

- Inspect named grids such as `density`, `temperature`, `flame`, `heat`, and `vel`; never assume naming or units.
- Record voxel size, world scale, bounds, frame range, compression, and whether the target renderer supports the required grids.
- For real-time use, consider baking a flipbook, vector field, mesh sequence, or sparse-volume texture rather than shipping the source cache directly.

### Brushes

- Confirm the brush format and application/version. Keep the original brush pack in `Source/`.
- Use brushes to create an editable high-resolution source document. Export purpose-built grayscale masks, color plates, or normals rather than treating the brush file itself as a runtime asset.

### Photo and video footage

- Record frame rate, shutter/motion blur, resolution, color space, bit depth, camera motion, and whether a clean plate or alpha exists.
- Key or matte against the correct background, remove spill, normalize exposure, crop/pad consistently, and loop only when the motion supports it.
- Photobash changes do not erase the footage license or attribution requirements.

### Generators and learning resources

- Record tool/plugin version, graph/script source, random seed, dependencies, and exact export settings so the result is reproducible.
- Separate a tutorial's method from downloadable assets. Recreate the method when companion-file rights are unclear.

## Acceptance checks

Before calling an asset ready, verify visual fit, correct channels/color space, alpha edges, loop/tile behavior, target-engine import, memory/texture budget, and documented provenance. Reject or regenerate an asset when license evidence or a required technical property remains unknown.
