check = {
    "properties": {
        "name": {"type": "string"},
        "tags": {"type": "string"},
        "timeout": {"type": "number", "minimum": 60, "maximum": 604800},
        "grace": {"type": "number", "minimum": 60, "maximum": 604800},
        "nag": {"type": "number", "minimum": 60, "maximum": 604800},
        "nag_mode": {"type": "string"},
        "channels": {"type": "string"}
    }
}
