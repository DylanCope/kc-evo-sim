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
BLACK = (0, 0, 0)


class RenderVideoCallback:

    def __init__(self, frequency: int, videos_dir: str = 'video', fps: int = 5):
        self.frequency = frequency
        self.videos_dir = videos_dir
        Path(self.videos_dir).mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.frames = []

    def on_step_finish(self, iteration: int, world: World) -> dict:
        logs = {}

        if iteration % self.frequency == 0:
            frame = render_world(world)
            self.frames.append(frame)

        return logs

    def on_iteration_finish(self, iteration: int, iteration_logs: dict) -> None:
        logs = {}

        if iteration % self.frequency == 0:
            video_path = f'{self.videos_dir}/iteration_{iteration:06d}'
            logs['video_save_file'] = save_video(self.frames, video_path, fps=self.fps)
            self.frames = []

        return logs


def render_world(world: World) -> np.ndarray:
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

    # Draw the organisms as black cells
    for organism in world.organisms:
        x, y = world.get_organism_position(organism)
        if world.grid[y][x] is not None:
            rect = (
                y * cell_width, x * cell_height,
                cell_width, cell_height
            )
            pygame.draw.rect(PYGAME_WINDOW, BLACK, rect)

    # Update the display
    # pygame.display.flip()
    # img = pygame.surfarray.array3d(pygame)
    img = np.flipud(np.rot90(pygame.surfarray.array3d(pygame.display.get_surface())))

    return img


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
