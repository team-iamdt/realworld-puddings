class NotFoundError(Exception):
    def __init__(self, find_by: str):
        self.find_by = find_by

    def __str__(self):
        return f"Object Not Found, Find by: {self.find_by}."
