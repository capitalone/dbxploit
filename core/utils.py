import requests
from config import headers, log

def get(url, params=None):
    resp = requests.get(url, headers=headers, params=params)
    #if resp.status_code != 200:
        #log(f"[!] Error {resp.status_code}: {resp.text}", level="error", always_print=True)
    return resp

def post(url, json=None):
    resp = requests.post(url, headers=headers, json=json)
    #if resp.status_code not in [200, 201]:
        #log(f"[!] Error {resp.status_code}: {resp.text}", level="error", always_print=True)
    return resp

def patch(url, json=None):
    resp = requests.patch(url, headers=headers, json=json)
    #if resp.status_code != 200:
        #log(f"[!] Error {resp.status_code}: {resp.text}", level="error", always_print=True)
    return resp

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}
