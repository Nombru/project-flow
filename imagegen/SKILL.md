---
name: imagegen
description: How to actually generate an image on this machine, routing between the local SDXL pipeline and Hugging Face Spaces (FLUX.1-schnell, Qwen-Image, Kontext editing), with the licence and cost trade-off for each. Use whenever a task needs an image made rather than found: design references, section comps, mockups, marks, brand exploration, or when a skill like imagegen-frontend-web or image-to-code asks for generated imagery.
---

# Image generation on this machine

Two routes exist. Neither is a default, pick by **what the output is for**.

> This is the shim `taste-skill`'s `imagegen-frontend-web`, `imagegen-frontend-mobile`,
> `image-to-code` and `brandkit` need. Those skills say "generate the image"; this says how.

## Route A, Hugging Face Spaces (`dynamic_space`)

Use for anything that leaves the machine or feeds commercial work.

| Need | Space |
|---|---|
| General image, fast, permissively licensed | `evalstate/flux1_schnell`: **FLUX.1-schnell, Apache-2.0** |
| Higher quality, more natural | `mcp-tools/FLUX.1-Krea-dev` |
| **The image must contain readable text**: UI comps, section headings, nav labels | `mcp-tools/Qwen-Image` (or `-Fast`) |
| Change an existing image instead of regenerating it | `mcp-tools/FLUX.1-Kontext-Dev` |
| Restore, upscale, remove an object | `prithivMLmods/Photo-Mate-i2i` · `fffiloni/InstantIR` |

**Always call `view_parameters` on a space before `invoke`.** Space signatures drift; a
hardcoded parameter list is a silent failure waiting to happen.

For UI and section comps, reach for **Qwen-Image** rather than a FLUX variant. Diffusion models
other than Qwen render text as plausible-looking gibberish, which is worse than no text in a
mockup someone is meant to build from.

## Route B, local SDXL

`04-Toolkit/imagegen/gen.py`. Free, offline, no rate limit, roughly 20 s an image, weights
already cached (6.6 GB).

```bash
~/Developer/04-Toolkit/imagegen/.venv/bin/python \
  ~/Developer/04-Toolkit/imagegen/gen.py --name <run> --seeds 6 --size 1024
```

`--prompt "..."` or `--prompt-file path.txt`, `--seeds N`, `--start-seed N`, `--steps N`. Each
run writes its images plus the exact prompt and a `meta.json` of seeds and timings, so any
result reproduces.

Use it for **volume and exploration**: sweeping seeds, trying twenty directions, anything
throwaway. It is the cheap route and nothing about it touches the network.

> **Licence caveat.** The model is `stabilityai/stable-diffusion-xl-base-1.0`, under
> **CreativeML Open RAIL++-M**: not Apache-2.0. (The README still describes FLUX.1-schnell;
> that turned out to be gated and `gen.py:23` records the swap. The README is stale.) For
> exploration this is fine. For output that ships as brand or client work, use Route A's
> `flux1_schnell` instead, which is Apache-2.0 and needs no further thought.

## Choosing

- **Ships to a client, a site, or a brand system** → Route A, `evalstate/flux1_schnell`.
- **Must contain legible words** → Route A, `mcp-tools/Qwen-Image`.
- **Iterating on one image** → Route A, `FLUX.1-Kontext-Dev`. Do not regenerate from scratch and
  hope the seed lands somewhere similar.
- **Twenty variations to find a direction** → Route B, local, seeds 1–20.
- **Network is down, or the run is throwaway** → Route B.

## House rules

- **One image per section, never a contact sheet.** A single board holding eight sections is
  unreadable at the size anyone will view it, and unusable as a build reference.
- **Generate at the aspect ratio of the thing being designed.** A square comp of a wide hero
  teaches the builder the wrong composition.
- **Keep the prompt with the output.** Route B does this automatically; on Route A, save the
  prompt next to the image yourself.
- **Check `design-language/` and `04-Toolkit/design-kits` first.** If the project has a house
  aesthetic, the generated image conforms to it, it does not propose a new one.
