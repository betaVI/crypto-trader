import json

class DataManager:
    def __init__(self):
        self.operations = self.loadOperations()

    def loadOperations(self):
        with open('data.json') as f:
            return json.load(f)

    def lastOpResults(self):
        if len(self.operations) == 0:
            return {}
        return self.operations[-1]

    def addOperation(self, operation, price):
        self.operations.append({
            'operation':operation,
            'lastOpPrice':price
        })
        self.save()

    def save(self):
        with open('data.json', 'w') as f:
            json.dump(self.operations, f, indent = 4, sort_keys=True)
