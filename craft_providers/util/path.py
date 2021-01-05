"""Path-related helpers."""
import pathlib
import shutil
from typing import Optional


def which(command: str) -> Optional[pathlib.Path]:
    """A pathlib.Path wrapper for shutil.which().

    Args:
        command: Which command to find (e.g. "my-executable").

    Returns:
        Path to command if found, else None.
    """
    path = shutil.which(command)
    if path:
        return pathlib.Path(path)

    return None


def which_required(command: str) -> pathlib.Path:
    """A pathlib.Path wrapper for shutil.which().

    Args:
        command: Which command to find (e.g. "my-executable").

    Raises:
        RuntimeError: If command not found.
    """
    path = which(command)
    if path is None:
        raise RuntimeError(f"Missing required command {command!r}.")

    return path
