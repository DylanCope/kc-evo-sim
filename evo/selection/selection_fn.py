from evo.organism import Organism
from evo.world import World

from abc import ABC


class SelectionFunction(ABC):

    def __init__(self, config: dict, method: str):
        self.method = method
        self.selection_config = config.get('selection_config')

    def __call__(self, world: World) -> dict:
        return self.select(world)

    def selection_fn(self, world: World, organism: Organism) -> bool:
        raise NotImplementedError()

    def select(self, world: World) -> dict:
        initial_population = world.current_population

        to_kill = []

        # create a list of organisms to kill
        # Note: we can't kill them in the loop because it would
        # attempt to modify the list we're iterating over
        for organism in world.organisms:
            if not self.selection_fn(world, organism):
                to_kill.append(organism)

        for organism in to_kill:
            world.kill_organism(organism)

        final_population = world.current_population

        return {
            'surviving_population_size': final_population,
            'survival_rate': final_population / initial_population
        }
