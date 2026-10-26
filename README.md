# 🔎 Twitter Checker

A Discord bot that analyzes which clients (Web, iPhone, Android, TweetDeck, third-party apps…) an X/Twitter account's latest tweets were posted from, and flags unusual sources that **may** indicate the account has been compromised.

```
/check username:wallstengine
```

The bot replies with an embed containing:

- **Sources** — how many tweets came from each client (✅ common / ⚠️ unusual)
- **Suspicious** — the tweets posted from unusual sources, with links
- **Verdict** — `NORMAL`, `SUSPICIOUS` or `HIGH RISK`

## How it works

X removed the source label from its interface, but the `source` field still comes back in the responses of the internal GraphQL API used by the website. The bot uses [twscrape](https://github.com/vladkens/twscrape) to fetch tweets with a logged-in account (via cookies) and reads the `sourceLabel` field of each one.

> ⚠️ The verdict is a **heuristic**, not proof. Many legitimate accounts (news outlets, companies, creators) use TweetDeck/X Pro or scheduling tools. Treat the result as a signal to investigate, never as an accusation.

## Requirements

- Python 3.10+
- A Discord bot ([Developer Portal](https://discord.com/developers/applications))
- A **secondary** X account (it may get suspended — don't use your main account)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/twitter-checker.git
cd twitter-checker
python -m pip install -r requirements.txt
```

### 1. Discord token

Copy the example file and paste your bot token (Developer Portal → your application → **Bot** → **Reset Token**):

```bash
cp .env.example .env        # Linux/Mac
copy .env.example .env      # Windows
```

```
DISCORD_TOKEN=your_token_here
```

Invite the bot to your server via **OAuth2 → URL Generator** with the `bot` and `applications.commands` scopes and the *Send Messages* and *Embed Links* permissions.

### 2. X account

While logged in to x.com with your secondary account, open DevTools (F12) → **Application** → **Cookies** → `https://x.com` and copy the values of `auth_token` and `ct0`. Then run:

```bash
python add_account.py ACCOUNT_NAME "auth_token=VALUE; ct0=VALUE"
```

You should see `active: True`. Don't click "Log out" on that account in the browser, or the cookies will stop working. For better stability, add 2–3 accounts: twscrape rotates between them.

### 3. Run

```bash
python bot.py
```

On Windows, you can use `iniciar.bat`, which automatically restarts the bot if it crashes.

## Customization

At the top of `bot.py`:

| Variable | What it does |
|---|---|
| `FONTES_NORMAIS` | Clients considered common (✅). Any other client is flagged with ⚠️ |
| `LIMITE_TWEETS` | How many tweets to analyze (default: 20) |
| `MAX_SUSPEITOS_EXIBIDOS` | How many suspicious tweets to list in the embed |
| `TIMEOUT_BUSCA` | Maximum wait time per lookup, in seconds |

## Limitations

- **IP addresses and locations are not available.** X does not expose this data to third parties.
- **It may break without notice.** X can change its internal API or remove the `source` field at any time. If that happens, update twscrape (`pip install -U twscrape`).
- **Usage limits.** Each `/check` makes a few requests, and X limits requests and post reads per account. Heavy use may temporarily lock the account.

## Disclaimer

This project accesses X's internal API through scraping, which violates the [X Terms of Service](https://x.com/tos). It is provided for educational and research purposes only. Anyone who uses it takes full responsibility for doing so, including the possible suspension of the accounts involved. The authors are not affiliated with X Corp.

**Never commit `.env` or `accounts.db`** — they contain the bot token and the X account cookies. The included `.gitignore` already excludes them.

## License

[MIT](LICENSE)
