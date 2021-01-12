import json

class DataManager:
    def __init__(self, filepath):
        self.filepath = filepath

    def loadData(self):
        try:
            with open(self.filepath) as f:
                return json.load(f)
        except Exception:
            return []

    def saveData(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent = 4, sort_keys=True)
