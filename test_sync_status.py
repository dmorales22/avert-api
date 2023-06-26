import requests
import json

target_url = "http://127.0.0.1:5000/get_sync_status"

post_request = requests.post(target_url)

sync_status = post_request.json()

print(sync_status)