from abc import ABC, abstractmethod

class Scrapper(ABC):
    @abstractmethod
    def get_ads(self, num_of_pages=None):
        pass
