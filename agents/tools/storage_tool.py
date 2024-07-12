import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

class StorageTool:
    def __init__(self, storage_file="storage.json"):
        self.storage_file = storage_file
        self.key_file = "secret.key"
        self.key = self.load_key()
        self.fernet = Fernet(self.key)

        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({}, f)

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)
        return key

    def load_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                return key_file.read()
        else:
            return self.generate_key()

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data):
        return self.fernet.decrypt(data.encode()).decode()

    def save(self, key, value):
        with open(self.storage_file, 'r+') as f:
            data = json.load(f)
            data[key] = {
                "value": self.encrypt(value),
                "storage_time": str(datetime.now()),
                "update_time": str(datetime.now())
            }
            f.seek(0)
            json.dump(data, f)
            f.truncate()

    def load(self, key):
        with open(self.storage_file, 'r') as f:
            data = json.load(f)
            if key in data:
                return {
                    "value": self.decrypt(data[key]["value"]),
                    "storage_time": data[key]["storage_time"],
                    "update_time": data[key]["update_time"]
                }
            return None

    def update(self, key, value):
        with open(self.storage_file, 'r+') as f:
            data = json.load(f)
            if key in data:
                data[key]["value"] = self.encrypt(value)
                data[key]["update_time"] = str(datetime.now())
                f.seek(0)
                json.dump(data, f)
                f.truncate()
            else:
                self.save(key, value)
