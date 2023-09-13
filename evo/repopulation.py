from evo.organism import Organism
from evo.world import World

from abc import ABC
import random


class RepopFunction(ABC):

    def __init__(self, config: dict):
        self.config = config
        self.target_population_size = config.get('pop_size')

    def __call__(self, world: World) -> dict:
        return self.repopulate(world)

    def create_new_organism(self, world: World) -> bool:
        raise NotImplementedError()

    def repopulate(self, world: World) -> dict:
        to_create = self.target_population_size - world.current_population
        for _ in range(to_create):
            new_organism = self.create_new_organism(world)
            world.add_organism(new_organism)

        return {
            'n_new_organisms': to_create
        }


class RandomCrossoverRepop(RepopFunction):

    def create_new_organism(self, world: World) -> bool:
        organism1: Organism = random.choice(world.organisms)
        organism2: Organism = random.choice(world.organisms)
        return organism1.reproduce(organism2)


def get_repop_function(config: dict) -> RepopFunction:

    repop_method = config.get('repop_method')
    if repop_method is None:
        raise Exception('repop_method not specified in config')

    if repop_method == 'random_crossover':
        return RandomCrossoverRepop(config)

    raise Exception(f'Unknown repop_method: {repop_method}')
