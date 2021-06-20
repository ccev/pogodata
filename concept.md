base: `https://pogo.malte.xx/v3/`

## Objects

### Enum

```js
{
    "id": int,
    "tmpl": string  // tmpl or template?
}
```

### FullType

```js
{
    "id": int,
    "type": Enum,
    "name": string,
    "asset": {
        "name": string,
        "url": string
    },
    "effective_against": [
        BaseType
    ],
    "weak_against": [
        BaseType
    ],
    "resists": [
        BaseType
    ],
    "resisted_by": [
        BaseType
    ]
}
```

### BaseType

```js
{
    "id": int,
    "type": Enum
}
```

### FullMove

```js
{
    "id": int,
    "move": Enum,
    "name": string,
    "type": FullType,
    "pve": {
        "power": int,
        "energy_gain": int,
        "duration": int,
        "window": {
            "start": float,
            "end": float
        }
    },
    "pvp": {
        "power": int,
        "energy_gain": int
    }
}
```

### BaseMove

```js
{
    "id": int,
    "move": Enum,
    "type": BaseType
}
```

### FullPokemon

```js
{
    "id": int(str(formid)+str(costumeid)+str(megaid)),
    "name": string,
    "shiny": int,           // 0 = no, 1 = catchable/hatchable/..., 2 = just evolutions
    "pokemon_type": string  // base, form, temp_evolution, costume
    "pokemon": Enum,
    "form": Enum,
    "costume": Enum,
    "temp_evolution": Enum,
    "moves": [
        BaseMove,
        BaseMove
    ],
    "elite_moves": [
        BaseMove,
        BaseMove
    ],
    "types": [
        FullType,
        FullType
    ],
    "evolutions": [
        {
            "candy": int,
            "quest": TBD,
            "into": BasePokemon
        }
    ],
    "temp_evolutions": [
        {
            "energy_initial": int,
            "energy_subsequent": int,
            "into": BasePokemon
        }
    ],
    "base_stats": [
        int,
        int,
        int
    ],
    "assets": [     // list for gender variations
        {
            "name": string,
            "url": string,
            "gender": int
        }
    ],
    "info": {
        "bonus_stardust": int,
        "bonus_candy": int,
        "bonus_xl": int,
        "deployable": bool,
        "tradable": bool,
        "transferable": bool,
        "buddy_distance": int,
        "height": float,
        "weight": float,
        "gender_ratio": {
            "male": float,
            "female": float
        },
        "third_move": {
            "candy": int,
            "stardust": int
        },
        "encounter": {
            "base_capture_rate": float,
            "flee_rate": float,
            "attack": {
                "duration": float,
                "probability": float
            },
            "dodge": {
                "duration": float,
                "probability": float,
                "distance": float
            }
        }
    }
}
```

### BasePokemon

```js
{
    "id": int(str(formid)+str(costumeid)+str(megaid)),
    "shiny": int        // 0 = no, 1 = catchable/hatchable/..., 2 = just evolutions
    "pokemon_type": str,
    "pokemon": Enum,
    "form": Enum,
    "costume": Enum,
    "temp_evolution": Enum,
}
```

### FullItem

```js
{
    "id": int,
    "item": Enum,
    "name": string,
    "min_level": int,
    "category": Enum
    "type": Enum 
}
```

### Event

```js
{
    "id": int,
    "name": string,
    "type": string,
    "start": datetime,
    "end": datetime,
    "spawns": [
        BasePokemon
    ],
    "eggs": [
        BasePokemon
    ],
    "raids": [
        BasePokemon
    ],
    "shinies": [
        BasePokemon
    ],
    "features": [
        "text": string,
        "id": string,
        "value": float,
        "details": string
    ],
    "details": [
        string
    ]
}
```

### Quest

#### RewardPokemonItem (candy, xl_candy, energy)
```js
{
    "amount": int
    "pokemon": BasePokemon
}
```

#### RewardDust
```js
{
    "amount": int
}
```

