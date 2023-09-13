from evo.simulation import EvolutionSimulation

import argparse
import yaml


class ExperimentRunner:

    def __init__(self, config):
        self.n_iterations = config.get('n_iterations')
        assert self.n_iterations is not None, \
            'n_iterations not specified in config'
        self.simualtion = EvolutionSimulation(config)

    def run(self):
        for iteration in range(self.n_iterations):
            print(f'Iteration {iteration}')
            iteration_logs = self.simualtion.run_iteration()
            self.log_iteration(iteration_logs)


def get_config(config_name: str):
    with open(f'experiments/config/{config_name}.yaml') as config_file:
        config = yaml.load(config_file)

    if 'inherits_from' in config:
        parent_config = get_config(config['inherits_from'])
        config = {**parent_config, **config}
    elif config_name != 'default_config':
        parent_config = get_config('default_config')
        config = {**parent_config, **config}

    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', type=str, default='default_config',
                        help='Name of the experiment YAML in the experiments/configs directory')
    args = parser.parse_args()

    config = get_config(args.experiment)

    runner = ExperimentRunner(config)
    runner.run()


if __name__ == '__main__':
    main()
