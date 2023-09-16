import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
from typing import List
import imageio


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


def read_video_cv2(file, n_frames=1000):
    cap = cv2.VideoCapture(file)
    all = []
    i = 0
    while cap.isOpened() and i < n_frames:
        ret, frame = cap.read()
        arr = np.array(frame)
        all.append(arr)
        i += 1
    return np.array(all)


# videos_dir = 'experiments/runs/right_side_survive_v1/run_2023-09-15_19-39-11_8773485453367/videos'
videos_dir = 'experiments/runs/rs_v1_one_barrier/run_2023-09-16_01-11-35_8770174447698/videos'
video_files = sorted(Path(videos_dir).glob('*.mp4'))


def get_generation(video):
    generation = video.stem.split('_')[1]
    return int(re.sub(r'\D', '', generation))


generations = [get_generation(video) for video in video_files]
render_generations = [0, 20, 100, 300, 580]

assert all(generation in generations for generation in render_generations), \
    'Not all render generations are in the video files'

video_frames = [
    read_video_cv2(str(file), n_frames=100)
    for generation, file in zip(generations, video_files)
    if generation in render_generations
]
generations = [
    generation
    for generation in generations
    if generation in render_generations
]

plot_frames = []
for frame_group in zip(*video_frames):
    fig, axs = plt.subplots(1, len(frame_group), figsize=(5 * len(frame_group), 5))
    for i, (frame, generation) in enumerate(zip(frame_group, generations)):
        axs[i].imshow(frame)
        axs[i].axis('off')
        axs[i].set_title(f'Generation {generation}')
    fig.tight_layout(pad=1.5)
    fig.canvas.draw()
    plot_frames.append(np.array(fig.canvas.renderer._renderer))
    fig.clf()
    plt.close(fig)

save_video(plot_frames, 'assets/barrier_evolution', format='gif', fps=10)
