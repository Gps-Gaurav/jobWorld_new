from bson import ObjectId
from datetime import datetime

def convert_objectid(obj):
    if isinstance(obj, list):
        return [convert_objectid(o) for o in obj]

    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                new_obj[key] = str(value)
            elif isinstance(value, datetime):
                new_obj[key] = value.isoformat()
            elif isinstance(value, dict):
                new_obj[key] = convert_objectid(value)
            elif isinstance(value, list):
                new_obj[key] = [convert_objectid(v) for v in value]
            else:
                new_obj[key] = value
        return new_obj

    return obj
