"""Image errors."""


class CompatibilityError(Exception):
    """Compatibility error.

    Attributes:
        reason: Reason for incompatibility.
    """

    def __init__(self, reason: str) -> None:
        super().__init__()
        self.reason = reason

    def __repr__(self) -> str:
        return f"CompatibilityError(reason={self.reason})"

    def __str__(self) -> str:
        return self.reason
