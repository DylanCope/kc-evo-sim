from evo.world import World
from evo.world_gen.world_generator import WorldGenerator
from evo.util.registry import register_world_gen


class Barrier:
    pass


@register_world_gen('simple_barriers')
class SimpleBarriersWorldGen(WorldGenerator):
    """
    Simple barriers world generator.

    Barriers are specified in the config as a list of tuples, where each tuple
    is of the form (x, y, width, height). These are measured as a proportion of
    the world size, so for example a barrier at (0.5, 0.5, 0.1, 0.1) would be
    a square in the middle of the world (assuming the world is a square).

    """

    def __init__(self, global_config: dict, generator_name: str) -> None:
        super().__init__(global_config, generator_name)
        self.world_width = self.global_config.get('world_width')
        self.world_height = self.global_config.get('world_height')
        self.barriers = [
            (int(x * self.world_width), int(y * self.world_height),
             max(1, int(w * self.world_width)), max(1, int(h * self.world_height)))
            for x, y, w, h in self.config.get('barriers')
        ]

    def generate(self, world: World):
        for x, y, w, h in self.barriers:
            for i in range(x, x + w):
                for j in range(y, y + h):
                    world.set_cell(i, j, Barrier())
