# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zhixing agent（知行 agent）是一个模板驱动的价值投资分析 AI Agent。融合用户个人投资笔记（Obsidian/flomo/NoNotes）与公开财务数据（AKShare/yfinance），辅助个人价值投资者完成从标的筛选到投资后追踪的全流程。

- **Language/Runtime**: Python 3.11+
- **LLM API**: DeepSeek via OpenAI-compatible SDK (`openai` npm package)
- **Package manager**: uv (preferred) or pip
- **Key libs**: openai, akshare, yfinance, pandas, numpy, typer, fastapi

## Commands

```bash
# Install
uv sync

# CLI
zhixing analyze --ticker 600519 --market A
zhixing screen --market A --filters "pe<15,roe>12"
zhixing track --portfolio workspace/portfolio/

# Development
uv run pytest                    # Run tests
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run mypy zhixing/             # Type check
```

## Architecture

```
zhixing/
├── cli.py                  — CLI entry (typer)
├── engine/
│   ├── agent.py            — AsyncAgent main loop
│   ├── tool_registry.py    — Tool registration and dispatch
│   ├── prompt_builder.py   — Scene → System + User prompt assembly
│   └── context_budget.py   — Context budget governance
├── scenes/                  — 6 analysis scenes (screening → tracking)
├── tools/                   — note_reader, financial_data, screener, valuation, report_writer
├── data/
│   ├── cache.py            — SQLite cache layer
│   └── schema.py           — Data models
└── render/
    └── renderer.py         — Markdown → HTML/PDF
templates/                   — 5 analysis templates (qualitative, quantitative, valuation, buy_plan, tracking)
workspace/                   — User workspace (analysis output)
```

## Key Design Principles

1. **Template-driven** — Templates are the Host, LLM operates within template constraints ("按图索骥")
2. **Traceability** — Every conclusion must be traceable to a data source or original note
3. **No PDF parsing** — MVP uses structured data from AKShare/yfinance only
4. **Scene mechanism** — Each analysis phase is a Scene with its own tool whitelist + prompt
5. **Insight injection** — User notes → structured insights → injected into analysis context

## Conventions

- **Naming**: files = snake_case, classes = PascalCase, functions = snake_case, constants = UPPER_SNAKE
- **Type hints**: All public functions must have type hints
- **Docstrings**: One-line docstrings only, no multi-paragraph blocks
- **Async**: All I/O operations use async/await
- **Error handling**: Never empty except blocks; use logging
- **Commit style**: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- **Language**: Code and comments in English; user-facing text and templates in Chinese

## Data Sources

- **A-shares**: AKShare (free, no token required)
- **US stocks**: yfinance (free, no token required)
- **Notes**: Obsidian (local files), flomo (HTML export), NoNotes (own API)
- **Reference**: CNINFO is the A-share equivalent of SEC EDGAR

## Important Notes

- AKShare API may have rate limits; cache results in SQLite
- A-shares use CAS (Chinese Accounting Standards), not US GAAP or IFRS
- Use CSRC industry classification for peer comparison, not GICS
- A-share market structure: T+1 settlement, 10% daily price limits (20% for ChiNext/STAR)
- Never store API keys in code; use environment variables or .env files
