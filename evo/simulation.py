from evo.world import World
from evo.organism import Organism
from evo.selection import get_selection_function
from evo.repopulation import get_repop_function


class RunCallbacks:

    def __init__(self):
        self.on_step_finish_callbacks = []
        self.on_iteration_finish_callbacks = []

    def add_on_step_finish(self, callback):
        self.on_step_finish_callbacks.append(callback)

    def add_on_iteration_finish(self, callback):
        self.on_iteration_finish_callbacks.append(callback)

    def on_step_finish(self, world: World) -> dict:
        logs = {}
        for callback in self.on_step_finish_callbacks:
            logs.update(callback(world))
        return logs

    def on_iteration_finish(self, iteration_logs: dict) -> None:
        logs = {}
        for callback in self.on_iteration_finish_callbacks:
            logs.update(callback(iteration_logs))
        return logs


class EvolutionSimulation:

    def __init__(self, config: dict, callbacks: RunCallbacks = None):
        self.config = config
        self.callbacks = callbacks or RunCallbacks()

        self.steps_per_iteration = config.get('world_steps_per_iteration')
        assert self.steps_per_iteration is not None, \
            'world_steps_per_iteration not specified in config'

        self.world = World(config)

        self.pop_size = config.get('pop_size')
        assert self.pop_size is not None, \
            'pop_size not specified in config'

        for _ in range(self.pop_size):
            self.world.add_organism(Organism.random_organism(config))

        self.selection = get_selection_function(config)
        self.repopulate = get_repop_function(config)

    def simulate(self) -> None:
        iteration_logs = dict()
        self.world.reset()
        for _ in range(self.steps_per_iteration):
            self.world.update()
            iteration_logs.update(self.callbacks.add_on_step_finish(self.world))
        return iteration_logs

    def run_iteration(self) -> dict:
        """
        Runs a single iteration of the simulation.
        """
        iteration_logs = self.simulate()
        iteration_logs.update(self.selection())
        iteration_logs.update(self.repopulate())
        iteration_logs.update(self.callbacks.on_iteration_finish(iteration_logs))
        return iteration_logs
