check = {
    "properties": {
        "name": {"type": "string"},
        "tags": {"type": "string"},
        "timeout": {"type": "number", "minimum": 60, "maximum": 604800},
        "grace": {"type": "number", "minimum": 60, "maximum": 604800},
        "channels": {"type": "string"},
        "priority": {"type": "number", "minimum": -2, "maximum": 2}
    }
}
