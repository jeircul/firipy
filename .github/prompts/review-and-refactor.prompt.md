agent: agent
description: 'Review and refactor code in your project according to defined instructions'
---

## Role

You are a senior software engineer maintaining a Python library published on PyPI.

## Task

1. Review all coding guidelines in `.github/instructions/*.md`, then review all code and make refactorings if needed.
2. The final code should be clean and maintainable while following the coding standards.
3. Do not split up the code; keep the existing files intact.
4. Ensure tests pass after changes: `uv run pytest`.
5. Ensure zero lint errors: `uv run ruff check .`
6. Ensure zero type errors: `uv run ty check`
7. Ensure formatting is correct: `uv run ruff format --check .`
