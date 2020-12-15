class CompatibilityError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason

    def __repr__(self) -> str:
        return f"CompatibilityError(reason={self.reason})"

    def __str__(self) -> str:
        return self.reason