```js
{
    "task": string,
    "type": string,         // event/ar/regular/sponsored
    "rewards": [
        {
            "type": "pokemon"|"item"|"xl_candy"|"candy"|"energy"|"stardust",
            "reward": BasicPokemon|FullItem|RewardPokemonItem|RewardDust
        }
    ]
}
```

### Grunt

```js
{
    "id": int,
    "character": enum, 
    "active": bool,
    "gender": int,       // 0 = male, 1 = female
    "boss": bool,
    "type": BaseType,
    "lineup": [
        {
            "reward": bool,
            "options": [
                BasePokemon
            ]
        },
        {
            ...
        },
        {
            ...
        }
    ]
}
```

## endpoints

Endpoints work via POST or GET requests. Queries can either be URL-encoded or sent as JSON in the payload.

Most endpoints return a list of according objects that match the query

Exception to both points are certain methods (e.g. cp calculation)

When "querying sub-objects", it's difference per-object what's accepted. Pokemon only accepts the id, Types would accept their ID, templateId and english name.

Queries can include languages, which only affect the "name" field. By default, it's english.

All can have an iconset and language parameter

### qlist

When an object has a list attribute, a qlist can be used in the query. It looks like this:

```
i,j         # matches a list that has i and j in it (like [i, j, k] or [i, j])
:i,j        # matches a list that only consists of i and j (just [i, j])
i|j         # matches a list that has i or j in it. (like [j, k, l] or [f, h, i])
```

### qint

When an object has an int attribute, sometimes, a qint can be used in the query. It looks like this:

```
1           # matches 1
>1          # matches all ints bigger than 1
<1          # matches all ints smaller than 1
```

### qfloat

Same as qint but with floats

### /pokemon

Limitied to 20 (?) list entries.

Query parameters

```
id: int
pokemon: int|string
lang: string                # default: english
name: string
shiny: qint
form: int|string
costume: int|string
temp_evolution: int|string
moves: qlist[int]           # Move IDs
types: qlist[int]           # Type IDs
evolutions: qlist[int]      # Pokemon IDs
temp_evolutions: qlist[int] # Pokemon IDs
assets: qlist[string]
bonus_stardust: qint
bonus_candy: qint
bonus_xl: qint
deployable: bool
tradable: bool
transferable: bool
buddy_distance: qfloat
weight: qfloat
height: qfloat
male_ratio: qfloat
female_ratio: qfloat
base_capture_rate: qfloat
flee_rate: qfloat
```

### /moves

Can return all moves

Query parameters

```
id: int
move: int|string
lang: string                # default: english
name: string
type: int|string            # ID, templateId or name
pve_power: qint
pve_energy_gain: qint
pve_duration: qint
pve_window_start: qfloat
pve_window_end: qfloat
pvp_power: qint
pvp_energy_gain: qint
```

### /items

Can return all items

Query parameters

```
id: int
item: int|string
lang: string                # default: english
name: string
min_level: qint
category: int|string
type: int|string
```

### /types

Can return all types

Query parameters

```
id: int
tmpl: string
lang: string                # default: english
name: string
effective_against: int|string   
weak_against: int|string
resists: int|string
resisted_by: int|string
```

### /events

Can return all events

Query parameters

```
id: int
types: qlist[string]
spawns: qlist[int]          # pokemon IDs
eggs: qlist[int]          # pokemon IDs
raids: qlist[int]          # pokemon IDs
shinies: qlist[int]          # pokemon IDs
```

### /raids

Returns a list of active raids and their level

```js
{
    "1": [
        BasePokemon
    ],
    "3": [
        BasePokemon
    ],
    "5": [
        BasePokemon
    ],
    "6": [
        BasePokemon
    ]
}
```

Query parameters

```
level: qint
```

### /quests

Can return all quests.

Query parameters

```
type: string
reward_types: qlist[string]
rewards: qlist[int]         # IDs
```

### /grunts

Can return all grunts

Query parameters

```
id: int
character: int|string
active: bool
gender: int
boss: bool
types: qlist[int|string]
```

## method endpoints

Only accept POST request with a body.

### /pokemon/cp

Payload:

```
id: int             # Pokemon ID
level: int
```

Returns

```js
{
    "level": int,
    "cp": int
}
```