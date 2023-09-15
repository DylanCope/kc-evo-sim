from pathlib import Path
from evo.organism import Organism
from evo.util.callback import Callback
from evo.util.registry import register_callback

import yaml
from evo.world import World
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


def save_genomes_to_file(world: World, path: str) -> str:
    genomes = np.array([org.genome.genes for org in world.organisms])
    path = f'{path}.npy'
    np.save(path, genomes)
    return path


def load_world_from_genomes(genomes_file: str, config: dict) -> World:
    genomes = np.load(genomes_file)
    world = World(config)
    for genome in genomes:
        world.add_organism(Organism(config, genome))
    return world


@register_callback('logger')
class LoggerCallback(Callback):

    def __init__(self, config: dict, callback_name: str) -> None:
        super().__init__(config, callback_name)
        self.history = []
        self.experiment_dir = self.global_config['experiment_dir']
        self.n_generations = self.global_config['n_generations']

        self.log_frequency = self._get_param('log_frequency')
        self.plot_metrics = self._get_param('plot_metrics')
        self.plot_frequency = self._get_param('plot_frequency')
        self.log_to_stdout = self._get_param('log_to_stdout')
        self.should_save_genomes = self._get_param('save_genomes')
        self.save_genomes_frequency = self._get_param('save_genomes_frequency')

        if self.save_genomes:
            self.genomes_dir = f'{self.experiment_dir}/genomes'
            Path(self.genomes_dir).mkdir(parents=True, exist_ok=True)
        else:
            self.genomes_dir = None

    def _get_param(self, param_name: str):
        param = self.config.get(param_name, param_name)
        assert param is not None, f'{param_name} not specified in logger config'
        return param

    def get_metric_array(self, metric: str) -> np.array:
        return np.array([log[metric] for log in self.history])

    def on_generation_finish(self,
                             generation: int,
                             generation_logs: dict,
                             world: World):
        if self.should_save_genomes and (generation % self.save_genomes_frequency == 0
                                         or generation == self.n_generations - 1):
            path = f'{self.genomes_dir}/genomes_{generation:06d}'
            generation_logs['genomes_ckpt'] = save_genomes_to_file(world, path)

        self.history.append(generation_logs)
        self.save_history()

        if self.log_to_stdout and (generation % self.log_frequency == 0
                                   or generation == self.n_generations - 1):
            self.log_generation_info(generation_logs)

        if generation % self.plot_frequency == 0 or generation == self.n_generations - 1:
            self.make_plots()

    def save_genomes(self, generation_logs: dict):
        genomes = generation_logs['genomes']
        generation = generation_logs['generation']
        np.save(f'{self.experiment_dir}/genomes_{generation:06d}', genomes)

    def log_generation_info(self, generation_logs: dict):
        print(yaml.dump(generation_logs, default_flow_style=False))

    def make_plots(self):
        generations = self.get_metric_array('generation')
        for metric in self.plot_metrics:
            plt.plot(generations, self.get_metric_array(metric))
            plt.title(metric)
            plt.savefig(f'{self.experiment_dir}/{metric}.png')
            plt.clf()

    def on_interrupt(self) -> None:
        self.save_history()

    def save_history(self):
        with open(f'{self.experiment_dir}/history.yaml', 'w') as history_file:
            yaml.dump(self.history, history_file, default_flow_style=False)
