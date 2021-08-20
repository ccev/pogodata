from pogodata import PogoData
import json

from flask import Flask, request, jsonify

data = PogoData()
app = Flask(__name__)


def _str_to_num(kwargs: dict):
    for k, v in kwargs.items():
        try:
            v = float(v)
            kwargs[k] = v
        except ValueError:
            pass
        try:
            v = int(v)
            kwargs[k] = v
        except ValueError:
            pass
    return kwargs


@app.route('/v1/pokemon', methods=['GET', 'POST'])
def pokemon():
    args = _str_to_num(dict(request.args))
    body = request.get_json()
    if body:
        args.update(body)
    mons = data.get_mons(**args)
    return (json.dumps([m.get_full(language=args.get("language"), iconset=args.get("iconset")) for m in mons], indent=4, ensure_ascii=False))


@app.route('/v1/types', methods=['GET', 'POST'])
def types():
    args = _str_to_num(dict(request.args))
    types_ = data.get_types(**args)
    raws = [t.get_full(language=request.args.get("language"), iconset=request.args.get("iconset")) for t in types_]
    print(raws)
    return (json.dumps(raws))


app.run(port=4442)
