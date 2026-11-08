# Quoteproof Community

[![test](https://github.com/andre-arc/Quoteproof-Community/actions/workflows/test.yml/badge.svg)](https://github.com/andre-arc/Quoteproof-Community/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](#install)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-d97757)](#install)
[![Pro](https://img.shields.io/badge/Pro-Agensi-2a78d6)](https://www.agensi.io/skills/quoteproof)

<img src="https://raw.githubusercontent.com/andre-arc/Quoteproof/master/assets/logo-128.png" width="64" alt="Quoteproof logo">

Free edition of Quoteproof: AI research where every quote is checked against its source web page, word for word, before it reaches your report. MIT licensed.

## Install

```bash
git clone https://github.com/andre-arc/Quoteproof-Community.git ~/.claude/skills/quoteproof-community
```

Update later with `git -C ~/.claude/skills/quoteproof-community pull`.

Made for **Claude Code** with Claude models: research runs on Haiku, the rest on your session's model. Other agents and models are not supported.

Then ask Claude to research something, e.g. *"Research whether SQLite WAL mode helps concurrent writes."* The report lands in `.claude/outputs/<topic>.md` and ends with an audit line counting every quote checked, verified and dropped.

Requires Python 3.9+ (standard library only), Claude Code, and network access to the cited sites.

## What it checks

`scripts/verify_quotes.py` fetches each cited web page once and checks that each quote appears on it, ignoring case, punctuation and spacing but never the words themselves:

| Result | Meaning | What happens |
| :-- | :-- | :-- |
| `verified` | Quote is on the cited page | kept |
| `not_found` | Quote is not on the cited page | dropped |
| `fetch_failed` | Page could not be read (PDF, blocked, offline) | kept only if the agent confirms it by hand |

You can also run the checker on its own, on any list of quotes:

```bash
python3 scripts/verify_quotes.py claims.json   # [{"claim", "source", "quote"}, ...]
```

## Community vs Pro

| | Community (free) | [Pro](https://www.agensi.io/skills/quoteproof) |
| :-- | :-- | :-- |
| 5-angle research pipeline | ✓ | ✓ |
| Word-for-word quote check, web pages | ✓ | ✓ |
| PDF sources (research papers) | — | ✓ |
| Quotes copied from the page's exact text, not a fetch-tool summary | — | ✓ |
| Detects quotes cited to the wrong page, and fixes the source | — | ✓ |

### Same research data, both editions

| Research run | Community | Pro |
| :-- | :-- | :-- |
| SQLite docs: 78 quotes, all web pages | 77 verified; **1 real quote dropped** (it was cited to the wrong page) | 77 verified; **1 corrected** to the right page |
| HTTP/3 papers: 83 quotes, 35 from PDFs | **47 checked**; 36 unreadable (35 PDFs + 1 blocked site) | **82 checked**; 1 blocked site |

Data and method: [Quoteproof proof](https://github.com/andre-arc/Quoteproof/blob/master/proof/README.md).

## Review it

Tried it on your own research? **[Share a review](https://github.com/andre-arc/Quoteproof-Community/issues/new?template=review.yml)**: your topic, the report's audit line, and whether it caught anything real or got something wrong. Honest results help most, including failures.

## Run the tests

```bash
python3 tests/test_community.py
```

## Network and privacy

The script fetches only the URLs cited in the claims, once each, and refuses private or local addresses. It writes no files and sends nothing anywhere else.

## License

MIT. See [LICENSE](LICENSE).
