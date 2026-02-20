from core.utils import get, safe_json
from config import workspace_url

def list_jobs():
    print("\n[*] Jobs")
    url = f"{workspace_url}/api/2.1/jobs/list"
    jobs = safe_json(get(url)).get("jobs", [])
    for job in jobs:
        print(f"  - Job ID: {job['job_id']} | Name: {job['settings']['name']}")

def list_clusters():
    print("\n[*] Clusters")
    url = f"{workspace_url}/api/2.0/clusters/list"
    clusters = safe_json(get(url)).get("clusters", [])
    for cluster in clusters:
        print(f"  - Cluster: {cluster['cluster_name']} | ID: {cluster['cluster_id']}")

def list_dbfs(path="/tmp"):
    print(f"\n[*] DBFS Files under {path}")
    url = f"{workspace_url}/api/2.0/dbfs/list"
    files = safe_json(get(url, params={"path": path})).get("files", [])
    for obj in files:
        print(f"  - {obj['path']}")
        if obj.get("is_dir"):
            list_dbfs(obj["path"])

def list_workspace_items(path="/Users"):
    print(f"\n[*] Workspace Items under {path}")
    url = f"{workspace_url}/api/2.0/workspace/list"
    objects = safe_json(get(url, params={"path": path})).get("objects", [])
    for obj in objects:
        print(f"  - {obj['object_type']}: {obj['path']}")
        if obj["object_type"] == "DIRECTORY":
            list_workspace_items(obj["path"])
