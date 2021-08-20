from pogodata import PogoData

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


def handle_request(r):
    args = _str_to_num(dict(r.args))
    body = r.get_json()
    if body:
        args.update(body)
    return args


ENDPOINTS = {
    "pokemon": {
        "get": data.get_mons,
    },
    "types": {
        "get": data.get_types
    },
    "moves": {
        "get": data.get_moves
    },
    "weather": {
        "get": data.get_weather
    }
}


@app.route('/v1/<endpoint>', methods=['GET', 'POST'])
def main_route(endpoint):
    args = handle_request(request)
    details = ENDPOINTS.get(endpoint)
    if not details:
        return jsonify({"error": "what"})

    objs = details["get"](**args)
    objs = [o.get_full(language=args.get("language"), iconset=args.get("iconset")) for o in objs]
    return jsonify(objs)


app.run(port=4442)
