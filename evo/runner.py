from evo.simulation import EvolutionSimulation, RunCallbacks
from evo.util.registry import get_callback

from pathlib import Path
import yaml

from evo.util import get_timestamp, merge_dicts_recursively


class ExperimentRunner:

    def __init__(self, config):
        self.n_generations = config.get('n_generations')
        assert self.n_generations is not None, \
            'n_generations not specified in config'

        self.name = config.get('experiment_name')
        self.experiment_dir = f'experiments/runs/{self.name}/run_{get_timestamp()}_{hash(self)}'
        Path(self.experiment_dir).mkdir(parents=True, exist_ok=True)
        config['experiment_dir'] = self.experiment_dir

        print('Running simulation with config:')
        print(yaml.dump(config, default_flow_style=False))

        with open(f'{self.experiment_dir}/config.yaml', 'w') as config_file:
            yaml.dump(config, config_file, default_flow_style=False)

        self.callbacks = RunCallbacks([
            get_callback(config, callback_name)
            for callback_name in config.get('callbacks', [])
        ])

        self.simulation = EvolutionSimulation(config, callbacks=self.callbacks)

    def run(self):
        try:
            for generation in range(0, self.n_generations):
                self.simulation.run_generation(generation)

        except KeyboardInterrupt:
            self.callbacks.on_interrupt(self.simulation.world)

        except Exception as e:
            self.callbacks.on_interrupt(self.simulation.world)
            self._handle_exception(e)

    def _handle_exception(self, e):
        crash_dir = f'{self.experiment_dir}/crash'
        Path(crash_dir).mkdir(parents=True, exist_ok=True)

        import traceback

        with open(f'{crash_dir}/exception_trace.txt', 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())

        raise e


def load_config(config_name: str):
    with open(f'experiments/config/{config_name}.yaml') as config_file:
        config = yaml.load(config_file)

    if 'inherits_from' in config:
        parent_config = load_config(config['inherits_from'])
        config = merge_dicts_recursively(parent_config, config)

    elif config_name != 'default_config':
        parent_config = load_config('default_config')
        config = merge_dicts_recursively(parent_config, config)

    return config
