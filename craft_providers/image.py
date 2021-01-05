"""Image module."""
import logging
from abc import ABC, abstractmethod

from .executor import Executor

logger = logging.getLogger(__name__)


class Image(ABC):  # pylint: disable=too-few-public-methods
    """Image Configurator.

    Images encapsulate the logic required to setup a base image upon initial
    launch and restarting.  By extending this class, an application may include
    its own additional setup/update requirements.

    Args:
        name: Name of image (typically the version alias).
        revision: Image setup compatibility tag.  This is used to verify
            that an instance was setup in a manner that is compatible with the
            current setup.  If changes to the image's setup configuration break
            on previous instantations, this version string would be incremented,
            or otherwise modified to indicate a incompatible tag.

    Attributes:
        name (str): Name of image (typically the version alias).
        revision (str): Image setup compatibility tag.  This is used to verify
            that an instance was setup in a manner that is compatible with the
            current setup.  If changes to the image's setup configuration break
            on previous instantations, this version string would be incremented,
            or otherwise modified to indicate a incompatible tag.

    """

    def __init__(self, *, name: str, revision: str) -> None:
        self.name = name
        self.revision = revision

    @abstractmethod
    def setup(self, *, executor: Executor) -> None:
        """Setup instance.

        Raises:
            CompatibilityError: if executor instance is incompatible with image.

        """
        ...
