# envdiff

> CLI tool to diff and reconcile .env files across environments

---

## Installation

```bash
pip install envdiff
```

Or with pipx for isolated installs:

```bash
pipx install envdiff
```

---

## Usage

Compare two `.env` files and highlight missing or mismatched keys:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
~ DB_HOST        dev=localhost        prod=db.example.com
+ SENTRY_DSN     missing in development
- DEBUG          missing in production
```

Reconcile by generating a merged template with all keys (values redacted):

```bash
envdiff .env.development .env.production --reconcile > .env.template
```

Check all environments at once:

```bash
envdiff .env.* --report
```

### Options

| Flag | Description |
|------|-------------|
| `--reconcile` | Output a merged key template |
| `--report` | Summarize diffs across multiple files |
| `--ignore-values` | Compare keys only, ignore values |
| `--quiet` | Exit with code 1 if differences found (CI use) |

---

## License

MIT © [envdiff contributors](https://github.com/yourname/envdiff)