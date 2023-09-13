import random
from dataclasses import dataclass
from typing import List, Optional

import numpy as np


class Action:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

    @staticmethod
    def all_actions() -> List['Action']:
        return [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

    @staticmethod
    def num_actions(_: dict) -> int:
        return len(Action.all_actions())

    @staticmethod
    def from_index(index: int) -> 'Action':
        return Action.all_actions()[index]

    @staticmethod
    def to_tuple(action: str) -> tuple:
        if action == Action.UP:
            return (0, -1)
        elif action == Action.DOWN:
            return (0, 1)
        elif action == Action.LEFT:
            return (-1, 0)
        elif action == Action.RIGHT:
            return (1, 0)


@dataclass
class LocalWorldState:
    x: int
    y: int
    local_cells: List[Optional['Organism']] = None
    world_metadata: dict = None

    @staticmethod
    def num_observations(config: dict) -> int:
        n_coords = 2  # x and y

        assert config.get('include_diagonal_cells') is not None, \
            'include_diagonal_cells not specified in config'

        if config.get('include_diagonal_cells'):
            n_local_cells = 8  # up, down, left, right, and diagonals
        else:
            n_local_cells = 4  # only up, down, left, right

        return n_coords + n_local_cells


class FeedForwardNeuralNetwork:

    def __init__(self, layer_weights: List[np.ndarray]) -> None:
        self.layers_weights = layer_weights

    def forward(self, inputs: List[float]) -> List[float]:
        x = np.concatenate([np.array(inputs), [1.]])
        for layer_idx, weight_matrix in enumerate(self.layers_weights):
            x = np.matmul(x, weight_matrix)
            x = np.tanh(x)
            if layer_idx < len(self.layers_weights) - 1:
                x = np.concatenate([x, [1.]])
        return x


class Genome:

    def __init__(self, genes: List[float], config: dict) -> None:
        self.genes = genes
        self.config = config

        self.mutation_rate = config.get('mutation_rate')
        assert self.mutation_rate is not None, \
            'Mutation rate not specified in config'

    @staticmethod
    def random_gene_value() -> float:
        """ Returns a random value between -1 and 1. """
        return 2 * random.random() - 1

    @staticmethod
    def random_genome(config: dict) -> 'Genome':
        """
        Creates a random genome.
        A genome is a list of floating point numbers that encodes all
        the weights of a small feedforward neural network.

        Args:
            config: A dictionary containing the configuration parameters
                for the genome. It must contain the key 'hidden_layer_dims',
                which is a list of integers specifying the number of neurons
                in each hidden layer.

        Returns:
            A Genome object.
        """
        hidden_layer_dims = config.get('hidden_layer_dims')
        assert hidden_layer_dims is not None, \
            'Hidden layer dims not specified in config'

        # input sizes at each layer
        input_sizes = [LocalWorldState.num_observations(config)] + hidden_layer_dims
        # output sizes at each layer
        output_sizes = hidden_layer_dims + [Action.num_actions(config)]

        # we compute the total number of genes needed for each layer
        # by multiplying the input dimension by the output dimension
        num_genes = 0
        for inp_dim, out_dim in zip(input_sizes, output_sizes):
            inp_dim += 1  # add 1 input for the bias
            num_genes += inp_dim * out_dim

        # create a list of random genes of the correct length
        genes = [Genome.random_gene_value() for _ in range(num_genes)]

        return Genome(genes, config)

    def copy(self) -> 'Genome':
        return Genome([v for v in self.genes], self.config)

    def maybe_mutate(self) -> None:
        if random.random() < self.mutation_rate:
            # pick a random gene in the list
            i = random.randint(0, len(self.genes) - 1)

            # change it to a new random value
            self.genes[i] = self.random_gene_value()

    def crossover(self, other: 'Genome') -> 'Genome':
        assert len(self.genes) == len(other.genes), \
            'Genomes must have the same length'

        new_genes = []
        for i in range(len(self.genes)):
            # randomly pick a gene from either parent
            # and add it to the new genome
            if random.random() < 0.5:
                new_genes.append(self.genes[i])
            else:
                new_genes.append(other.genes[i])

        return Genome(new_genes, self.config)

    def make_brain(self) -> FeedForwardNeuralNetwork:
        hidden_layers = self.config.get('hidden_layer_dims')
        assert hidden_layers is not None, \
            'Hidden layer dims not specified in config'

        # input sizes at each layer
        input_sizes = [LocalWorldState.num_observations(self.config)] + hidden_layers
        # output sizes at each layer
        output_sizes = hidden_layers + [Action.num_actions(self.config)]

        i = 0
        layers = []
        for input_dim, output_dim in zip(input_sizes, output_sizes):
            input_dim += 1  # add 1 input for the bias
            # get the weights for this layer
            weights = np.array(self.genes[i:i + input_dim * output_dim])
            # reshape them into a matrix
            weights = weights.reshape((input_dim, output_dim))
            # add the weights to the list of layers
            layers.append(weights)
            # update the index
            i += input_dim * output_dim

        return FeedForwardNeuralNetwork(layers)


class Organism:

    def __init__(self, config: dict, genome: Genome) -> None:
        self.local_world_state: Optional[LocalWorldState] = None
        self.genome = genome
        self.brain = genome.make_brain()
        self.brain_inputs = np.array([0.] * LocalWorldState.num_observations(config))
        self.config = config
        self.world_width = config.get('world_width')
        assert self.world_width is not None, \
            'World width not specified in config'
        self.world_height = config.get('world_width')
        assert self.world_height is not None, \
            'World height not specified in config'

    def update_brain_inputs(self) -> None:
        self.brain_inputs[0] = self.local_world_state.x / self.world_width
        self.brain_inputs[1] = self.local_world_state.y / self.world_height
        for i, cell in enumerate(self.local_world_state.local_cells):
            if cell is None:
                self.brain_inputs[i + 2] = 0.
            else:
                self.brain_inputs[i + 2] = 1.

    def get_action(self) -> Action:
        self.update_brain_inputs()
        outputs = self.brain.forward(self.brain_inputs)
        action_index = np.argmax(outputs)
        return Action.from_index(action_index)

    def reproduce(self, other: Optional['Organism'] = None) -> 'Organism':
        if other is None:
            return Organism(self.config, self.genome.copy().maybe_mutate())

        new_genome = self.genome.crossover(other.genome)
        new_genome.maybe_mutate()
        return Organism(self.config, new_genome)

    @staticmethod
    def random_organism(config: dict) -> 'Organism':
        return Organism(config, Genome.random_genome(config))
