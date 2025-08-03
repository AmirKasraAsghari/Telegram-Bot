# Hyperliquid Trading Companion

[![coverage](https://img.shields.io/badge/coverage-%3E%3D90%25-brightgreen)](#)

This repository contains a prototype of a Telegram‑first trading companion for the Hyperliquid exchange. Phase 2 extends the MVP with natural‑language order entry and a sentiment micro‑service.

## Structure

- `bot/` – Telegram bot implementation and utilities (includes natural language parser and voice stub).
- `hyperliquid_bot/api/` – FastAPI application exposing REST endpoints including `/sentiment/{pair}`.
- `hyperliquid_bot/sentiment/` – Sentiment aggregation job and models.
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

7. Run the sentiment job manually (normally scheduled hourly):

   ```bash
   python -m hyperliquid_bot.sentiment.job
   ```

   or launch the worker container:

   ```bash
   docker compose run --rm sentiment
   ```

8. For full environment orchestration, use the provided `docker-compose.yml` to start Postgres and Redis alongside the bot, API and sentiment worker.

9. Run the latency test:

   ```bash
   pytest -q tests/test_latency.py
   ```

## Environment Variables

The bot relies on the following environment variables. A convenient way to configure them is to create a `.env` file based on `.env.example`.

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | – |
| `OPENAI_API_KEY` | API key for OpenAI integration | – |
| `DATABASE_URL` | SQLAlchemy database URL | – |
| `REDIS_URL` | Redis/KeyDB connection URL | – |
| `BUILDER_FEE_DEFAULT` | Builder fee in tenths of a basis point | `5` |
| `LAUNCH_ZERO_FEE` | When `true`, override builder fee to zero | `false` |
| `DENY_COUNTRIES_PATH` | Path to geofence list JSON | `hyperliquid_bot/config/deny_countries.json` |
| `TOKEN_BUDGET_MONTHLY` | Maximum USD spend for GPT requests before fallback | `200` |

## Tests

Tests live under the `tests/` directory and can be executed with `pytest`. Coverage is measured using `pytest-cov` and should remain above 90 % to satisfy acceptance criteria. See individual test files for more details.

## Status

Phase 2 implements:

- Natural‑language order parser with confirmation flow.
- Voice message transcription stub feeding the parser.
- Budget guard to switch away from GPT when monthly spend is exceeded.
- Sentiment aggregation job storing results in Postgres and `/sentiment/{pair}` endpoint.

Future phases will add referral tracking, HIP‑3 pair indexing, strategy generation and revenue‑sharing mechanisms.
