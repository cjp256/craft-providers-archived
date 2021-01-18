"""Image errors."""


class CompatibilityError(Exception):
    """Compatibility error.

    :param reason: Reason for incompatibility.
    """

    def __init__(self, reason: str) -> None:
        super().__init__()
        self.reason = reason

    def __repr__(self) -> str:
        """Return representation."""
        return f"CompatibilityError(reason={self.reason})"

    def __str__(self) -> str:
        """Return string representation."""
        return self.reason
