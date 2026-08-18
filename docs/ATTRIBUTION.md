# Attribution

This private monorepo vendors **indexes and sync scripts** for third-party skill libraries. Third-party **code is not committed**; run `scripts/sync-vendor.sh` to populate `vendor/`.

## Registered upstream sources

| Source | License notes | Sync target |
|--------|---------------|-------------|
| [anthropics/skills](https://github.com/anthropics/skills) | Mostly Apache-2.0; `docx` / `pdf` / `pptx` / `xlsx` are **source-available**, not open source — sync indexes them but never copies those four folders into commits | `vendor/anthropics-skills` |
| [obra/superpowers](https://github.com/obra/superpowers) | See upstream LICENSE | `vendor/obra-superpowers` |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Curated list | `vendor/awesome-claude-skills` |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Curated list | `vendor/composio-awesome-claude-skills` |

## Local-only mirrors (not cloned from GitHub)

| Path | Role |
|------|------|
| `~/.agents/skills` | Matt Pocock / community set (symlink forest) |
| `~/.cc-switch/skills` | Anthropic + baoyu copies via cc-switch |
| `~/.cursor/skills-cursor` | Cursor built-in skills |
| `~/.cursor/plugins/cache/cursor-public` | Plugin skill caches (cloudflare, stripe, deploy-on-aws) |

## Authored skills with third-party LICENSE files

- `skills/guizang-ppt` — keep upstream `LICENSE` and attribution as shipped with that skill.
- Skills that previously lived under Anthropic/baoyu trees (`algorithmic-art`, `brand-guidelines`, `frontend-design`, etc.) remain **upstream** via sync/index; they are **not** moved into `skills/` unless they were real authored directories.

## Document skills (Anthropic)

Claude's document skills (`docx`, `pdf`, `pptx`, `xlsx`) are source-available reference implementations. This repo may **point** at them after sync for conversion of non-Markdown inputs into Markdown before `longdoc-to-deck` segmentation. Do not republish those folders.
