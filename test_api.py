import urllib.request
import json

try:
    req = urllib.request.Request('http://localhost:8000/health')
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read())
        print("API Response:", data)
except Exception as e:
    print(f"Cannot connect: {e}")
    print("Start API first: python agent/api.py")
