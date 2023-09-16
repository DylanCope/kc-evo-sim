from evo.world import World

from abc import ABC, abstractmethod


class WorldGenerator(ABC):

    def __init__(self, global_config: dict, generator_name: str) -> None:
        self.global_config = global_config
        self.config = global_config.get('world_gen', dict())
        self.generator_name = generator_name

    @abstractmethod
    def generate(self, world: World):
        pass
