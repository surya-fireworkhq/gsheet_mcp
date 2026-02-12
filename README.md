# Google Sheet MCP

An MCP (Model Context Protocol) server that lets you query **private** Google Sheets via a Google Apps Script proxy. It fetches sheet data and runs pandas-style queries on it.

## How it works

1. **MCP tool** `query_private_sheet(sheet_id, query)` is called (e.g. from Cursor).
2. The server calls your **Google Apps Script** web app with `sheet_id` and an API key.
3. Apps Script reads the sheet (with your Google credentials) and returns the data as JSON.
4. The MCP server converts the data to a pandas DataFrame, runs your **query** (pandas query syntax), and returns filtered results as JSON.

The sheet stays private; only your deployed Apps Script (with your auth) can read it.

---

## Configuration

Config is split between environment variables and code.

| What | Source | Description |
|------|--------|-------------|
| **API key** | Env var `API_KEY` | Secret your Apps Script checks. Loaded from `.env` or the process environment. |

### Using a `.env` file

In `gsheet_mcp/` create a `.env` file and add it to `.gitignore`:

```bash
# gsheet_mcp/.env (do not commit)
API_KEY=your_secret_api_key
```

Optional (if you add URL loading in code): `APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec`

`load_dotenv()` runs at startup and loads these from the current working directory, so run the server from `gsheet_mcp/` or set the variables in your shell / MCP config.

### Config reference

| Variable | Required | Used in code | Description |
|----------|----------|--------------|-------------|
| `API_KEY` | Yes | `os.getenv("API_KEY")` | API key sent to Apps Script; must match your script’s expected key. |
| `APPS_SCRIPT_URL` | Yes (in code for now) | Hardcoded in `google_sheet_mcp.py` | Deployed Apps Script web app URL. |

---

## Setup

### 1. Python environment

```bash
cd gsheet_mcp
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the MCP server

From the `gsheet_mcp` directory (so `.env` is loaded if present):

```bash
cd gsheet_mcp
source .venv/bin/activate
python google_sheet_mcp.py
```

Ensure `API_KEY` is set (in `.env` or in your environment).

---

## Using with Cursor (MCP)

Add the server to your Cursor MCP config (e.g. `~/.cursor/mcp.json` or project MCP settings). Use the full path to your `gsheet_mcp` folder:

```json
{
  "mcpServers": {
    "google-sheet": {
      "command": "/Users/<root_folder>/gsheet_mcp/.venv/bin/python3.11",
      "args": [
        "/Users/<root_folder>/gsheet_mcp/google_sheet_mcp.py"
      ],
      "env": {
        "API_KEY": "your_secret_api_key"
      }
    }
  }
}
```

If you use a `.env` file in `gsheet_mcp/`, you can omit `env` as long as Cursor runs the server with `cwd` set to that directory (so `load_dotenv()` finds `.env`).

---

## Tool: `query_private_sheet`

- **Parameters**
  - `sheet_id` (str): Google Spreadsheet ID from the sheet URL.
  - `query` (str): A pandas-style query string (e.g. `"Owner == 'surya-firework'"`, `"Browser == 'safari'"`).
- **Returns**: JSON with `count` and `results` (list of row objects). Column names in the sheet are normalized (spaces → underscores) for the query.

**Query examples (pandas syntax):**

- `"Owner == 'surya-firework'"`
- `"Browser == 'safari'"`
- `"Owner == 'surya-firework' and Browser == 'safari'"`

---

## Dependencies

- `mcp` (MCP server)
- `pandas`
- `requests`
- `python-dotenv`
- `openpyxl` (optional, for other pandas I/O)

See `gsheet_mcp/requirements.txt`.
