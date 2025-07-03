class DomainException(Exception):
    def __init__(self, message: str, details: str = "", http_code: int = 400):
        self.message = message
        self.details = details
        self.http_code = http_code
        super().__init__(self.message)
