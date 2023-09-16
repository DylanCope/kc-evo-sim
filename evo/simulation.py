from evo.world import World
from evo.organism import Organism
from evo.util.registry import get_selection_function, get_repop_function, get_world_generator
from evo.util.callback import RunCallbacks
from evo.world_gen.world_generator import WorldGenerator


class EvolutionSimulation:

    def __init__(self, config: dict, callbacks: RunCallbacks = None):
        self.config = config
        self.callbacks = callbacks or RunCallbacks()

        self.steps_per_generation = config.get('world_steps_per_generation')
        assert self.steps_per_generation is not None, \
            'world_steps_per_generation not specified in config'

        self.world_generator: WorldGenerator = get_world_generator(config)
        self.world = World(config, self.world_generator)

        self.pop_size = config.get('pop_size')
        assert self.pop_size is not None, \
            'pop_size not specified in config'

        print(f'Creating initial population of {self.pop_size} organisms')
        for _ in range(self.pop_size):
            self.world.add_organism(Organism.random_organism(config))

        self.selection = get_selection_function(config)
        self.repopulate = get_repop_function(config)

    def simulate(self, generation: int) -> None:
        generation_logs = {'generation': generation}
        self.world.reset()
        for _ in range(self.steps_per_generation):
            self.world.update()
            generation_logs.update(self.callbacks.on_step_finish(generation, self.world))
        return generation_logs

    def run_generation(self, generation: int) -> dict:
        """
        Runs a single generation of the simulation.
        """
        generation_logs = self.simulate(generation)
        generation_logs.update(self.selection(self.world))
        generation_logs.update(self.repopulate(self.world))
        self.callbacks.on_generation_finish(generation, generation_logs, self.world)
        return generation_logs
