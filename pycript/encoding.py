import json
from base64 import b64encode

def encode_base64(data):
    # Convert dict to string
    if isinstance(data, dict):
        data = json.dumps(data)

    # Handle unicode (Jython)
    if isinstance(data, unicode):
        data = data.encode('utf-8')

    # Now base64 encode
    return b64encode(data).decode('utf-8')
