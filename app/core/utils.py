from datetime import datetime
import json


def datetime_to_string(dt: datetime) -> str:
    return dt.isoformat()

def string_to_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str)

def dict_to_json(data: dict) -> str:
    return json.dumps(data, default=str)

def json_to_dict(json_str: str) -> dict:
    return json.loads(json_str)
