from core.utils import get, safe_json
from config import workspace_url, log
import csv

def dump_secrets(output_file="secrets_dump.csv"):
    log("\n[*] Dumping secrets")
    scopes_url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    scopes_resp = get(scopes_url)
    scopes = safe_json(scopes_resp).get("scopes", [])

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scope", "key", "value"])

        for scope in scopes:
            log(f"\n[+] Scope: {scope['name']}")
            keys_url = f"{workspace_url}/api/2.0/secrets/list"
            keys_resp = get(keys_url, params={"scope": scope['name']})
            keys = safe_json(keys_resp).get("secrets", [])

            for key_entry in keys:
                key = key_entry['key']
                get_url = f"{workspace_url}/api/2.0/secrets/get"
                secret_resp = get(get_url, params={"scope": scope['name'], "key": key})
                value = safe_json(secret_resp).get("value", "[ACCESS DENIED]")
                writer.writerow([scope['name'], key, value])
                log(f"   - {key}: {value}")
