from abc import ABC, abstractmethod

class Managing_class(ABC):
    @staticmethod
    @abstractmethod
    async def parse_json(*args):
        pass

    @staticmethod
    @abstractmethod
    async def scrape(*args):
        pass