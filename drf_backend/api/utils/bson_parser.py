from bson import ObjectId

def convert_objectid(data):
    """
    Recursively converts MongoDB ObjectId to string for JSON serialization.
    Supports dicts, lists, and single values.
    """
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(item) for item in data]
    else:
        return data
