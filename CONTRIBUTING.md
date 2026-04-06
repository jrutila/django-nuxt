# Contributing to django-nuxt

Thanks for your interest in contributing to `django-nuxt`.

Repository: <https://github.com/jrutila/django-nuxt>

## Ways to contribute

- Report bugs and unexpected behavior
- Improve documentation and examples
- Add tests for edge cases and regressions
- Submit bug fixes and small enhancements

## Development prerequisites

- Python 3.10+ (3.12 recommended)
- `uv` (Python package and environment manager)
- Node.js 20+ (for Nuxt example app)
- npm, pnpm, yarn, or bun (examples below use `pnpm`)

## Local setup

1. Fork and clone the repository.
2. Create a virtual environment with `uv`.
3. Install development dependencies with `uv`.

Example commands:

```bash
uv sync
uv sync --group dev
```

You can run Python commands through `uv run ...` without manually activating the virtual environment.

## Running tests

From the repository root:

```bash
uv run runtests.py
```

Please run tests before opening a pull request.

## Running the example projects

This repository currently contains the `example/basic` project.

### Example 1: Development mode (Django + Nuxt dev server)

This is the main way to develop and verify integration behavior.

1. Install Python dependencies for the example with `uv`:

```bash
cd example/basic
uv sync
```

2. Install and run Nuxt app in one terminal:

```bash
cd example/basic/ui
pnpm install
pnpm dev
```

3. Run Django in another terminal:

```bash
cd example/basic
uv run manage.py migrate
uv run manage.py runserver
```

4. Create a superuser:

```bash
uv run manage.py createsuperuser
```

4. Open <http://127.0.0.1:8000/>.

Nuxt runs on port `3000`, and Django on port `8000`.

### Example 2: Generated static mode (without Nuxt dev server)

Use this to test production-like static output serving from Django.

1. Generate Nuxt static files:

```bash
cd example/basic/ui
npm install
npm run generate
```

2. In `example/basic/basic/settings.py`, ensure this is configured:

- `DJANGO_NUXT_GENERATED_FOLDER = 'ui/.output/public/'`
- `DJANGO_NUXT_SERVER_RUNNING = False`

3. Run Django:

```bash
cd example/basic
uv run python manage.py migrate
uv run python manage.py runserver
```

4. Open <http://127.0.0.1:8000/>.

## Pull request guidelines

- Keep PRs focused and small when possible
- Add or update tests for behavior changes
- Update docs when behavior or API changes
- Use clear commit messages describing the intent
- Include a short test plan in PR description

## Reporting issues

When reporting a bug, include:

- Operating system and Python version
- `django-nuxt` version
- Minimal reproducible example
- Expected behavior vs actual behavior
- Relevant logs or traceback

## Code of conduct

Please be respectful and constructive in all project interactions.
