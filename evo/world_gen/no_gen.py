from evo.world import World
from evo.world_gen.world_generator import WorldGenerator
from evo.util.registry import register_world_gen


@register_world_gen('no_gen')
class NoWorldGen(WorldGenerator):

    def generate(self, world: World):
        pass
