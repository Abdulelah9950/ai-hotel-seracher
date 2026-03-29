import requests
import json
import time

time.sleep(2)

response = requests.post('http://127.0.0.1:5000/api/chat', 
    json={
        'message': 'Show me luxury hotels in Riyadh',
        'user_location': {'lat': 24.083177250000002, 'lng': 38.040670999999996}
    },
    timeout=15
)

data = response.json()
hotels = data.get('hotels', [])
print('Total hotels returned:', len(hotels))
print()
for i, h in enumerate(hotels[:12]):
    rating = h.get('star_rating', 'N/A')
    name = h['name']
    print(str(i+1) + '.', name, '-', rating, 'stars')
