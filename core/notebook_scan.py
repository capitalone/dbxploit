import base64
import re
from core.utils import get, safe_json
from config import workspace_url, log

def extract_credentials_from_notebooks(path="/Users"):
    log("\n[*] Scanning Notebooks for Secrets")
    url = f"{workspace_url}/api/2.0/workspace/list"
    objects = safe_json(get(url, params={"path": path})).get("objects", [])

    for obj in objects:
        if obj["object_type"] == "DIRECTORY":
            extract_credentials_from_notebooks(obj["path"])

        elif obj["object_type"] == "NOTEBOOK":
            nb_path = obj["path"]
            export_url = f"{workspace_url}/api/2.0/workspace/export"
            resp = get(export_url, params={"path": nb_path, "format": "SOURCE"})
            content = safe_json(resp).get("content")

            if content:
                decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                pattern = re.compile(r"(?i)(password|token|key|secret|access_key|client_secret|aws_secret_access_key|aws_access_key_id|slack.com|xoxp-|xoxb-)[\s:=]+['\"]([^'\"]{4,})['\"]")
                matches = list(re.finditer(pattern, decoded))

                if matches:
                    log(f"\n[!] Secrets found in {nb_path}:")
                    for match in matches:
                        keyword = match.group(1)
                        value = match.group(2)
                        context_start = max(0, match.start() - 100)
                        context_end = match.end() + 100
                        snippet = decoded[context_start:context_end].replace("\n", " ")
                        log(f"  - Keyword: {keyword}\n    Value: {value}\n    Snippet: ...{snippet}...")
