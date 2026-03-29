import requests
import json

# Test luxury hotels in Riyadh
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'Show me luxury hotels in Riyadh'})

print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
