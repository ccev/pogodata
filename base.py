from pogodata import PogoData
import ast
import json

data = PogoData()

while True:
    query = input("Mon Query: ")
    mons = data.get_mons(**ast.literal_eval(query))
    print(json.dumps([m.get_full() for m in mons], indent=4, ensure_ascii=False))
    #print([m.get_full() for m in mons])
