import random
from evo.organism import Organism
from evo.repop.repop_fn import RepopFunction
from evo.util.registry import register_repop_fn
from evo.world import World


@register_repop_fn('random_crossover')
class RandomCrossoverRepop(RepopFunction):

    def create_new_organism(self, world: World) -> bool:
        organism1: Organism = random.choice(world.organisms)
        organism2: Organism = random.choice(world.organisms)
        return organism1.reproduce(organism2)
