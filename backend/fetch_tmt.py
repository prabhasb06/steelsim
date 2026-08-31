import urllib.request
import json

try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/plant/template/tmt') as r:
        data = json.loads(r.read())
        print('Nodes:', [n['name'] for n in data['nodes']])
        for e in data['edges']:
            print(f"Edge: {e['connection_type']} from {e['source_node']} to {e['target_node']}")
except Exception as e:
    print('Error:', e)
