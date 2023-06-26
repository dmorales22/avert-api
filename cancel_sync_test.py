import requests
import json

target_url = "http://127.0.0.1:5000/cancel_sync"
config = {
    'keystroke': False,
    'mouse_action': False,
    'screenshot': True,
    'process': True,
    'window_history': True,
    'system_call': True,
    'video': True,
    'network_activity': True,
    'artifact': True
}
post_request = requests.post(target_url, json = config)
sync_status = post_request.json()

print(sync_status)