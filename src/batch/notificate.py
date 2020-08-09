import requests
import json
import os
import yaml

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)) , "../.." ))
secret_conf_path = os.path.join(app_home, 'config/secret_conf.yaml') 

with open(secret_conf_path, 'r') as yml:
    conf = yaml.load(yml)

def slack_connect(text):
    WEB_HOOK_URL = conf["SLACK_WEB_HOOK_URL"]
    requests.post(WEB_HOOK_URL, data=json.dumps({
        "text": text,
        "username": u'Sec-Batch',
        'link_names': 1,
    }))

def create_notification(code, update_result):
    if update_result == "SUCCESS":
        return f"update success {code}"
    elif update_result == "NO_ACCESS":
        return f"offline or url invalid {code}"
    elif update_result == "DIFF_HTML":
        return f"html invalid {code}"
    elif update_result == "UNCONNECT_SQL":
        return f"miss sql update"
