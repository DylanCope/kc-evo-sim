from evo.simulation import EvolutionSimulation, RunCallbacks
from evo.render import RenderVideoCallback

from pathlib import Path
import yaml


class ExperimentRunner:

    def __init__(self, config):
        self.n_iterations = config.get('n_iterations')
        assert self.n_iterations is not None, \
            'n_iterations not specified in config'

        self.name = config.get('experiment_name')
        self.experiment_dir = f'experiments/logs/{self.name}_{hash(self)}'
        Path(self.experiment_dir).mkdir(parents=True, exist_ok=True)

        print('Running simulation with config:')
        print(yaml.dump(config, default_flow_style=False))

        callbacks = RunCallbacks([
            RenderVideoCallback(config.get('video_frequency'),
                                videos_dir=self.experiment_dir + '/videos')
        ])

        self.simualtion = EvolutionSimulation(config, callbacks=callbacks)

        self.history = []

    def run(self):
        self.history = []
        for iteration in range(1, self.n_iterations + 1):
            print(f'Iteration {iteration}')
            iteration_logs = self.simualtion.run_iteration(iteration)
            self.log_iteration(iteration_logs)
            self.history.append(iteration_logs)
            self.save_history()

    def save_history(self):
        with open(f'{self.experiment_dir}/history.yaml', 'w') as history_file:
            yaml.dump(self.history, history_file, default_flow_style=False)

    def log_iteration(self, iteration_logs: dict) -> None:
        print(yaml.dump(iteration_logs, default_flow_style=False))


def load_config(config_name: str):
    with open(f'experiments/config/{config_name}.yaml') as config_file:
        config = yaml.load(config_file)

    if 'inherits_from' in config:
        parent_config = load_config(config['inherits_from'])
        config = {**parent_config, **config}
    elif config_name != 'default_config':
        parent_config = load_config('default_config')
        config = {**parent_config, **config}

    return config
