from abc import ABC, abstractmethod
from typing import List

from .data import DataAsset


class Task(ABC):
    """
    Abstract base class for all tasks.
    """

    @property
    @abstractmethod
    def docker_image(self) -> str:
        """The Docker image URI for this task."""
        pass

    @property
    @abstractmethod
    def entrypoint(self) -> List[str]:
        """The entrypoint command for this task."""
        pass

    @property
    @abstractmethod
    def data_assets(self) -> List[DataAsset]:
        """List of data assets required by this task."""
        pass

    @abstractmethod
    def get_overrides(self) -> List[str]:
        """
        Generate the list of command-line overrides/arguments
        to pass to the entrypoint.
        """
        pass
