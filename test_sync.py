import requests
import json

target_url = "http://127.0.0.1:5000/start_sync"
artifacts_to_sync = {
    'keystroke': True,
    'mouse_action': True,
    'screenshot': True,
    'process': True,
    'window_history': True,
    'system_call': True,
    'video': True,
    'network_activity': True
}

target_info = {"target_ip": "192.168.1.246", "artifacts_to_sync": artifacts_to_sync}
post_request = requests.post(target_url, json = target_info)