# Original asset creation recipes

Use these routes when the catalog has no suitable production-safe result or when the user wants an original asset. Start from the required runtime deliverable, not from a favorite tool.

## Choose a source method

| Need | Efficient source method | Typical deliverable |
|---|---|---|
| Reusable breakup, erosion, distortion | Procedural noise and shape composition | Seamless grayscale masks, flow/normal maps, editable graph |
| Stylized silhouettes and accents | Hand-painted strokes and shape design | Grayscale/color sprites, brush source, layered document |
| Natural detail with art direction | Licensed photo/video photobash | Cleaned plate, mask, flipbook, decal |
| Complex temporal motion | 2D/3D simulation | Flipbook, VDB, mesh sequence, vector field |
| Fast concept exploration | Generated or synthesized source plates | Curated high-resolution plate, then manually cleaned and made runtime-safe |

Generated imagery is source material, not automatically a shippable texture. Verify the generation service's rights, remove artifacts, make alpha/tiling/looping explicit, and retain prompts/settings when reproducibility matters.

## Effect-family recipes

### Fire and explosion

1. Establish a readable hot core and a slower outer flame/smoke silhouette.
2. Combine large rising shapes with medium breakup and fine erosion; avoid equal-detail noise at every scale.
3. Generate opacity, emission/color, and distortion separately. Keep HDR emission in a suitable high-range format when the engine pipeline supports it.
4. For animation, simulate or animate shape evolution, then bake a consistently cropped flipbook. Check first/last-frame continuity only if a loop is required.

### Smoke, cloud, dust, and steam

1. Start with low-frequency volume or painted massing, then add directional curl and edge breakup.
2. Preserve soft internal value variation; pure alpha cutouts often look flat.
3. Choose a VDB for offline/volume workflows, or bake density/lighting to a flipbook for real-time use.
4. Test over both light and dark backgrounds and remove color fringes at low alpha.

### Water, splash, foam, and caustics

1. Separate body shape, thin sheets, droplets, foam, and caustic light patterns because they need different motion and shading.
2. Derive normals/flow from clean height or velocity information rather than painted RGB when physically coherent refraction matters.
3. Use simulation or footage for complex splashes; use procedural patterns for tileable foam and caustics.
4. Validate temporal aliasing and mip behavior, especially for thin highlights and droplets.

### Lightning, magic, aura, and energy

1. Design the primary path or emblem first, then secondary branches, glow, sparks, and distortion.
2. Keep a sharp structural mask separate from blurred glow so the engine can control bloom and color.
3. Add flow/noise modulation without destroying the main silhouette. For loops, animate phase-continuous noise or use a deliberate cycle.

### Impact, muzzle flash, slash, decal, and splatter

1. Match the surface/view use: camera-facing sprite, mesh ribbon, projected decal, or world-space mark.
2. Separate transient flash/dust from persistent damage or stain.
3. For decals, create opacity plus material-response channels needed by the target shader; pad borders and verify projection stretching.

## Deliverable specification

Before generation or painting, state:

- asset type: static, tile, flipbook, VDB, brush, decal, mesh, or footage;
- dimensions and power-of-two requirement;
- color space, bit depth, HDR requirement, and compression target;
- channel contract and alpha convention;
- animation grid, frame count/rate, duration, and loop requirement;
- target engine/DCC and import path;
- memory/performance budget;
- provenance and license for every external source.

Preserve an editable source and a deterministic recipe when possible. Produce only the runtime variants the project actually needs.
