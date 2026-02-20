from core.utils import get, safe_json
from config import workspace_url, log
import csv

def summarize_secret_acls():
    url = f"{workspace_url}/api/2.0/secrets/scopes/list"
    scopes = safe_json(get(url)).get("scopes", [])
    summary = []
    for scope in scopes:
        name = scope.get("name")
        acl_url = f"{workspace_url}/api/2.0/secrets/acls/list?scope={name}"
        acl_resp = get(acl_url)
        items = safe_json(acl_resp).get("items", [])
        for acl in items:
            summary.append({
                "resource": name,
                "type": "secret_scope",
                "principal": acl.get("principal"),
                "permission": acl.get("permission")
            })
    return summary

def summarize_cluster_acls():
    url = f"{workspace_url}/api/2.0/clusters/list"
    clusters = safe_json(get(url)).get("clusters", [])
    summary = []
    for cluster in clusters:
        cid = cluster.get("cluster_id")
        acl_url = f"{workspace_url}/api/2.0/permissions/clusters/{cid}"
        acls = safe_json(get(acl_url)).get("access_control_list", [])
        for entry in acls:
            for perm in entry.get("all_permissions", []):
                summary.append({
                    "resource": cid,
                    "type": "cluster",
                    "principal": entry.get("user_name") or entry.get("group_name"),
                    "permission": perm.get("permission_level")
                })
    return summary

def generate_access_summary():
    log("[*] Generating access tier summary...")
    rows = summarize_secret_acls() + summarize_cluster_acls()
    with open("access_summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "resource", "principal", "permission"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    log("[+] Access summary written to access_summary.csv")
