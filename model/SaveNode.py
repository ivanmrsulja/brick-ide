class SaveNode(object):
    def __init__(self, path):
        self.data = ""
        self.saved = True
        self.path = path

    def save(self):
        with open(self.path, "w") as file:
            file.write(self.data)

    def get_data(self):
        return self._data
