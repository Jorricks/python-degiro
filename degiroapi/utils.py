import json
from typing import Dict, List, Union


def pretty_json(data: Union[str, int, List, Dict]) -> str:
    return json.dumps(data, indent=4, sort_keys=True)
