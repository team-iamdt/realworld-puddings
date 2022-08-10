class MissingDependencyError(Exception):
    def __init__(self, field):
        super(self).__init__()
        self.field = field

    def __str__(self):
        return f"Missing dependency for: {self.field}."
