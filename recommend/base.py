from abc import ABC, abstractmethod


class BaseRecommender(ABC):

    @abstractmethod
    def recommend(self, preferences, duration, weather, attractions):
        raise NotImplementedError
