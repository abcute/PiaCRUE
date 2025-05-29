import abc
from typing import Any

class PerceptionModule(abc.ABC):
    """
    Abstract base class for perception modules.
    """

    @abc.abstractmethod
    def perceive(self, sensory_data: dict) -> None:
        """
        Processes raw sensory input.

        Args:
            sensory_data: A dictionary containing raw sensory data.
        """
        pass

    @abc.abstractmethod
    def process_sensory_input(self, processed_data: dict) -> Any:
        """
        Further processes or interprets the perceived data.

        Args:
            processed_data: A dictionary containing processed sensory data.

        Returns:
            Any: The result of the processing, can be any type.
        """
        pass
