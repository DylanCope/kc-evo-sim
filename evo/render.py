from evo.selection import RegionBasedSelectionFunction, SelectionFunction
from evo.world import World

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
WINDOW_SIZE = 800
PYGAME_WINDOW = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
WHITE = (255, 255, 255)
LIGHT_GREEN = (192, 255, 158)
BLACK = (0, 0, 0)


class RenderVideoCallback:

    def __init__(self,
                 frequency: int,
                 n_iterations: int,
                 videos_dir: str = 'video',
                 fps: int = 5):
        self.frequency = frequency
        self.n_iterations = n_iterations
        self.videos_dir = videos_dir
        self.sim_selection_fn = None
        Path(self.videos_dir).mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.frames = []

    def is_video_iteration(self, iteration: int) -> bool:
        return iteration % self.frequency == 0 or iteration == self.n_iterations - 1

    def on_step_finish(self, iteration: int, world: World) -> dict:
        logs = {}

        if self.is_video_iteration(iteration):
            frame = render_world(world, self.sim_selection_fn)
            self.frames.append(frame)

        return logs

    def on_iteration_finish(self, iteration: int, iteration_logs: dict) -> None:
        logs = {}

        if self.is_video_iteration(iteration):
            video_path = f'{self.videos_dir}/iteration_{iteration:06d}'
            logs['video_save_file'] = save_video(self.frames, video_path, fps=self.fps)
            self.frames = []

        return logs


def render_world(world: World,
                 sim_selection_fn: SelectionFunction = None) -> np.ndarray:
    """
    Renders the world.

    Args:
        world (World): The world to render.

    Returns:
        np.ndarray: The pixel array of the rendered world.
    """
    PYGAME_WINDOW.fill(WHITE)

    cell_width = WINDOW_SIZE / world.world_width
    cell_height = WINDOW_SIZE / world.world_height

    def get_cell_rect(x: int, y: int):
        return (
            y * cell_width, x * cell_height,
            cell_width, cell_height
        )

    if isinstance(sim_selection_fn, RegionBasedSelectionFunction):
        for x in range(world.world_width):
            for y in range(world.world_height):
                if sim_selection_fn.in_survival_region(world, x, y):
                    rect = get_cell_rect(x, y)
                    pygame.draw.rect(PYGAME_WINDOW, LIGHT_GREEN, rect)

    # Draw the organisms as black cells
    for organism in world.organisms:
        x, y = world.get_organism_position(organism)
        if world.grid[y][x] is not None:
            rect = get_cell_rect(x, y)
            pygame.draw.rect(PYGAME_WINDOW, BLACK, rect)

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
