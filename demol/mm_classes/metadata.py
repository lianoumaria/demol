class Metadata:
    def __init__(self, parent, name, description, author, os):
        self.parent = parent
        self.name = name
        self.description = description
        self.author = author
        self.os = os

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'os': self.os,
        }

