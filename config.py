import logging

account_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  
workspace_url = "https://your-workspace.cloud.databricks.com"
platform_url = "https://accounts.cloud.databricks.com"
token = "dapiXXXXXXXXXXXXXXXXXXXXXXXX" 

headers = {
    "Authorization": f"Bearer {token}"
}

VERBOSE = True
LOG_FILE = "dbxploit.log"

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(msg, level="info", always_print=False):
    if level == "info":
        logging.info(msg)
    elif level == "error":
        logging.error(msg)
    if VERBOSE or always_print:
        print(msg)
