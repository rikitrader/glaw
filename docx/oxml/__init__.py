class OxmlElement(dict):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    def append(self, value):
        self.setdefault("children", []).append(value)

    def set(self, key, value):
        self[key] = value
