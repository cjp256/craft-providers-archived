import logging
from abc import ABC, abstractmethod

from craft_providers import Executor

logger = logging.getLogger(__name__)


class Image(ABC):
    """Image Configurator.

    Attributes:
        name: Name of image (typically the version alias).
        revision: Compatibility / revision of setup.
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
