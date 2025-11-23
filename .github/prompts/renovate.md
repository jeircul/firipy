# Renovate Config Prompt

Analyze the entire repository, detect all dependency managers and signals, and produce the best Renovate configuration available today using official docs.

Steps:

1. Inventory all dependency files, custom annotations, and CI/CD pipelines.
2. Generate one `.github/renovate.json5` (supported per [official docs](https://docs.renovatebot.com/configuration-options/)) that:
   - Extends `config:recommended` plus any needed presets.
   - Enables dependency dashboard, semantic commits, and safe schedules.
   - Separates majors, groups related packages (e.g., Flux charts, terraform providers/modules, container images), and honors repo conventions.
   - Adds custom/regex managers for pinned manifest URLs or other bespoke patterns.
   - Replaces existing config entirely.
3. Validate the JSON5 (syntax + schema) before presenting it.
4. Summarize improvements in ≤3 sentences and end by asking: “Would you like to enable automerge for safe update types?”

Rules:

- Stay concise; no extra commentary beyond summary + question to save tokens.
- Follow Renovate upgrade best practices for pinning, automerge, and lockfile maintenance.
- If automerge is appropriate, request explicit user approval before enabling.
- Use only current option names from the Renovate schema.
- Ensure option combinations are schema-valid.
- Never propose opening a PR—output only the config, summary, and question.
