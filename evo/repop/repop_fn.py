from evo.organism import Organism
from evo.world import World

from abc import ABC


class RepopFunction(ABC):

    def __init__(self, config: dict, method: str):
        self.method = method
        self.config = config
        self.target_population_size = config.get('pop_size')

    def __call__(self, world: World) -> dict:
        return self.repopulate(world)

    def create_new_organism(self, world: World) -> Organism:
        raise NotImplementedError()

    def repopulate(self, world: World) -> dict:
        to_create = self.target_population_size - world.current_population
        for _ in range(to_create):
            new_organism = self.create_new_organism(world)
            world.add_organism(new_organism)

        return {
            'n_new_organisms': to_create
        }
