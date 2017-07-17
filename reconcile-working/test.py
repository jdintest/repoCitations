import json

query='{"query" : "Ford Taurus", "limit" : 3, "type": "/automobile/model"}'


if query.startswith("{"):
    query = json.loads(query)['query']

print(query)
