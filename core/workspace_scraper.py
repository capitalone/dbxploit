import base64
from core.utils import get, safe_json
from config import workspace_url, log
import json

def scrape_workspace_items(path="/Users"):
    log(f"[*] Scraping workspace under: {path}")
    url = f"{workspace_url}/api/2.0/workspace/list"
    export_url = f"{workspace_url}/api/2.0/workspace/export"
    items = safe_json(get(url, params={"path": path})).get("objects", [])
    result = []
    for obj in items:
        if obj["object_type"] == "DIRECTORY":
            result.extend(scrape_workspace_items(path=obj["path"]))
        elif obj["object_type"] == "NOTEBOOK":
            export = safe_json(get(export_url, params={"path": obj["path"], "format": "SOURCE"}))
            content = base64.b64decode(export.get("content", "")).decode("utf-8", errors="ignore")
            result.append({"path": obj["path"], "content": content})
        else:
            result.append({"path": obj["path"], "type": obj["object_type"]})
    return result

def dump_workspace_scrape():
    log("[*] Starting workspace scrape...")
    result = scrape_workspace_items()
    with open("workspace_scrape.json", "w") as f:
        json.dump(result, f, indent=2)
    log("[+] Workspace scrape saved to workspace_scrape.json")
