from pogodata import PogoData
import ast
import json

data = PogoData()

while True:
    query = input("Mon Query: ")
    query = ast.literal_eval(query)
    mons = data.get_mons(**query)
    print(json.dumps([m.get_full(language=query.get("language"), iconset=query.get("iconset")) for m in mons], indent=4, ensure_ascii=False))
    #print([m.get_full() for m in mons])
