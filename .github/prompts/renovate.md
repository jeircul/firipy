# Renovate Config Prompt

Analyze the entire repository, detect all dependency managers and signals, and produce the best Renovate configuration available today using official docs.

Steps:

1. Inventory all dependency files, custom annotations, and CI/CD pipelines.
2. Consult the latest Renovate documentation at <https://docs.renovatebot.com> to identify current schema property names and valid option combinations (no CLI validation commands—cross-check against docs only).
3. Generate one `.github/renovate.json5` that:
   - Extends `config:recommended` plus any needed presets.
   - Enables dependency dashboard, semantic commits, safe schedules, and an automerge policy for safe update types when explicitly requested.
   - Separates majors, groups related packages (e.g., Flux charts, terraform providers/modules, container images), and honors repo conventions.
   - Adds custom/regex managers for pinned manifest URLs or other bespoke patterns.
   - Includes `commitMessageExtra: '( {{currentVersion}} → {{newVersion}} )'` for major/minor/patch updates and `commitMessageExtra: '( {{currentDigestShort}} → {{newDigestShort}} )'` for digest updates.
   - Replaces existing config entirely.
4. Validate the generated JSON5 against the schema at <https://docs.renovatebot.com/renovate-schema.json> (syntax + schema compliance + option compatibility) by reasoning from the documentation.
5. Summarize improvements in ≤3 sentences and end by asking: "Would you like to enable automerge for safe update types?"

Rules:

- Stay concise; no extra commentary beyond summary + question to save tokens.
- Follow Renovate upgrade best practices for pinning, automerge, and lockfile maintenance.
- If automerge is appropriate, request explicit user approval before enabling.
- Use only current option names from the Renovate schema and prefer the latest migration guidance instead of relying on Renovate-generated migration PRs.
- Ensure option combinations are schema-valid.
- Never propose opening a PR—output only the config, summary, and question.
