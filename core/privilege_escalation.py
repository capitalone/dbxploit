from core.utils import get, post, patch, safe_json
from config import workspace_url, log, account_id, platform_url


def check_token_roles():
    url = f"{platform_url}/api/2.0/accounts/{account_id}/scim/v2/Me"
    r = get(url)
    user = safe_json(r)
    roles = [role.get("value") for role in user.get("roles", [])]
    entitlements = [ent.get("value") for ent in user.get("entitlements", [])]
    return roles, entitlements


def get_user_id_from_eid(eid):
    url = f"{platform_url}/api/2.0/accounts/{account_id}/scim/v2/Users?filter=userName eq \"{eid}\""
    r = get(url)
    users = safe_json(r).get("Resources", [])
    return users[0]["id"] if users else None

def list_service_principals():
    log("\n[*] Listing service principals (SCIM)")
    url = f"{workspace_url}/api/2.0/preview/scim/v2/ServicePrincipals"
    resp = get(url)
    data = safe_json(resp).get("Resources", [])
    for sp in data:
        log(f"  - {sp.get('displayName')} ({sp.get('id')})")

def list_groups():
    log("\n[*] Listing groups")
    url = f"{workspace_url}/api/2.0/preview/scim/v2/Groups"
    resp = get(url)
    groups = safe_json(resp).get("Resources", [])
    for group in groups:
        log(f"  - {group.get('displayName')} ({group.get('id')})")


def make_user_workspace_admin(eid):
    roles, entitlements = check_token_roles()
    if "account_admin" not in roles:
        log("[!] Insufficient privileges. Requires account_admin role.", level="error", always_print=True)
        return False
    uid = get_user_id_from_eid(eid)
    if not uid:
        log(f"[!] User EID {eid} not found", level="error")
        return False
    url = f"{platform_url}/api/2.0/accounts/{account_id}/scim/v2/Users/{uid}"
    body = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],
        "entitlements": [{"value": "workspace-access"}, {"value": "workspace-admin"}]
    }
    resp = patch(url, json=body)
    if resp.status_code == 200:
        log(f"[+] {eid} promoted to workspace admin")
        return True
    else:
        log(f"[-] Failed to promote {eid}. Status: {resp.status_code}")
        return False

def make_user_platform_admin(eid):
    roles, entitlements = check_token_roles()
    if "account_admin" not in roles:
        log("[!] Insufficient privileges. Requires account_admin role.", level="error", always_print=True)
        return False
    uid = get_user_id_from_eid(eid)
    if not uid:
        log(f"[!] User EID {eid} not found", level="error")
        return False
    url = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{account_id}/scim/v2/Users/{uid}"
    body = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],
        "roles": [{"value": "account_admin"}]
    }
    resp = patch(url, json=body)
    if resp.status_code == 200:
        log(f"[+] {eid} promoted to platform admin")
        return True
    else:
        log(f"[-] Failed to promote {eid}. Status: {resp.status_code}")
        return False

'''
def make_user_platform_admin(eid):
    user_id = get_user_id_from_eid(eid)
    if not user_id:
        log(f"User with EID '{eid}' not found.", level="error", always_print=True)
        return

    log(f"\n[*] Attempting to grant platform admin rights to: {eid} ({user_id})")
    url = f"{platform_url}/api/2.0/accounts/{account_id}/scim/v2/Users/{user_id}/roles"
    data = {"roles": ["account_admin"]}
    resp = patch(url, json=data)
    log(resp.text)

def make_user_workspace_admin(eid):
    user_id = get_user_id_from_eid(eid)
    if not user_id:
        log(f"User with EID '{eid}' not found.", level="error", always_print=True)
        return

    log(f"\n[*] Attempting to make user a workspace admin: {eid} ({user_id})")
    url = f"{platform_url}/api/2.0/accounts/{account_id}/scim/v2/Users/{user_id}"
    data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "add",
                "path": "roles",
                "value": [{"value": "workspace-admin"}]
            }
        ]
    }
    resp = patch(url, json=data)
    log(resp.text)
'''
