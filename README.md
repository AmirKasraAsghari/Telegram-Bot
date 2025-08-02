# Hyperliquid Trading Companion

[![coverage](https://img.shields.io/badge/coverage-%3E%3D85%25-brightgreen)](#)

This repository contains a prototype of a Telegram‑first trading companion for the Hyperliquid exchange. It is designed to follow the development plan set out in the product requirements document and provides a foundation for interacting with Hyperliquid via builder codes, natural‑language commands and growth features.

## Structure

- `bot/` – Python package containing the Telegram bot implementation. It uses **aiogram** for asynchronous Telegram interactions.
- `api/` – FastAPI application exposing REST endpoints (e.g. leaderboard).
- `config/deny_countries.json` – List of ISO country codes to block via geofencing.
- `requirements.txt` – Python dependencies.
- `tests/` – Unit tests ensuring core functions behave as expected.
- `Dockerfile.bot`, `Dockerfile.api`, `docker-compose.yml` – Containerisation configuration.

## Getting Started

1. Install Python (>=3.10) and Poetry or pip.
2. Create a `.env` file based on `.env.example` and populate `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL` and optional settings.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run tests:

   ```bash
   pytest -q --cov=hyperliquid_bot
   ```

5. Launch the bot (development mode):

   ```bash
   python -m hyperliquid_bot.bot.main
   ```

6. Launch the API server:

   ```bash
   uvicorn hyperliquid_bot.api.main:app --reload
   ```

7. For full environment orchestration, use the provided `docker-compose.yml` to start Postgres and Redis alongside the bot and API.

8. Run the latency test:

   ```bash
   pytest -q tests/test_latency.py
   ```

## Environment Variables

The bot relies on the following environment variables. A convenient way to
configure them is to create a `.env` file based on `.env.example`.

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | – |
| `OPENAI_API_KEY` | API key for OpenAI integration | – |
| `DATABASE_URL` | SQLAlchemy database URL | – |
| `REDIS_URL` | Redis/KeyDB connection URL | – |
| `BUILDER_FEE_DEFAULT` | Builder fee in tenths of a basis point | `5` |
| `LAUNCH_ZERO_FEE` | When `true`, override builder fee to zero | `false` |
| `DENY_COUNTRIES_PATH` | Path to geofence list JSON | `hyperliquid_bot/config/deny_countries.json` |

## Tests

Tests live under the `tests/` directory and can be executed with `pytest`. Coverage is measured using `pytest-cov` and should remain above 85 % to satisfy acceptance criteria. See individual test files for more details.

## Status

This is the initial implementation covering Phase 1 of the roadmap. It includes basic command handling, order JSON generation and placeholder endpoints. Future phases will add natural‑language parsing, sentiment analysis, referral tracking, HIP‑3 pair indexing, strategy generation and revenue‑sharing mechanisms.
