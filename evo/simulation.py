from evo.world import World
from evo.organism import Organism
from evo.selection import get_selection_function
from evo.repopulation import get_repop_function


class RunCallbacks:

    def __init__(self, callbacks=None):
        self.callbacks = callbacks or []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def on_step_finish(self, iteration: int, world: World) -> dict:
        logs = {}
        for callback in self.callbacks:
            logs.update(callback.on_step_finish(iteration, world))
        return logs

    def on_iteration_finish(self, iteration: int, iteration_logs: dict) -> None:
        logs = {}
        for callback in self.callbacks:
            logs.update(callback.on_iteration_finish(iteration, iteration_logs))
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

        print(f'Creating initial population of {self.pop_size} organisms')
        for _ in range(self.pop_size):
            self.world.add_organism(Organism.random_organism(config))

        self.selection = get_selection_function(config)
        self.repopulate = get_repop_function(config)

    def simulate(self, iteration: int) -> None:
        iteration_logs = {'iteration': iteration}
        self.world.reset()
        for _ in range(self.steps_per_iteration):
            self.world.update()
            iteration_logs.update(self.callbacks.on_step_finish(iteration, self.world))
        return iteration_logs

    def run_iteration(self, iteration: int) -> dict:
        """
        Runs a single iteration of the simulation.
        """
        iteration_logs = self.simulate(iteration)
        iteration_logs.update(self.selection(self.world))
        iteration_logs.update(self.repopulate(self.world))
        iteration_logs.update(self.callbacks.on_iteration_finish(iteration, iteration_logs))
        return iteration_logs
