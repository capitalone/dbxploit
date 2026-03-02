from config import account_id, log, workspace_url
from core.utils import get, safe_json
import urllib.parse


def show_current_token_identity():
    url = f"{workspace_url}/api/2.0/preview/scim/v2/Me"
    #url = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{account_id}/scim/v2/Me"
    resp = get(url)
    data = safe_json(resp)
    #print(data)
    user = data.get("userName", "Unknown")
    #user = data.get("displayName", "Unknown")
    roles = [r.get("value") for r in data.get("roles", [])]
    entitlements = [e.get("value") for e in data.get("entitlements", [])]

    log("\n=== Current Token Identity ===")
    log(f"User: {user}")
    log(f"Roles: {', '.join(roles) or 'None'}")
    log(f"Entitlements: {', '.join(entitlements) or 'Not able to retrieve entitlements'}")
    log("===============================\n")


