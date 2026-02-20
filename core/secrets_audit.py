from core.utils import get, safe_json
from config import workspace_url, log

'''
def audit_secret_scopes(weak_only=False):
    log("\n[*] Auditing Secret Scopes")
    scopes_url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    scopes_resp = get(scopes_url)
    scopes = safe_json(scopes_resp).get("scopes", [])

    for scope in scopes:
        name = scope['name']
        backend_type = scope.get("backend_type", "UNKNOWN")
        acl_url = f"{workspace_url}/api/2.0/secrets/acls/list?scope={name}"
        acl_resp = get(acl_url)
        items = safe_json(acl_resp).get("items", [])

        if not items:
            log(f"[!] Scope '{name}' has no ACLs defined (potentially public)")
            continue

        weak_acls = [a for a in items if a['permission'] != 'MANAGE']
        if weak_only and not weak_acls:
            continue

        log(f"\n[+] Scope: {name} (Backend: {backend_type})")
        for acl in (weak_acls if weak_only else items):
            log(f"  - {acl['principal']}: {acl['permission']}")
'''

def list_scopes():
    url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    response = get(url)
    response.raise_for_status()
    return response.json().get("scopes", [])


def get_scope_acls(scope_name):
    url = f"{workspace_url}/api/2.0/secrets/acls/list?scope={scope_name}"
    response = get(url)

    if response.status_code == 403:
        return [{"principal": "ACCESS DENIED", "permission": "N/A"}]

    #response.raise_for_status()
    return response.json().get("items", [])


def audit_secret_scopes(weak_only=False):
    scopes = list_scopes()
    print(f"Found {len(scopes)} secret scope(s).\n")

    for scope in scopes:
        name = scope["name"]
        backend_type = scope.get("backend_type", "UNKNOWN")
        print(f"Scope: {name} (Backend: {backend_type})")
        acls = get_scope_acls(name)

        if not acls:
            print("  No ACLs defined (might be accessible to all users)")

        weak_acls = [a for a in acls if a['permission'] != 'MANAGE']
        if weak_only and not weak_acls:
            continue

        log(f"\n[+] Scope: {name} (Backend: {backend_type})")
        for acl in (weak_acls if weak_only else acls):
            log(f"  - {acl['principal']}: {acl['permission']}")
            print(f"  - {acl['principal']}: {acl['permission']}")

        print("-" * 40)
