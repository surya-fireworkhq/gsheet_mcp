import pandas as pd
import requests
import json
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv


# Initialize MCP Server
mcp = FastMCP("GoogleSheetDownloader")
load_dotenv()
# --- Configuration ---
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyx5ChHRVhPBQxWGYLQL5CJr0M30Xyel8puf98EnHXdvWi9gaUAexjEZnB03lW7IVO7/exec"

@mcp.tool()
def query_private_sheet(sheet_id: str, query: str) -> str:
    """
    Accesses a private sheet via Apps Script proxy and runs a pandas query.
    """
    params = {
        "sheetId": sheet_id,
        "api_key": os.getenv("API_KEY")
    }

    try:
        # 1. Fetch from Apps Script
        response = requests.get(APPS_SCRIPT_URL, params=params)
        result = response.json()

        if result.get("status") != "success":
            return f"Error: {result.get('error')}"

        # 2. Convert 2D array to Pandas DataFrame
        # result['data'][0] is the header row, result['data'][1:] is the content
        raw_data = result.get("data")
        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

        # 3. Clean column names for query
        df.columns = [str(c).replace(' ', '_') for c in df.columns]

        # 4. Apply Query
        filtered_df = df.query(query)

        # 5. Return JSON Result
        return json.dumps({
            "count": len(filtered_df),
            "results": filtered_df.to_dict(orient='records')
        }, indent=2)

    except Exception as e:
        return f"Python Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()