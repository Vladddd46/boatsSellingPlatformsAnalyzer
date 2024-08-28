from abc import ABC, abstractmethod


class Scrapper(ABC):
    @abstractmethod
    async def get_ads(self, num_of_pages=None):
        pass
