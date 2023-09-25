from evo.selection.selection_fn import SelectionFunction
from evo.util.registry import register_selection_fn
from evo.organism import Organism
from evo.world import World


class RegionBasedSelectionFunction(SelectionFunction):

    def in_survival_region(self, world: World, x: int, y: int) -> bool:
        raise NotImplementedError()

    def selection_fn(self, world: World, organism: Organism) -> bool:
        x = organism.local_world_state.x
        y = organism.local_world_state.y
        return self.in_survival_region(world, x, y)


@register_selection_fn('one_side_survive')
class SelectionFunctionOneSideSurvive(RegionBasedSelectionFunction):

    def __init__(self, config: dict, method: str = 'one_side_survive'):
        super().__init__(config, method)
        self.survival_region_proportion = self.selection_config.get('survival_region_proportion')
        assert self.survival_region_proportion is not None, \
            'survival_region_proportion not specified in config'

        self.survival_side = self.selection_config.get('survival_side')
        assert self.survival_side is not None, \
            'survival_side not specified in config'

        assert self.survival_side in ['left', 'right', 'top', 'bottom'], \
            'survival_side must be one of [left, right, top, bottom]'

    def in_survival_region(self, world: World, x: int, y: int) -> bool:
        if self.survival_side == 'left':
            return x / world.world_width < self.survival_region_proportion
        elif self.survival_side == 'right':
            return x / world.world_width > 1 - self.survival_region_proportion
        elif self.survival_side == 'top':
            return y / world.world_height < self.survival_region_proportion
        elif self.survival_side == 'bottom':
            return y / world.world_height > 1 - self.survival_region_proportion
