from evo.organism import Organism
from evo.world import World

from abc import ABC


class SelectionFunction(ABC):

    def __init__(self, selection_config: dict):
        self.selection_config = selection_config

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


class SelectionFunctionOneSideSurvive(SelectionFunction):

    def __init__(self, selection_config: dict):
        super().__init__(selection_config)
        self.survival_region_proportion = selection_config.get('survival_region_proportion')
        assert self.survival_region_proportion is not None, \
            'survival_region_proportion not specified in config'

        self.survival_side = selection_config.get('survival_side')
        assert self.survival_side is not None, \
            'survival_side not specified in config'

    def selection_fn(self, world: World, organism: Organism) -> dict:
        if self.survival_side == 'left':
            return organism.local_world_state.x / world.world_width < self.survival_region_proportion
        elif self.survival_side == 'right':
            return organism.local_world_state.x / world.world_width > 1 - self.survival_region_proportion
        elif self.survival_side == 'top':
            return organism.local_world_state.y / world.world_height < self.survival_region_proportion
        elif self.survival_side == 'bottom':
            return organism.local_world_state.y / world.world_height > 1 - self.survival_region_proportion


def get_selection_function(config: dict) -> SelectionFunction:
    selection_config = config.get('selection_config')
    if selection_config is None:
        raise Exception('selection_config not specified in config')

    selection_method = selection_config.get('method')
    if selection_method is None:
        raise Exception('selection_method not specified in config: ' + str(selection_config))

    if selection_method == 'one_side_survive':
        return SelectionFunctionOneSideSurvive(selection_config)

    raise Exception(f'Unknown selection_method: {selection_method}')
