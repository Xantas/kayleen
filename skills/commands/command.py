import enum
from abc import ABC, abstractmethod


class Command(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_name(self) -> str:
        pass



