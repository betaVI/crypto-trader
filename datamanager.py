import json

class DataManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.operations = self.loadOperations()

    def loadOperations(self):
        with open(self.filepath) as f:
            return json.load(f)

    def lastOpResults(self):
        if len(self.operations) == 0:
            return {}
        return self.operations[-1]

    def addOperation(self, operation):
        self.operations.append(operation)
        self.save()

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.operations, f, indent = 4, sort_keys=True)
