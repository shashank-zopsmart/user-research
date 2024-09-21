import abc

class ScraperAdapter(abc.ABC):
    @abc.abstractmethod
    def scrape(self, query, max_results=100):
        pass