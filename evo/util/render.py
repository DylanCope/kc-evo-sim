from evo.selection.region_based_selection import RegionBasedSelectionFunction, SelectionFunction
from evo.util.registry import get_selection_function, register_callback
from evo.world import World
from evo.organism import Organism
from evo.util.callback import Callback

from typing import List
from pathlib import Path

import numpy as np
import imageio
import pygame
import os


# set SDL to use the dummy NULL video driver,
#   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.display.init()
PYGAME_WINDOW = None
WHITE = (255, 255, 255)
LIGHT_GREEN = (192, 255, 158)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)


@register_callback('render_video')
class RenderVideoCallback(Callback):

    def __init__(self, global_config: dict, callback_name: str = 'render_video'):
        super().__init__(global_config, callback_name)

        self.frequency = self.config.get('video_frequency')
        assert self.frequency is not None, 'frequency not specified in render_video config'

        self.fps = self.config.get('fps')
        assert self.fps is not None, 'fps not specified in render_video config'

        self.n_generations = global_config.get('n_generations')
        self.videos_dir = global_config.get('experiment_dir') + '/videos'
        Path(self.videos_dir).mkdir(parents=True, exist_ok=True)

        self.sim_selection_fn = get_selection_function(global_config)
        self.frames = []

    def is_video_generation(self, generation: int) -> bool:
        return generation % self.frequency == 0 or generation == self.n_generations - 1

    def on_step_finish(self, generation: int, world: World) -> dict:
        logs = {}

        if self.is_video_generation(generation):
            frame = render_world(world, self.sim_selection_fn)
            self.frames.append(frame)

        return logs

    def on_generation_finish(self, generation: int, generation_logs: dict, _: World) -> None:
        if self.is_video_generation(generation):
            video_path = f'{self.videos_dir}/generation_{generation:06d}'
            generation_logs['video_save_file'] = save_video(self.frames, video_path, fps=self.fps)
            self.frames = []


def get_organism_colour(organism: Organism) -> tuple:
    genes = organism.genome.genes
    n_genes = len(genes)
    red_genes = genes[:n_genes // 3]
    green_genes = genes[n_genes // 3:2 * n_genes // 3]
    blue_genes = genes[2 * n_genes // 3:]

    def genes_to_colour(genes):
        return 50 + int((np.mean(genes) % 1.0) * 150)

    return (genes_to_colour(red_genes),
            genes_to_colour(green_genes),
            genes_to_colour(blue_genes))


def render_world(world: World,
                 sim_selection_fn: SelectionFunction = None) -> np.ndarray:
    """
    Renders the world.

    Args:
        world (World): The world to render.

    Returns:
        np.ndarray: The pixel array of the rendered world.
    """

    # cell_width = WINDOW_SIZE / world.world_width
    # cell_height = WINDOW_SIZE / world.world_height
    cell_height = 16
    cell_width = 16

    global PYGAME_WINDOW
    if PYGAME_WINDOW is None:
        window_width = int(cell_width * world.world_width)
        window_height = int(cell_height * world.world_height)
        PYGAME_WINDOW = pygame.display.set_mode((window_width, window_height))

    PYGAME_WINDOW.fill(WHITE)

    def get_cell_rect(x: int, y: int):
        return (
            y * cell_width, x * cell_height,
            cell_width, cell_height
        )

    def get_cell_circle(x: int, y: int):
        return (
            int(y * cell_width + cell_width / 2),
            int(x * cell_height + cell_height / 2)
        )

    if isinstance(sim_selection_fn, RegionBasedSelectionFunction):
        for x in range(world.world_width):
            for y in range(world.world_height):
                if sim_selection_fn.in_survival_region(world, x, y):
                    rect = get_cell_rect(x, y)
                    pygame.draw.rect(PYGAME_WINDOW, LIGHT_GREEN, rect)

    for (x, y), value in world.occupied_cells.items():
        rect = get_cell_rect(x, y)
        if isinstance(value, Organism):
            pygame.draw.ellipse(PYGAME_WINDOW, get_organism_colour(value), rect)
        else:
            pygame.draw.rect(PYGAME_WINDOW, DARK_GRAY, rect)

    # returns the pixel array of the pygame window as a numpy array
    return pygame.surfarray.array3d(pygame.display.get_surface())


def save_video(frames: List[np.ndarray],
               file_path: str = 'video',
               format='mp4',
               fps: int = 30) -> str:
    """
    Saves a video of the policy being evaluating in an environment.

    Args:
        frames (List[np.ndarray]): The frames of the video.
        file_path (str): The path of the file to save the video to.
        fps (int): The frames per second of the video.

    Returns:
        str: The path to the saved video.
    """
    if not file_path.endswith(f'.{format}'):
        file_path = file_path + f'.{format}'

    imageio.mimwrite(file_path, frames, fps=fps)

    return file_path
