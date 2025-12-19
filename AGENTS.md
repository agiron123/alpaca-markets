# Repository Guidelines

## Project Structure & Module Organization
- Entry points live at the repo root: `main.py` (crypto streaming) and `news_stream*.py` (news streaming).
- Examples and demos live in `news_examples.py`.
- The quick smoke test is `test_news_stream.py`.
- Reference docs are `README.md`, `NEWS_API_REFERENCE.md`, and `NEWS_IMPLEMENTATION_GUIDE.md`.
- Generated artifacts include `news_feed.jsonl` and `filtered_news.jsonl` (do not commit).

## Build, Test, and Development Commands
- `uv sync` installs dependencies defined in `pyproject.toml`.
- `python main.py` starts the crypto market data stream (BTC/USD, ETH/USD).
- `python news_stream.py` runs the basic news stream.
- `python news_stream_advanced.py` runs the advanced stream and writes `news_feed.jsonl`.
- `python news_stream_filtered.py` runs filtered news and writes `filtered_news.jsonl`.
- `python test_news_stream.py` waits for a few news items to verify connectivity.

## Coding Style & Naming Conventions
- Follow standard Python style: 4-space indentation, `snake_case` for functions/vars, `PascalCase` for classes.
- Keep scripts focused and single-purpose; prefer clear handler names like `handle_news`.
- No formatter or linter is configured in `pyproject.toml`; keep changes minimal and readable.

## Testing Guidelines
- No automated test runner is set up; use `python test_news_stream.py` as a manual smoke test.
- Add new tests as standalone `test_*.py` scripts at the repo root for consistency.
- If you add a real test framework, document the command and expected coverage here.

## Commit & Pull Request Guidelines
- Current history uses short, descriptive messages (e.g., “Add comprehensive README”).
- Avoid “WIP” in final commits; use imperative, one-line summaries.
- PRs should include: a brief description, steps to verify (commands run), and sample output if behavior changes.

## Security & Configuration Tips
- Store Alpaca credentials in `.env` (not committed). Required keys: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`.
- Do not commit generated JSONL feeds or credential files.
