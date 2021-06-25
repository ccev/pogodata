from pogodata import PogoData
import json

from flask import Flask, request, jsonify

data = PogoData()
app = Flask(__name__)


@app.route('/v1/pokemon', methods=['GET', 'POST'])
def templating():
    mons = data.get_mons(**request.args)
    return (json.dumps([m.get_full(language=request.args.get("language"), iconset=request.args.get("iconset")) for m in mons], indent=4, ensure_ascii=False))


app.run(port=4442)
